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
  for page in ("cfp.html", "papers.html"):
    source = root / page
    if source.exists():
      shutil.copy2(source, dist / page)
  paper_pdfs = root / "papers" / "pdf"
  if paper_pdfs.exists():
    shutil.copytree(paper_pdfs, dist / "papers" / "pdf", dirs_exist_ok=True)
  if assets.exists():
    shutil.copytree(assets, dist / "assets", dirs_exist_ok=True)
  nojekyll = root / ".nojekyll"
  if nojekyll.exists():
    shutil.copy2(nojekyll, dist / ".nojekyll")
  print(f"Build complete: {dist}")


if __name__ == "__main__":
  main()
