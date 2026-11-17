#!/usr/bin/env python3
"""
Turn a photo into a dreamy dotted header in pastel pink + baby blue.

    python3 tools/pastel_header.py PHOTO
    python3 tools/pastel_header.py PHOTO --mode pink      (pink only)
    python3 tools/pastel_header.py PHOTO --mode blue      (blue only)
    python3 tools/pastel_header.py --demo                 (no photo? makes dreamy clouds)

Needs Pillow + numpy:  pip install pillow numpy
Writes assets/header-dark.png and assets/header-light.png.
"""

import argparse
import os

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Pastel inks. Dark theme uses soft pastels, light theme uses slightly
# deeper versions so the dots still show up on a white page.
PINK_DARK, BLUE_DARK = (247, 168, 200), (168, 216, 247)   # #F7A8C8  #A8D8F7
PINK_LIGHT, BLUE_LIGHT = (232, 138, 180), (127, 184, 230) # #E88AB4  #7FB8E6
DARK_BG, LIGHT_BG = (13, 17, 23), (255, 255, 255)         # GitHub's dark canvas / white


def ink_layer(size, left, right, mode):
    """A colour field for the dots: a pink→blue sweep, or one solid colour."""
    w, h = size
    if mode == "pink":
        return Image.new("RGB", size, left)
    if mode == "blue":
        return Image.new("RGB", size, right)
    # Diagonal sweep with a gentle ease so the middle turns lilac, not grey.
    x = np.linspace(0, 1, w)[None, :]
    y = np.linspace(0, 1, h)[:, None]
    t = np.clip(0.8 * x + 0.2 * y, 0, 1)
    t = t * t * (3 - 2 * t)
    a, b = np.array(left, float), np.array(right, float)
    rgb = a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]
    return Image.fromarray(rgb.astype(np.uint8), "RGB")


def dither(gray, ink, bg):
    """1-bit Floyd–Steinberg dots, painted with the ink layer over the background."""
    bw = gray.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    return Image.composite(ink, Image.new("RGB", gray.size, bg), bw)


def demo_clouds(w=1800, h=1200, seed=7):
    """A soft cloudscape from layered noise, for people without a photo yet."""
    rng = np.random.default_rng(seed)
    img = np.zeros((h, w))
    for scale, weight in ((8, 1.0), (16, 0.5), (32, 0.25), (64, 0.12)):
        n = Image.fromarray((rng.random((scale, int(scale * w / h))) * 255).astype(np.uint8))
        img += weight * np.asarray(n.resize((w, h), Image.BICUBIC), float)
    img = (img - img.min()) / (img.max() - img.min())
    yy = np.linspace(0, 1, h)[:, None]
    img = np.clip(img * 1.3 - 0.35 + 0.25 * (1 - yy), 0, 1)   # brighter sky up top
    out = Image.fromarray((img * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
    return out.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("photo", nargs="?")
    ap.add_argument("--demo", action="store_true", help="use generated clouds instead of a photo")
    ap.add_argument("--mode", choices=["both", "pink", "blue"], default="both")
    ap.add_argument("--top", type=float, default=0.35, help="where the crop starts (0 = top, 1 = bottom)")
    ap.add_argument("--ratio", type=float, default=3.0, help="banner width / height")
    ap.add_argument("--width", type=int, default=600, help="dots across, before scaling up")
    ap.add_argument("--dot", type=int, default=2, help="pixels per dot")
    ap.add_argument("--contrast", type=float, default=1.15)
    ap.add_argument("--gamma", type=float, default=1.6, help="higher = fewer, sparklier dots")
    ap.add_argument("--out", default="assets")
    args = ap.parse_args()

    if args.demo:
        im = demo_clouds()
    elif args.photo:
        im = Image.open(args.photo).convert("RGB")
    else:
        ap.error("give a PHOTO, or use --demo")

    w, h = im.size
    bh = min(h, int(w / args.ratio))
    y = min(int(args.top * h), h - bh)
    band = im.crop((0, y, w, y + bh))
    grid = band.resize((args.width, int(args.width / args.ratio)), Image.LANCZOS)
    gray = ImageOps.autocontrast(grid.convert("L"), cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(args.contrast)
    dark_src = gray.point(lambda v: round(255 * (v / 255) ** args.gamma))
    light_src = gray.point(lambda v: round(255 * (v / 255) ** (1 / args.gamma)))

    os.makedirs(args.out, exist_ok=True)
    size = (grid.width * args.dot, grid.height * args.dot)

    dark = dither(dark_src, ink_layer(grid.size, PINK_DARK, BLUE_DARK, args.mode), DARK_BG)
    light = dither(ImageOps.invert(light_src), ink_layer(grid.size, PINK_LIGHT, BLUE_LIGHT, args.mode), LIGHT_BG)
    for img, name in ((dark, "header-dark.png"), (light, "header-light.png")):
        p = os.path.join(args.out, name)
        img.resize(size, Image.NEAREST).save(p, optimize=True)
        print("%s  %dx%d  %.0f KB" % (p, size[0], size[1], os.path.getsize(p) / 1e3))


if __name__ == "__main__":
    main()
