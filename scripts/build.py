#!/usr/bin/env python3
"""Build static site into dist/ from repository root."""

import shutil
from pathlib import Path


def main() -> None:
  root = Path(__file__).resolve().parent.parent
  dist = root / "dist"

  index = root / "index.html"
  styles = root / "styles.css"
  if not index.exists() or not styles.exists():
    raise FileNotFoundError("index.html or styles.css is missing")

  dist.mkdir(parents=True, exist_ok=True)
  for path in dist.iterdir():
    if path.is_dir():
      shutil.rmtree(path)
    else:
      path.unlink()

  shutil.copy2(index, dist / "index.html")
  shutil.copy2(styles, dist / "styles.css")
  print(f"Build complete: {dist}")


if __name__ == "__main__":
  main()
