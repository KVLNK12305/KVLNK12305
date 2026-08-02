#!/usr/bin/env python3
"""Turn a photo into ascii.svg — a self-typing, monochrome ASCII portrait.

This is the generator that produced the portrait at the top of the README.
Run it once; it is not on a schedule, unlike scripts/generate_stats.py.

    pip install pillow numpy opencv-python-headless rembg onnxruntime
    python3 scripts/make_portrait.py photo.png --crop 400,110,910,790
    python3 scripts/embed_portrait_font.py      # inline the font, see below

The first run downloads a ~176 MB background-removal model, once.

Two things decide whether the output is any good, and neither is a parameter:

  * The photo. ASCII draws with shadow, not detail — about 13 brightness levels
    in total. You need side light (a window at ~45°, everything else off), a
    tight crop from chin to just above the hair, and real resolution. A 320px
    headshot fails: thin features like glasses frames are averaged away on
    downscale. Flat frontal light renders the face as a hole.
  * The darkening curve below. Without it the face comes out washed out and
    featureless — brows, glasses and lips all dissolve.

The grid bakes in an advance width of exactly 0.600 em (CHAR_W / FONT_SIZE), so
after generating, run scripts/embed_portrait_font.py to inline JetBrains Mono.
Otherwise a viewer whose default monospace is narrower — Consolas is ≈0.55 —
sees the portrait about 7% too narrow.

Motion is SMIL, because GitHub strips <script> from READMEs: each row is
revealed by a clipPath wipe with a cursor block riding its edge, staggered top
to bottom, frozen at the end so it prints once and stops.
"""
import argparse
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

RAMP = " .`:-=+*cs#%@"     # bright/sparse -> dark/dense; leading space = blank
COLS = 90                  # below ~88 the face muddies; far above it dominates
CLAHE_CLIP = 3.0           # higher amplifies skin texture into noise
GAMMA = 1.0                # ramp mapping exponent
CURVE = 1.7                # the darkening curve — the difference-maker
CROP_BOTTOM = 0.0          # fraction to trim off the bottom (torso, chair)
ROW_RATIO = 0.48           # monospace cells are about twice as tall as wide

FG_LIGHT = "#6e7681"       # readable on GitHub light — the portrait's grey
FG_DARK = "#c9d1d9"        # and its dark-mode step
CHAR_W = 7.74              # 0.600 em at FONT_SIZE — keep these in step
FONT_SIZE = 12.9
LINE_H = 15
ROW_DELAY = 0.09           # per-row stagger, seconds
FAMILY = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def prep(path, crop=None, use_rembg=True):
    """Cut out the background, even the local contrast, then darken."""
    src = Image.open(path).convert("RGBA")
    if crop:
        src = src.crop(crop)

    alpha = None
    if use_rembg:
        try:
            cut = remove(src)
            alpha_test = np.array(cut.split()[-1])
            if alpha_test.mean() > 1.0:
                alpha = alpha_test
            else:
                cut = src
        except Exception:
            cut = src
    else:
        cut = src

    if alpha is None:
        alpha = np.array(cut.split()[-1]) if cut.mode == "RGBA" else np.full(cut.size[::-1], 255, dtype=np.uint8)

    # Composite onto white so everything outside the subject maps to the blank end of the ramp.
    white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    gray = np.array(Image.alpha_composite(white, cut).convert("L"))

    # For photographic input, apply bilateral filter and CLAHE contrast enhancement
    if alpha is not None and alpha.mean() > 10.0:
        gray = cv2.bilateralFilter(gray, 11, 50, 50)
        gray = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=(8, 8)).apply(gray)
        gray = (255.0 * (gray / 255.0) ** CURVE).astype("uint8")
        gray[alpha < 20] = 255

    return Image.fromarray(gray)


