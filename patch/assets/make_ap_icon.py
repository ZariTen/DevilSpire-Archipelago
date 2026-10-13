"""Draws the Archipelago check icon (6 shaded orbs in the AP colours, pyramid like the AP logo).
Writes patch/assets/ap_icon.png (16x16 inventory icon) and ap_icon_D.png (64x64 dropped/3D sprite).
Run: python patch/assets/make_ap_icon.py   (needs Pillow; the PNGs are committed, so only needed to redraw)."""
import math
from pathlib import Path
from PIL import Image

COLS = [(238, 227, 145), (201, 118, 130), (117, 194, 117), (118, 126, 189), (202, 148, 194), (217, 160, 125)]
LIGHT = (-0.45, -0.55, 0.70)


def orb(img, cx, cy, r, col, outline):
    n = math.sqrt(sum(c * c for c in LIGHT))
    lx, ly, lz = (c / n for c in LIGHT)
    for y in range(img.height):
        for x in range(img.width):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            if outline and d2 > (1 - outline) ** 2:
                img.putpixel((x, y), tuple(int(c * 0.35) for c in col) + (255,))
                continue
            nz = math.sqrt(1 - d2)
            diff = max(0.0, dx * lx + dy * ly + nz * lz)
            spec = max(0.0, diff) ** 18
            k = 0.45 + 0.7 * diff
            img.putpixel((x, y), tuple(min(255, int(c * k + 255 * 0.8 * spec)) for c in col) + (255,))


def draw(size, r, outline):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    s = size / 64
    centres = [(32, 14), (21, 32), (43, 32), (10, 50), (32, 50), (54, 50)]
    for (cx, cy), col in zip(centres, COLS):
        orb(img, cx * s, cy * s, r, col, outline)
    return img


here = Path(__file__).resolve().parent
draw(64, 10.5, 0.14).save(here / "ap_icon_D.png")
draw(16, 3.0, 0.0).save(here / "ap_icon.png")
