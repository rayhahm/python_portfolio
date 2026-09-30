"""Loads the local ServiceTitan knowledge base for the chatbot.

The knowledge base is small (a handful of short markdown articles, a few
thousand tokens total), so the whole thing is simply passed to Claude as
context on every question rather than retrieved piecemeal. A keyword-based
retrieval step was tried first, but it silently returned nothing for
Korean questions against the English-language articles (no literal term
overlap) — passing everything sidesteps that and is simpler besides.

If the knowledge base grows large enough that it no longer fits comfortably
in context (dozens of long articles), switch to real semantic retrieval
(e.g. Voyage AI embeddings) instead of re-adding keyword search.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Article:
    title: str
    text: str


def load_knowledge_base(knowledge_dir: Path) -> list[Article]:
    articles: list[Article] = []
    for path in sorted(knowledge_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        title_match = re.match(r"^#\s+(.+)", content)
        title = title_match.group(1).strip() if title_match else path.stem
        articles.append(Article(title=title, text=content))
    return articles


def build_context(articles: list[Article]) -> str:
    if not articles:
        return "(지식 베이스가 비어 있습니다.)"
    return "\n\n---\n\n".join(a.text for a in articles)