def to_lines(img, cols=COLS, gamma=GAMMA):
    w, h = img.size
    if CROP_BOTTOM:
        img = img.crop((0, 0, w, int(h * (1 - CROP_BOTTOM))))
        w, h = img.size

    rows = int(cols * (h / w) * ROW_RATIO)
    
    # Calculate cell density via inverted downsampling for crisp line & contour art
    arr = np.array(img, dtype=float)
    darkness = np.maximum(0.0, 255.0 - arr)
    img_dark = Image.fromarray(darkness.astype(np.uint8))
    img_resized = img_dark.resize((cols, rows), Image.LANCZOS)
    px_dark = np.array(img_resized, dtype=float) / 255.0

    d_min, d_max = px_dark.min(), px_dark.max()
    if d_max > d_min:
        px_norm = (px_dark - d_min) / (d_max - d_min)
    else:
        px_norm = px_dark

    n = len(RAMP)
    out = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            val = px_norm[r, c]
            if val < 0.05:
                row_chars.append(' ')
            else:
                idx = int((val ** gamma) * (n - 1))
                row_chars.append(RAMP[min(n - 1, max(1, idx))])
        out.append("".join(row_chars).rstrip())

    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def build_svg(lines, cols=COLS):
    pad = 14
    width = int(cols * CHAR_W + pad * 2)
    height = len(lines) * LINE_H + pad * 2

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
         f'height="{height}" viewBox="0 0 {width} {height}" '
         f'font-family="{FAMILY}">',
         f'<style>.a{{fill:{FG_LIGHT}}}'
         f'@media(prefers-color-scheme:dark){{.a{{fill:{FG_DARK}}}}}</style>']

    for i, line in enumerate(lines):
        y = pad + i * LINE_H
        begin = f"{i * ROW_DELAY:.2f}s"
        end = f"{(i + 1) * ROW_DELAY:.2f}s"
        w = max(len(line), 1) * CHAR_W
        safe = (line.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))

        p.append(f'<clipPath id="c{i}"><rect x="{pad}" y="{y}" '
                 f'height="{LINE_H}" width="0">'
                 f'<animate attributeName="width" from="0" to="{w:.1f}" '
                 f'begin="{begin}" dur="{ROW_DELAY}s" fill="freeze"/>'
                 f'</rect></clipPath>')
        p.append(f'<g clip-path="url(#c{i})"><text xml:space="preserve" '
                 f'x="{pad}" y="{y + 11.2:.1f}" class="a" '
                 f'font-size="{FONT_SIZE}">{safe}</text></g>')
        # the cursor: a small block riding the wipe edge, gone once the row lands
        p.append(f'<rect y="{y + 1}" width="6" height="12" class="a" '
                 f'opacity="0">'
                 f'<animate attributeName="x" from="{pad}" to="{pad + w:.1f}" '
                 f'begin="{begin}" dur="{ROW_DELAY}s" fill="freeze"/>'
                 f'<set attributeName="opacity" to="0.8" begin="{begin}"/>'
                 f'<set attributeName="opacity" to="0" begin="{end}"/></rect>')

    p.append("</svg>")
    return "".join(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("photo")
    ap.add_argument("out", nargs="?", default="ascii.svg")
    ap.add_argument("--crop", help="left,top,right,bottom, applied first — crop "
                                   "tight to the head so the whole grid goes to "
                                   "the face")
    ap.add_argument("--cols", type=int, default=COLS)
    ap.add_argument("--no-rembg", action="store_true", help="skip automatic background removal")
    ap.add_argument("--preview", action="store_true",
                    help="print the ASCII to the terminal as well")
    args = ap.parse_args()

    crop = None
    if args.crop:
        parts = [int(v) for v in args.crop.split(",")]
        if len(parts) != 4:
            sys.exit("--crop needs four numbers: left,top,right,bottom")
        crop = tuple(parts)

    lines = to_lines(prep(args.photo, crop, use_rembg=not args.no_rembg), cols=args.cols)
    if args.preview:
        print("\n".join(lines))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(build_svg(lines, cols=args.cols))
    print(f"wrote {args.out} — {len(lines)} rows, {args.cols} columns")
    print("next: python3 scripts/embed_portrait_font.py")


if __name__ == "__main__":
    main()
