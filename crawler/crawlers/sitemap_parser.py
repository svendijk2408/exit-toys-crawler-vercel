"""Sitemap parser - haalt alle URLs op uit de EXIT Toys sitemaps."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from config import BASE_URL
from crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)

# Sitemaps zijn al per type gesorteerd
SITEMAP_MAP = {
    "products": f"{BASE_URL}/sitemap-products.xml",
    "pages": f"{BASE_URL}/sitemap-pages.xml",
    "faqs": f"{BASE_URL}/sitemap-faqs.xml",
    "blogs": f"{BASE_URL}/sitemap-blog.xml",
}


class SitemapParser:
    """Parst alle sitemaps en retourneert URLs per categorie."""

    def __init__(self, crawler: BaseCrawler):
        self.crawler = crawler

    async def parse_all(self) -> dict[str, list[str]]:
        """Parse alle sitemaps en retourneer URLs per categorie.

        Returns:
            Dict met keys: products, faqs, blogs, pages
        """
        categorized = {}

        for category, sitemap_url in SITEMAP_MAP.items():
            logger.info(f"Ophalen sitemap: {sitemap_url}")
            xml = await self.crawler.fetch(sitemap_url)
            if xml:
                urls = self._extract_urls(xml)
                categorized[category] = urls
                logger.info(f"  {category}: {len(urls)} URLs")
            else:
                categorized[category] = []
                logger.warning(f"  {category}: sitemap niet beschikbaar")

        total = sum(len(v) for v in categorized.values())
        logger.info(f"Totaal {total} URLs uit sitemaps")

        return categorized

    def _extract_urls(self, xml: str) -> list[str]:
        """Extract URLs uit sitemap XML."""
        soup = BeautifulSoup(xml, "lxml-xml")
        urls = []
        for loc in soup.find_all("loc"):
            url = loc.text.strip()
            if url.startswith(BASE_URL):
                urls.append(url)
        return list(set(urls))  # Dedupliceer
