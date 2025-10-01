from __future__ import annotations

import base64
import io
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import qrcode
from PIL import Image, ImageDraw


@dataclass
class QRConfig:
    url: str
    foreground_color: str
    background_color: str
    size: int
    padding: int
    border_radius: int


@dataclass
class QRPreview:
    svg_data: str
    png_data: str


@dataclass
class QRRender:
    svg_text: str
    png_bytes: bytes


@dataclass
class QRAssets:
    svg_path: Path
    png_path: Path


HEX_ALPHA = 255
TRANSPARENT = (0, 0, 0, 0)


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _hex_to_rgba(color: str) -> Tuple[int, int, int, int]:
    if color.lower() == 'transparent':
        return TRANSPARENT
    color = color.lstrip('#')
    if len(color) != 6:
        raise ValueError('Expected 6 character hex color or "transparent"')
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return r, g, b, HEX_ALPHA


def _create_matrix(config: QRConfig) -> List[List[bool]]:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        border=0,
    )
    qr.add_data(config.url)
    qr.make(fit=True)
    return qr.get_matrix()


def _render_svg(config: QRConfig, matrix: List[List[bool]]) -> str:
    modules = len(matrix)
    module_size = config.size / modules
    total_size = config.size + config.padding * 2
    bg = config.background_color
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_size}" height="{total_size}" viewBox="0 0 {total_size} {total_size}">'
    ]
    if bg.lower() != 'transparent':
        svg_parts.append(
            f'<rect width="{total_size}" height="{total_size}" fill="{bg}" rx="{config.border_radius}" ry="{config.border_radius}" />'
        )
    pad = config.padding
    fg = config.foreground_color
    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            if not cell:
                continue
            x0 = pad + x * module_size
            y0 = pad + y * module_size
            svg_parts.append(
                f'<rect x="{x0:.3f}" y="{y0:.3f}" width="{module_size:.3f}" height="{module_size:.3f}" fill="{fg}" />'
            )
    svg_parts.append('</svg>')
    return ''.join(svg_parts)


def _render_png(config: QRConfig, matrix: List[List[bool]]) -> bytes:
    modules = len(matrix)
    module_size = config.size / modules
    total_size = config.size + config.padding * 2

    background = Image.new('RGBA', (total_size, total_size), _hex_to_rgba(config.background_color))
    draw = ImageDraw.Draw(background)
    fg_rgba = _hex_to_rgba(config.foreground_color)

    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            if not cell:
                continue
            x0 = config.padding + x * module_size
            y0 = config.padding + y * module_size
            x1 = x0 + module_size
            y1 = y0 + module_size
            draw.rectangle([x0, y0, x1, y1], fill=fg_rgba)

    if config.border_radius > 0:
        radius = min(config.border_radius, total_size // 2)
        mask = Image.new('L', (total_size, total_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle((0, 0, total_size, total_size), radius=radius, fill=255)
        rounded = Image.new('RGBA', (total_size, total_size))
        rounded.paste(background, (0, 0), mask=mask)
        background = rounded

    with io.BytesIO() as buf:
        background.save(buf, format='PNG')
        return buf.getvalue()


def render_qr(config: QRConfig) -> QRRender:
    matrix = _create_matrix(config)
    svg_text = _render_svg(config, matrix)
    png_bytes = _render_png(config, matrix)
    return QRRender(svg_text=svg_text, png_bytes=png_bytes)


def generate_qr_assets(
    config: QRConfig,
    *,
    svg_dir: Path,
    png_dir: Path,
) -> QRAssets:
    svg_dir = _ensure_dir(svg_dir)
    png_dir = _ensure_dir(png_dir)
    render = render_qr(config)

    svg_filename = f"{uuid.uuid4()}.svg"
    svg_path = svg_dir / svg_filename
    svg_path.write_text(render.svg_text, encoding='utf-8')

    png_filename = f"{svg_filename[:-4]}.png"
    png_path = png_dir / png_filename
    png_path.write_bytes(render.png_bytes)

    return QRAssets(svg_path=svg_path, png_path=png_path)


def encode_render(render: QRRender) -> QRPreview:
    return QRPreview(
        svg_data=render.svg_text,
        png_data=base64.b64encode(render.png_bytes).decode('ascii'),
    )
