#!/usr/bin/env python3
"""Generate papers.html from the OpenReview status CSV and papers/papers_meta.json.

The CSV exported from OpenReview also carries reviewer scores and identities, so it
stays out of the published site: only title, abstract and decision are read. Per-paper
forum links are deliberately not published either, since the forums expose reviews.
"""

import csv
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "papers" / "SDAD 2026 Submission Status.csv"
META_PATH = ROOT / "papers" / "papers_meta.json"
PDF_DIR = ROOT / "papers" / "pdf"
OUT_PATH = ROOT / "papers.html"

BRACE_COMMANDS = ("textbf", "textit", "emph", "texttt", "textrm", "mathrm", "mathbf", "text")

SYMBOLS = {
  r"\rightarrow": "→",
  r"\leftarrow": "←",
  r"\Rightarrow": "⇒",
  r"\to": "→",
  r"\times": "×",
  r"\approx": "≈",
  r"\leq": "≤",
  r"\geq": "≥",
  r"\pm": "±",
  r"\cdot": "·",
  r"\ldots": "…",
  r"\%": "%",
  r"\&": "&",
  r"\_": "_",
  r"\#": "#",
  r"\{": "{",
  r"\}": "}",
}


def clean_latex(text: str) -> str:
  """Turn the LaTeX-flavoured abstracts stored in OpenReview into plain text."""
  out = text
  for _ in range(3):
    before = out
    for cmd in BRACE_COMMANDS:
      out = re.sub(r"\\" + cmd + r"\s*\{([^{}]*)\}", r"\1", out)
    if out == before:
      break
  out = re.sub(r"\$([^$]*)\$", r"\1", out)
  for token, replacement in SYMBOLS.items():
    out = out.replace(token, replacement)
  out = re.sub(r"\\[a-zA-Z]+\s?", "", out)
  return out


URL_RE = re.compile(r"https?://[^\s<>\"]+")


def linkify(escaped: str) -> str:
  def repl(match: re.Match) -> str:
    url = match.group(0)
    trailing = ""
    while url and url[-1] in ".,;:)":
      trailing = url[-1] + trailing
      url = url[:-1]
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>{trailing}'

  return URL_RE.sub(repl, escaped)


def to_paragraphs(text: str) -> list[str]:
  blocks = re.split(r"\n\s*\n", clean_latex(text).strip())
  paragraphs = []
  for block in blocks:
    joined = re.sub(r"\s+", " ", block).strip()
    if joined:
      paragraphs.append(linkify(html.escape(joined)))
  return paragraphs


def esc(text: str) -> str:
  return html.escape(text, quote=True)


def load_rows() -> list[dict]:
  meta = json.loads(META_PATH.read_text(encoding="utf-8"))["papers"]
  with CSV_PATH.open(encoding="utf-8-sig", newline="") as handle:
    records = list(csv.DictReader(handle))

  papers = []
  for record in records:
    decision = (record.get("decision") or "").strip()
    if not decision.lower().startswith("accept"):
      continue
    number = record["number"].strip()
    entry = meta.get(number, {})
    pdf_name = entry.get("pdf")
    if pdf_name and not (PDF_DIR / pdf_name).exists():
      sys.exit(f"Missing PDF for submission {number}: {pdf_name}")
    papers.append(
      {
        "number": number,
        "title": record["title"].strip(),
        "abstract": record["abstract"],
        "is_oral": "oral" in decision.lower(),
        "authors": entry.get("authors") or [],
        "affiliations": entry.get("affiliations") or [],
        "pdf": pdf_name,
      }
    )
  papers.sort(key=lambda item: int(item["number"]))
  return papers


def render_card(paper: dict) -> str:
  kind = "Spotlight" if paper["is_oral"] else "Poster"
  badge_class = "oral" if paper["is_oral"] else "poster"
  lines = [
    f'          <article class="paper-card" id="paper-{esc(paper["number"])}">',
    '            <div class="paper-top">',
    f'              <span class="paper-badge {badge_class}">{kind}</span>',
    f'              <span class="paper-id">Submission #{esc(paper["number"])}</span>',
    "            </div>",
    f'            <h3 class="paper-title">{esc(paper["title"])}</h3>',
  ]

  if paper["authors"]:
    lines.append(f'            <p class="paper-authors">{esc(", ".join(paper["authors"]))}</p>')
  if paper["affiliations"]:
    lines.append(
      f'            <p class="paper-affils">{esc(" · ".join(paper["affiliations"]))}</p>'
    )

  lines.append('            <details class="paper-abstract">')
  lines.append("              <summary>Abstract</summary>")
  lines.append('              <div class="paper-abstract-body">')
  for paragraph in to_paragraphs(paper["abstract"]):
    lines.append(f"                <p>{paragraph}</p>")
  lines.append("              </div>")
  lines.append("            </details>")

  if paper["pdf"]:
    href = "./papers/pdf/" + esc(paper["pdf"])
    lines.append('            <div class="paper-actions">')
    lines.append(f'              <a class="button small primary" href="{href}">PDF</a>')
    lines.append("            </div>")
  lines.append("          </article>")
  return "\n".join(lines)


