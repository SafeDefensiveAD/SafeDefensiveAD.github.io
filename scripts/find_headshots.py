#!/usr/bin/env python3
"""Fetch a page HTML and print likely headshot URLs (jpg/png/webp)."""
from __future__ import annotations

import re
import sys
import urllib.parse

import requests


SKIP = ("icon", "logo", "favicon", "sprite", "social", "facebook", "twitter")


def collect(url: str) -> list[str]:
  r = requests.get(
    url,
    timeout=30,
    headers={"User-Agent": "Mozilla/5.0 (compatible; SDAD-site-bot/1.0)"},
  )
  r.raise_for_status()
  html = r.text
  found: set[str] = set()
  for m in re.finditer(r'src="([^"]+)"', html):
    u = m.group(1)
    if u.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
      found.add(urllib.parse.urljoin(url, u))
  for m in re.finditer(r"url\(([^)]+)\)", html):
    u = m.group(1).strip().strip('"').strip("'")
    if u.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
      found.add(urllib.parse.urljoin(url, u))
  out = []
  for u in sorted(found):
    low = u.lower()
    if any(s in low for s in SKIP):
      continue
    out.append(u)
  return out


def main() -> None:
  for arg in sys.argv[1:]:
    print(f"--- {arg}")
    try:
      for u in collect(arg):
        print(u)
    except Exception as exc:
      print("ERROR", exc)


if __name__ == "__main__":
  main()
