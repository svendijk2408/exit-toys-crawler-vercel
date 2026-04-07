"""Blog parser - extractie van blog content."""

from __future__ import annotations

import logging
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BlogParser:
    """Parst blogpagina's en extraheert de content."""

    def __init__(self, written_by_prefix: str = "Geschreven door:"):
        self.written_by_prefix = written_by_prefix

    def parse(self, url: str, html: str) -> dict | None:
        """Parse een blogpost pagina en retourneer gestructureerde data."""
        soup = BeautifulSoup(html, "lxml")

        # Check of dit een blogpost is
        main = soup.select_one("main.container.blog")
        if not main:
            return None

        editor = main.select_one(".editor")
        if not editor:
            return None

        # Titel
        h1 = editor.select_one("h1")
        if not h1:
            return None
        title = h1.get_text(strip=True)

        # Skip als het de index pagina is
        if title.lower() in ("blogs", "blog"):
            return None

        # Datum
        date_elem = editor.select_one(".date .dt")
        date = date_elem.get_text(strip=True) if date_elem else ""

        # Auteur
        author = ""
        person_elem = editor.select_one(".written .person")
        if person_elem:
            author_text = person_elem.get_text(strip=True)
            # Verwijder "Geschreven door:" / "Geschrieben von:" prefix
            prefix_pattern = re.escape(self.written_by_prefix)
            author = re.sub(rf"^{prefix_pattern}\s*", "", author_text).strip()

        # Content
        content = self._extract_content(editor)

        if not content:
            return None

        return {
            "url": url,
            "type": "blog",
            "title": title,
            "author": author,
            "date": date,
            "content": content,
        }

    def parse_index(self, html: str) -> list[str]:
        """Parse de blog index pagina en retourneer blog post URLs."""
        soup = BeautifulSoup(html, "lxml")
        urls = []

        # Alle blog item links (big, regular, small, hidden)
        for a in soup.select("main.blog .items .item figure.item a"):
            href = a.get("href", "")
            if href and "/blog/" in href:
                urls.append(href)

        return list(set(urls))

    def _extract_content(self, editor) -> str:
        """Extract de blog content als schone tekst."""
        # Verwijder niet-content elementen
        for selector in [".date", ".share", ".clear", ".backtooverview",
                         ".written", ".related", "button", ".readmore"]:
            for elem in editor.select(selector):
                elem.decompose()

        # Verzamel content elementen
        parts = []
        h1_found = False

        for elem in editor.children:
            if not hasattr(elem, "name"):
                continue

            # Begin na de H1
            if elem.name == "h1":
                h1_found = True
                continue

            if not h1_found:
                continue

            if elem.name in ("h2", "h3", "h4"):
                text = elem.get_text(strip=True)
                if text:
                    parts.append(f"\n{text}")
            elif elem.name == "p":
                text = elem.get_text(strip=True)
                if text:
                    parts.append(text)
            elif elem.name == "ul":
                for li in elem.find_all("li"):
                    text = li.get_text(strip=True)
                    if text:
                        parts.append(f"- {text}")
            elif elem.name == "ol":
                for i, li in enumerate(elem.find_all("li"), 1):
                    text = li.get_text(strip=True)
                    if text:
                        parts.append(f"{i}. {text}")
            elif elem.name == "table":
                parts.append(self._parse_table(elem))
            elif elem.name == "figure":
                # Skip afbeeldingen
                continue

        return "\n".join(parts).strip()

    def _parse_table(self, table) -> str:
        """Converteer een HTML tabel naar tekst."""
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
            rows.append(" | ".join(cells))
        return "\n".join(rows)
