#!/usr/bin/env python3
"""Download public profile photos referenced on the workshop site."""

from __future__ import annotations

from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent / "assets" / "images" / "people"

# (filename, url, Notes for maintainers.)
ASSETS: list[tuple[str, str, str]] = [
  (
    "marco-pavone.jpg",
    "https://profiles.stanford.edu/proxy/api/cap/profiles/46879/resources/profilephoto/350x350.1696806908518.jpg",
    "Marco Pavone — Stanford Profiles.",
  ),
  ("dragomir-anguelov.gif", "https://ai.stanford.edu/~drago/Drago3.gif", "Dragomir Anguelov — Stanford legacy homepage."),
  (
    "jun-gao.jpg",
    "http://www.cs.toronto.edu/~jungao/images/whole.jpg",
    "Jun Gao — personal site (prior affiliation).",
  ),
  ("chong-ruan.jpg", "https://unavatar.io/github/soloice", "Chong Ruan — resolves GitHub @soloice profile image."),
  (
    "boyi-li.jpg",
    "https://research.nvidia.com/sites/default/files/person/Boyi_Li.jpg",
    "Boyi Li — NVIDIA Research person page.",
  ),
  (
    "dan-levi.jpg",
    (
      "https://lh3.googleusercontent.com/sitesv/AA5AbUDXbIvhw3S4WJJAFwzPcnpeFZ4FAGXpuh99PbIZypJ"
      "QchbN9pEu1rW4ItV_2g1tqHjF-H3q3eRDxlirzr4V3uuLQhiAE6HDQXsahDcaSid3e9tKiLy6sdWbRBYLghzYf6"
      "VyvAmJxbMetuWK3JPrJNqI5BOkWKkurteL4JIee8tam6tAE1Yi4aZjSN8xTaY4KVKikV46MIGm=w1280"
    ),
    # Google Sites CDN URL can change — re-run dump_img_candidates.py on the homepage when needed.
    "Dan Levi — Google Sites homepage (https://sites.google.com/view/danlevi/home).",
  ),
  ("qifeng-chen.jpg", "https://cqf.io/fig/qifeng-chen.jpg", "Qifeng Chen — https://cqf.io/."),
  (
    "alexandre-alahi.jpg",
    (
      "https://people.epfl.ch/rails/active_storage/representations/proxy/"
      "eyJfcmFpbHMiOnsiZGF0YSI6MTI5MjgsImV4cCI6IjIwMjYtMDUtMTdUMDc6MTg6NDEuNjgwWiIsInB1ciI6ImJsb2JfaWQifX0=--"
      "b31f0db02ab4798f8cd37b4467f126b27323a341/"
      "eyJfcmFpbHMiOnsiZGF0YSI6eyJmb3JtYXQiOiJqcGciLCJyZXNpemVfdG9fbGltaXQiOls2MDAsNjAwXX0sInB1ciI6InZhcmlhdGlvbiJ9fQ==--"
      "f0434730233511d2b7f78b3f724fd44f404193e0/129343.jpg?lang=fr"
    ),
    # The above signed URL can expire — re-run dump_img_candidates.py on Alexandre's EPFL people page when needed.
    "Alexandre Alahi — EPFL people.epfl.ch (ActiveStorage CDN).",
  ),
  ("bo-li.jpg", "http://boli.cs.illinois.edu/files/bo_li_headshot.jpg", "Bo Li — research group web site."),
  (
    "yiyi-liao.jpeg",
    "https://person.zju.edu.cn/person//attachments/2022-03/0327035417-2069908222.jpeg",
    "Yiyi Liao — ZJU directory.",
  ),
  ("li-erran-li.png", "https://www.cs.columbia.edu/~lierranli/lierranli.png", "Li Erran Li — Columbia homepage."),
  (
    "tongyi-cao.jpg",
    "https://cms-image.pandaily.com/20260428225041_9_1958_0e1504bac3.jpg",
    "Tongyi Cao — Pandaily automotive press photo (Apr 29, 2026). Replace when an official portrait is available.",
  ),
]


headers = {"User-Agent": "Mozilla/5.0 SDAD-web-asset-bot/1.0 (+mailto:cqf@ust.hk)"}


def main() -> None:
  ROOT.mkdir(parents=True, exist_ok=True)
  session = requests.Session()
  session.headers.update(headers)

  for fname, url, note in ASSETS:
    target = ROOT / fname
    if target.exists() and target.stat().st_size > 5000:
      print(f"[skip exists] {fname}")
      continue
    print(f"[fetch] {fname} ({note})\n           {url[:90]}...")
    response = session.get(url, timeout=45)
    response.raise_for_status()
    content = response.content
    if len(content) < 256:
      raise RuntimeError(f"{fname}: response too small ({len(content)} bytes)")
    target.write_bytes(content)


if __name__ == "__main__":
  main()
