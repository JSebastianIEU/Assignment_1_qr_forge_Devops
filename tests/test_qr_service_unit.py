import base64
from pathlib import Path

from services.qr import QRConfig, encode_render, generate_qr_assets, render_qr


def _config() -> QRConfig:
    return QRConfig(
        url="https://example.com",
        foreground_color="#000000",
        background_color="#ffffff",
        size=128,
        padding=4,
        border_radius=0,
    )


def test_render_qr_outputs_svg_and_png() -> None:
    render = render_qr(_config())
    assert "<svg" in render.svg_text
    assert len(render.png_bytes) > 0


def test_encode_render_returns_base64() -> None:
    render = render_qr(_config())
    preview = encode_render(render)
    assert preview.svg_data.startswith("<svg")
    base64.b64decode(preview.png_data)


def test_generate_qr_assets_writes_files(tmp_path: Path) -> None:
    assets = generate_qr_assets(
        _config(),
        svg_dir=tmp_path / "svgs",
        png_dir=tmp_path / "pngs",
    )
    assert assets.svg_path.exists()
    assert assets.png_path.exists()
    assert assets.svg_path.suffix == ".svg"
    assert assets.png_path.suffix == ".png"