def render_section(title: str, note: str, papers: list[dict]) -> str:
  cards = "\n".join(render_card(paper) for paper in papers)
  return f"""        <h2 class="paper-section-title">{esc(title)}</h2>
        <p class="section-note">{esc(note)}</p>
        <div class="paper-list">
{cards}
        </div>"""


def render_page(papers: list[dict]) -> str:
  orals = [paper for paper in papers if paper["is_oral"]]
  posters = [paper for paper in papers if not paper["is_oral"]]
  sections = "\n\n".join(
    [
      render_section(
        "Spotlight Talks",
        "Selected for a 10-minute talk in the morning spotlight session, and also presented as posters.",
        orals,
      ),
      render_section(
        "Poster Presentations",
        "Presented in poster sessions 1 and 2.",
        posters,
      ),
    ]
  )

  return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Accepted Papers · SDAD @ ECCV 2026</title>
    <meta
      name="description"
      content="Accepted papers at the Safe and Defensive Autonomous Driving (SDAD) workshop at ECCV 2026, with abstracts and camera-ready PDFs."
    />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <header class="site-header">
      <div class="container nav-wrap">
        <a class="brand" href="./index.html#top">SDAD 2026 @ ECCV</a>
        <nav aria-label="Primary">
          <ul class="nav-list">
            <li><a href="./index.html#about">About</a></li>
            <li><a href="./index.html#program">Program</a></li>
            <li><a href="./index.html#speakers">Speakers</a></li>
            <li><a href="./cfp.html">Call for Papers</a></li>
            <li><a href="./papers.html" aria-current="page">Papers</a></li>
            <li><a href="./index.html#sponsors">Sponsors</a></li>
            <li><a href="./index.html#organizers">Organizers</a></li>
          </ul>
        </nav>
      </div>
    </header>

    <main class="section section-light page-main">
      <div class="container">
        <h1 class="page-title">Accepted Papers</h1>
        <p class="section-note page-lead">
          Safe and Defensive Autonomous Driving (SDAD) · ECCV&nbsp;2026 · Malmö, Sweden ·
          Non-archival workshop track
        </p>

        <ul class="paper-stats">
          <li>
            <span class="paper-stat-value">{len(papers)}</span>
            <span class="paper-stat-label">Accepted papers</span>
          </li>
          <li>
            <span class="paper-stat-value">{len(orals)}</span>
            <span class="paper-stat-label">Spotlight talks</span>
          </li>
          <li>
            <span class="paper-stat-value">{len(posters)}</span>
            <span class="paper-stat-label">Poster presentations</span>
          </li>
        </ul>

        <p class="paper-intro">
          Every accepted paper is presented as a poster; three papers were additionally selected
          for spotlight talks. Because the workshop is non-archival, authors retain the right to
          submit their work elsewhere. Camera-ready PDFs are posted here as they are received.
        </p>

{sections}

        <p class="page-back">
          <a href="./index.html">&larr; Back to workshop home</a>
        </p>
      </div>
    </main>

    <footer>
      <div class="container footer-wrap">
        <p>Safe and Defensive Autonomous Driving (SDAD) · ECCV 2026</p>
        <p>Contact: <a href="mailto:cqf@ust.hk">cqf@ust.hk</a></p>
      </div>
    </footer>
  </body>
</html>
"""


def main() -> None:
  papers = load_rows()
  OUT_PATH.write_text(render_page(papers), encoding="utf-8")
  missing = [paper["number"] for paper in papers if not paper["pdf"]]
  print(f"Wrote {OUT_PATH.relative_to(ROOT)} with {len(papers)} accepted papers")
  if missing:
    print(f"No camera-ready PDF yet for submissions: {', '.join(missing)}")


if __name__ == "__main__":
  main()
