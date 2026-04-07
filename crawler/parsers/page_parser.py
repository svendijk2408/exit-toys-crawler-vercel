"""Page parser - extractie van content uit info- en categoriepagina's."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PageParser:
    """Parst info- en categoriepagina's."""

    def __init__(self, skip_words: tuple[str, ...] = ("zoeken", "search", "winkelwagen")):
        self.skip_words = skip_words

    def parse(self, url: str, html: str) -> dict | None:
        """Parse een pagina en retourneer gestructureerde data."""
        soup = BeautifulSoup(html, "lxml")

        # Titel
        h1 = soup.select_one("h1")
        if not h1:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True).replace(" | EXIT Toys", "")
            else:
                return None
        else:
            title = h1.get_text(strip=True)

        # Skip lege titels of zoekpagina's
        if not title or title.lower() in self.skip_words:
            return None

        # Content extractie
        content = self._extract_content(soup)
        if not content or len(content) < 50:
            return None

        # Meta description als extra context
        meta_desc = ""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            meta_desc = meta.get("content", "")

        return {
            "url": url,
            "type": "page",
            "title": title,
            "meta_description": meta_desc,
            "content": content,
        }

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract de hoofdcontent van een pagina."""
        # Zoek het hoofd-content blok
        main = soup.select_one("main#div_content, main.container, #div_content")
        if not main:
            main = soup.select_one("main")
        if not main:
            return ""

        # Verwijder navigatie, footer, scripts, etc.
        for selector in ["nav", "footer", "script", "style", "header",
                         ".submenu", ".breadcrumbs", "#div_breadcrumbs",
                         ".cookie", ".newsletter"]:
            for elem in main.select(selector):
                elem.decompose()

        parts = []
        for elem in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th"]):
            text = elem.get_text(strip=True)
            if text and len(text) > 2:
                # Voeg headers toe met prefix
                if elem.name in ("h1", "h2", "h3", "h4"):
                    parts.append(f"\n{text}")
                else:
                    parts.append(text)

        # Dedupliceer opeenvolgende identieke regels
        cleaned = []
        for part in parts:
            if not cleaned or part != cleaned[-1]:
                cleaned.append(part)

        return "\n".join(cleaned).strip()
