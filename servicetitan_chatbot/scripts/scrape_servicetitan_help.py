"""Fetch ServiceTitan Help Center articles into knowledge/ as markdown.

This sandbox's network policy blocks help.servicetitan.com, so this script
can't be run here. Run it on your own laptop/PC (pip install -r
scripts/requirements.txt first), pointing at the article URLs your team
actually needs, then commit the resulting knowledge/*.md files.

Usage:
    python scripts/scrape_servicetitan_help.py \
        https://help.servicetitan.com/docs/getting-started-with-servicetitan \
        https://help.servicetitan.com/docs/... \
        -o ../knowledge

Some Help Center articles require being logged into a ServiceTitan account
to view. For those, save the page as HTML from your logged-in browser
(File > Save Page As) and pass the local .html path instead of a URL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CenturyMechanicalBot/1.0)"}


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_-]+", "-", text) or "article"


def fetch_html(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        resp = requests.get(source, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text
    return Path(source).read_text(encoding="utf-8")


def extract_article(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled Article"

    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(attrs={"class": re.compile(r"(content|article)", re.I)})
        or soup.body
        or soup
    )

    converter = html2text.HTML2Text()
    converter.ignore_images = True
    converter.ignore_emphasis = False
    converter.body_width = 0
    body_md = converter.handle(str(main)).strip()

    return title, body_md


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", help="Article URLs or local .html files")
    parser.add_argument(
        "-o", "--out-dir", default="knowledge", help="Output directory for .md files"
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for source in args.sources:
        try:
            html = fetch_html(source)
            title, body_md = extract_article(html)
        except Exception as exc:  # noqa: BLE001
            print(f"[skip] {source}: {exc}", file=sys.stderr)
            continue

        origin = urlparse(source).netloc or "local"
        filename = f"{slugify(title)}.md"
        out_path = out_dir / filename
        out_path.write_text(
            f"# {title}\n\n"
            f"<!-- source: {source} ({origin}) -->\n\n"
            f"## {title}\n{body_md}\n",
            encoding="utf-8",
        )
        print(f"[ok] {source} -> {out_path}")


if __name__ == "__main__":
    main()
