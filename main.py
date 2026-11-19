#!/usr/bin/env python3
"""Entry for make.fun news-image-20261119: sum up the world news of
Thursday 19 November 2026 in one 1024x1024 image.

The image is rendered at build time by render.py (Pillow + DejaVu Sans)
and shipped as entry.png; this program just copies it to the output
directory. Standard library only, no network. Deterministic: every run
writes identical bytes.
Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    if not os.path.isfile(src):
        raise SystemExit("entry.png missing from repository")
    if os.path.getsize(src) > 1048576:
        raise SystemExit("entry.png exceeds the 1 MiB limit")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
