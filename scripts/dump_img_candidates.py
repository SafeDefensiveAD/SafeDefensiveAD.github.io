#!/usr/bin/env python3
"""Print image-like URLs extracted from arbitrary HTML."""

from __future__ import annotations

import re
import sys
import urllib.parse

import requests


IMG_RE = re.compile(
    r"https?://[^\s\"'<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"'<>]*)?",
    flags=re.IGNORECASE,
)


SRC_RE = re.compile(
    r"""(?:data-src|data-original|src|content)=["']([^"']+)["']""",
    flags=re.IGNORECASE,
)


def main() -> None:
  url = sys.argv[1]
  r = requests.get(
    url,
    timeout=30,
    headers={"User-Agent": "Mozilla/5.0 (compatible; SDAD-img-probe/1.0)"},
  )
  r.raise_for_status()
  html = r.text

  imgs = list(dict.fromkeys(IMG_RE.findall(html)))
  for u in imgs:
    if any(x in u.lower() for x in ["icon", "logo", "favicon"]):
      continue
    print(u)

  extras: set[str] = set()
  for m in SRC_RE.finditer(html):
    fragment = m.group(1).strip()
    if not fragment or fragment.startswith("data:"):
      continue
    if any(fragment.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
      extras.add(urllib.parse.urljoin(url, fragment))

  if extras:
    print("--- extras")
    for u in sorted(extras):
      if any(x in u.lower() for x in ["icon", "logo", "favicon"]):
        continue
      print(u)


if __name__ == "__main__":
  main()
