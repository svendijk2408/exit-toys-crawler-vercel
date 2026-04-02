"""FAQ parser - extractie van Q&A paren uit FAQ pagina's."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class FAQParser:
    """Parst FAQ pagina's en extraheert vraag-antwoord paren."""

    def parse(self, url: str, html: str) -> list[dict]:
        """Parse een FAQ pagina en retourneer lijst van Q&A dicts."""
        soup = BeautifulSoup(html, "lxml")

        # Check of dit een FAQ pagina is
        main = soup.select_one("main.container.faqs")
        if not main:
            return []

        faqs = []
        faqsitem = soup.select_one("div.faqsitem")
        if not faqsitem:
            return []

        # Hoofdcategorie uit H1
        h1 = faqsitem.select_one("h1")
        main_category = h1.get_text(strip=True) if h1 else ""

        # Parse Q&A paren per sub-topic
        for item_div in faqsitem.select("div.box > div.item"):
            # Sub-topic titel
            title_elem = item_div.select_one("div.title")
            sub_topic = title_elem.get_text(strip=True) if title_elem else ""

            # Itereer door question/answer paren
            current_question = None
            for elem in item_div.children:
                if not hasattr(elem, "get"):
                    continue

                classes = elem.get("class", [])
                if "question" in classes:
                    current_question = elem.get_text(strip=True)
                elif "answer" in classes and current_question:
                    answer_text = self._extract_answer_text(elem)
                    if answer_text:
                        faqs.append({
                            "url": url,
                            "main_category": main_category,
                            "sub_topic": sub_topic,
                            "question": current_question,
                            "answer": answer_text,
                        })
                    current_question = None

        logger.debug(f"FAQ pagina {url}: {len(faqs)} Q&A paren gevonden")
        return faqs

    def parse_index(self, html: str) -> list[str]:
        """Parse de FAQ index pagina en retourneer categorie-URLs."""
        soup = BeautifulSoup(html, "lxml")
        urls = []

        # Links uit de index pagina
        for a in soup.select("div.items div.item div.title a"):
            href = a.get("href", "")
            if href:
                urls.append(href)

        # Ook links uit de sidebar (als we op een categoriepagina zijn)
        for a in soup.select("div.submenu ul li a"):
            href = a.get("href", "")
            if href and href not in urls:
                urls.append(href)

        return urls

    def _extract_answer_text(self, elem) -> str:
        """Extract schone tekst uit een antwoord-element."""
        # Behoud structuur maar converteer naar platte tekst
        parts = []
        for child in elem.descendants:
            if child.name in ("p", "li"):
                text = child.get_text(strip=True)
                if text:
                    parts.append(text)
            elif child.name == "br":
                parts.append("")

        if parts:
            return "\n".join(parts)

        # Fallback naar platte tekst
        return elem.get_text(strip=True)
