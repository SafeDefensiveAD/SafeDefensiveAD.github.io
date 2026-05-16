#!/usr/bin/env python3
"""Build static site into dist/ from repository root."""

import shutil
from pathlib import Path


def main() -> None:
  root = Path(__file__).resolve().parent.parent
  dist = root / "dist"

  index = root / "index.html"
  styles = root / "styles.css"
  assets = root / "assets"
  if not index.exists() or not styles.exists():
    raise FileNotFoundError("index.html or styles.css is missing")

  dist.mkdir(parents=True, exist_ok=True)

  shutil.copy2(index, dist / "index.html")
  shutil.copy2(styles, dist / "styles.css")
  cfp = root / "cfp.html"
  if cfp.exists():
    shutil.copy2(cfp, dist / "cfp.html")
  if assets.exists():
    shutil.copytree(assets, dist / "assets", dirs_exist_ok=True)
  nojekyll = root / ".nojekyll"
  if nojekyll.exists():
    shutil.copy2(nojekyll, dist / ".nojekyll")
  print(f"Build complete: {dist}")


if __name__ == "__main__":
  main()
