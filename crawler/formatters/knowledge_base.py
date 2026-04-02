"""Knowledge base generator - combineert alle data tot finaal JSON."""

from __future__ import annotations

import json
import logging
import shutil

from config import KNOWLEDGE_BASE_COPY, KNOWLEDGE_BASE_FILE
from formatters.blog_formatter import BlogFormatter
from formatters.faq_formatter import FAQFormatter
from formatters.page_formatter import PageFormatter
from formatters.product_formatter import ProductFormatter

logger = logging.getLogger(__name__)


class KnowledgeBaseGenerator:
    """Genereert de finale kennisbank JSON uit alle gecrawlde data."""

    def __init__(self):
        self.product_fmt = ProductFormatter()
        self.faq_fmt = FAQFormatter()
        self.blog_fmt = BlogFormatter()
        self.page_fmt = PageFormatter()

    def generate(self, results: dict) -> list[dict]:
        """Genereer kennisbank entries uit alle resultaten.

        Args:
            results: Dict met keys products, faqs, blogs, pages, parts

        Returns:
            Lijst van trigger/content dicts
        """
        entries = []

        # Producten
        products = results.get("products", [])
        for product in products:
            try:
                entry = self.product_fmt.format(product)
                entries.append(entry)
            except Exception as e:
                logger.error(f"Product format fout: {e}")

        # Onderdelen (zelfde format als producten)
        parts = results.get("parts", [])
        for part in parts:
            try:
                entry = self.product_fmt.format(part)
                entries.append(entry)
            except Exception as e:
                logger.error(f"Onderdeel format fout: {e}")

        # FAQs
        faqs = results.get("faqs", [])
        seen_questions = set()
        for faq in faqs:
            try:
                q = faq.get("question", "")
                if q not in seen_questions:
                    entry = self.faq_fmt.format(faq)
                    entries.append(entry)
                    seen_questions.add(q)
            except Exception as e:
                logger.error(f"FAQ format fout: {e}")

        # Blogs
        blogs = results.get("blogs", [])
        for blog in blogs:
            try:
                entry = self.blog_fmt.format(blog)
                entries.append(entry)
            except Exception as e:
                logger.error(f"Blog format fout: {e}")

        # Pagina's
        pages = results.get("pages", [])
        for page in pages:
            try:
                entry = self.page_fmt.format(page)
                entries.append(entry)
            except Exception as e:
                logger.error(f"Pagina format fout: {e}")

        # Dedupliceer op basis van trigger
        entries = self._deduplicate(entries)

        logger.info(f"Kennisbank: {len(entries)} totale entries")
        return entries

    def save(self, entries: list[dict]):
        """Sla de kennisbank op als JSON."""
        # Hoofd output
        with open(KNOWLEDGE_BASE_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        logger.info(f"Opgeslagen: {KNOWLEDGE_BASE_FILE} ({len(entries)} entries)")

        # Kopie naar Downloads (overslaan in CI-modus)
        if KNOWLEDGE_BASE_COPY is not None:
            try:
                shutil.copy2(KNOWLEDGE_BASE_FILE, KNOWLEDGE_BASE_COPY)
                logger.info(f"Kopie: {KNOWLEDGE_BASE_COPY}")
            except Exception as e:
                logger.warning(f"Kon geen kopie maken naar Downloads: {e}")

    def _deduplicate(self, entries: list[dict]) -> list[dict]:
        """Verwijder duplicate entries op basis van trigger."""
        seen = set()
        unique = []
        for entry in entries:
            trigger = entry.get("trigger", "")
            if trigger not in seen:
                seen.add(trigger)
                unique.append(entry)
        return unique
