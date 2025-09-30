from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import qrcode
import qrcode.image.svg as svg
from PIL import Image, ImageDraw, ImageFont


@dataclass
class QRConfig:
    url: str
    foreground_color: str
    background_color: str
    size: int
    padding: int
    border_radius: int
    overlay_text: Optional[str]


@dataclass
class QRAssets:
    svg_path: Path
    png_path: Path


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _compute_box_size(config: QRConfig) -> int:
    # qrcode box size correlates with output size; clamp to avoid tiny images
    return max(2, min(20, config.size // 32))


def _compute_border(config: QRConfig) -> int:
    # QRCode expects border in modules; map padding pixels to modules approximately
    return max(1, min(10, config.padding // 8 + 1))


def _apply_overlay(image: Image.Image, config: QRConfig) -> None:
    if not config.overlay_text:
        return
    text = config.overlay_text.strip()
    if not text:
        return
    draw = ImageDraw.Draw(image)
    font_size = max(12, config.size // 6)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (image.width - text_width) / 2
    y = (image.height - text_height) / 2
    draw.text((x, y), text, font=font, fill=config.background_color if config.foreground_color.lower() == "#ffffff" else config.foreground_color)


def _apply_border_radius(image: Image.Image, radius: int) -> Image.Image:
    if radius <= 0:
        return image
    radius = min(radius, min(image.size) // 2)
    # create rounded mask
    mask = Image.new("L", image.size, 0)
    corner = Image.new("L", (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(corner)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    mask.paste(corner.crop((0, 0, radius, radius)), (0, 0))
    mask.paste(corner.crop((radius, 0, radius * 2, radius)), (image.width - radius, 0))
    mask.paste(corner.crop((0, radius, radius, radius * 2)), (0, image.height - radius))
    mask.paste(
        corner.crop((radius, radius, radius * 2, radius * 2)),
        (image.width - radius, image.height - radius),
    )
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rectangle((radius, 0, image.width - radius, image.height), fill=255)
    draw_mask.rectangle((0, radius, image.width, image.height - radius), fill=255)
    rounded = Image.new("RGBA", image.size)
    rounded.paste(image, (0, 0), mask=mask)
    return rounded


def generate_qr_assets(
    config: QRConfig,
    *,
    svg_dir: Path,
    png_dir: Path,
) -> QRAssets:
    svg_dir = _ensure_dir(svg_dir)
    png_dir = _ensure_dir(png_dir)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=_compute_box_size(config),
        border=_compute_border(config),
    )
    qr.add_data(config.url)
    qr.make(fit=True)

    svg_filename = f"{uuid.uuid4()}.svg"
    svg_path = svg_dir / svg_filename
    svg_image = qr.make_image(
        fill_color=config.foreground_color,
        back_color=config.background_color,
        image_factory=svg.SvgImage,
    )
    svg_image.save(str(svg_path))

    png_filename = f"{svg_filename[:-4]}.png"
    png_path = png_dir / png_filename
    pil_image = qr.make_image(fill_color=config.foreground_color, back_color=config.background_color).convert("RGBA")
    if config.size and config.size != pil_image.width:
        pil_image = pil_image.resize((config.size, config.size), Image.LANCZOS)
    _apply_overlay(pil_image, config)
    pil_image = _apply_border_radius(pil_image, config.border_radius)
    pil_image.save(png_path, format="PNG")

    return QRAssets(svg_path=svg_path, png_path=png_path)
