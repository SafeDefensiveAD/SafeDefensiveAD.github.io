#!/usr/bin/env python3
"""Crop all portraits to uniform, face-centered squares for the poster.

No face detector is available, so face boxes are hand-tuned as fractions
(x0, y0, x1, y1) of each source image. Each crop is sized so the head fills
a consistent share of the square, then resized to a common resolution.
"""

import os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "poster" / "faces"
OUT.mkdir(parents=True, exist_ok=True)

TARGET_HEAD = 0.62   # head height as a share of the square crop
FACE_V = 0.45        # vertical placement of the face center (headroom)
SIZE = 600           # output resolution (square)

# name, source path (relative to repo root), head box (x0, y0, x1, y1)
PEOPLE = [
    ("marco-pavone",      "assets/images/people/marco-pavone.jpg",     (0.18, 0.04, 0.76, 0.82)),
    ("dragomir-anguelov", "assets/images/people/dragomir-anguelov.gif",(0.30, 0.23, 0.68, 0.70)),
    ("jun-gao",           "assets/images/people/jun-gao.jpg",          (0.29, 0.11, 0.71, 0.57)),
    ("chong-ruan",        "assets/images/people/chong-ruan.jpg",       (0.43, 0.11, 0.58, 0.37)),
    ("boyi-li",           "assets/images/people/boyi-li.jpg",          (0.29, 0.09, 0.67, 0.55)),
    ("qifeng-chen",       "assets/images/people/qifeng-chen.jpg",      (0.27, 0.15, 0.65, 0.73)),
    ("alexandre-alahi",   "assets/images/people/alexandre-alahi.jpg",  (0.27, 0.05, 0.73, 0.57)),
    ("bo-li",             "assets/images/people/bo-li.jpg",            (0.33, 0.05, 0.67, 0.63)),
    ("yiyi-liao",         "assets/images/people/yiyi-liao.jpeg",       (0.27, 0.09, 0.71, 0.65)),
    ("li-erran-li",       "assets/images/people/li-erran-li.jpg",      (0.27, 0.11, 0.75, 0.73)),
    ("tongyi-cao",        "dist/assets/images/people/tongyi-cao.jpeg", (0.27, 0.05, 0.61, 0.43)),
]


def main() -> None:
    for name, rel, (x0, y0, x1, y1) in PEOPLE:
        im = Image.open(ROOT / rel).convert("RGB")
        w, h = im.size
        head_h = (y1 - y0) * h
        cx = (x0 + x1) / 2 * w
        cy = (y0 + y1) / 2 * h
        s = min(head_h / TARGET_HEAD, w, h)
        left = max(0, min(cx - s / 2, w - s))
        top = max(0, min(cy - FACE_V * s, h - s))
        crop = im.crop((round(left), round(top), round(left + s), round(top + s)))
        crop = crop.resize((SIZE, SIZE), Image.LANCZOS)
        crop.save(OUT / f"{name}.jpg", quality=90)
        print(f"{name:18s} src={w}x{h}  crop={round(s)}px  head~{head_h/s:.2f}")


if __name__ == "__main__":
    main()
