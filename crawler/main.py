#!/usr/bin/env python3
"""EXIT Toys Website Crawler - Kennisbank Generator.

Crawlt de volledige exittoys.nl website en exporteert alle data
naar een JSON kennisbank in trigger/content format voor een AI chatbot.

Gebruik:
    python3 main.py           # Hervat waar gestopt of start nieuw
    python3 main.py --force   # Volledige recrawl (wist state)
"""

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

# Voeg project root toe aan path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOG_FORMAT, LOG_LEVEL, LOGS_DIR
from crawlers.base import BaseCrawler
from crawlers.blog_crawler import BlogCrawler
from crawlers.category_crawler import CategoryCrawler
from crawlers.faq_crawler import FAQCrawler
from crawlers.page_crawler import PageCrawler
from crawlers.parts_crawler import PartsCrawler
from crawlers.product_crawler import ProductCrawler
from crawlers.sitemap_parser import SitemapParser
from formatters.knowledge_base import KnowledgeBaseGenerator
from utils.state import CrawlState

logger = logging.getLogger("crawler")


def setup_logging():
    """Configureer logging naar console en bestand."""
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(console)

    # File handler
    log_file = LOGS_DIR / "crawler.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(file_handler)


async def run_crawler(force: bool = False):
    """Hoofdfunctie die de crawler orkestreert."""
    start_time = time.monotonic()

    # State management
    state = CrawlState()
    if force:
        logger.info("Force mode: state wordt gereset")
        state.reset()

    async with BaseCrawler() as crawler:
        # ============================================================
        # FASE 1: Sitemaps parsen
        # ============================================================
        if state.phase in ("init", "sitemaps"):
            state.set_phase("sitemaps")
            logger.info("=" * 60)
            logger.info("FASE 1: Sitemaps parsen")
            logger.info("=" * 60)

            sitemap_parser = SitemapParser(crawler)
            sitemap_urls = await sitemap_parser.parse_all()

            # Sla ontdekte URLs op per categorie
            for category, urls in sitemap_urls.items():
                state.set_discovered_urls(f"sitemap_{category}", urls)

            state.set_phase("discovery")

        # ============================================================
        # FASE 2: URL Discovery (extra URLs via categoriepagina's)
        # ============================================================
        if state.phase == "discovery":
            logger.info("=" * 60)
            logger.info("FASE 2: URL Discovery")
            logger.info("=" * 60)

            # Product discovery via categoriepagina's
            known_products = set(state.get_discovered_urls("sitemap_products"))
            cat_crawler = CategoryCrawler(crawler)
            extra_products = await cat_crawler.discover_products(known_products)

            # Combineer alle product URLs
            all_product_urls = list(known_products | set(extra_products))
            state.set_discovered_urls("products", all_product_urls)
            logger.info(f"Producten totaal: {len(all_product_urls)} URLs "
                        f"({len(known_products)} sitemap + {len(extra_products)} discovery)")

            # FAQ discovery
            faq_crawler = FAQCrawler(crawler, state)
            faq_urls = await faq_crawler.discover_faq_urls(
                state.get_discovered_urls("sitemap_faqs")
            )
            state.set_discovered_urls("faqs", faq_urls)

            # Blog discovery
            blog_crawler = BlogCrawler(crawler, state)
            blog_urls = await blog_crawler.discover_blog_urls(
                state.get_discovered_urls("sitemap_blogs")
            )
            state.set_discovered_urls("blogs", blog_urls)

            # Pagina's filteren
            page_crawler = PageCrawler(crawler, state)
            page_urls = page_crawler.filter_urls(
                state.get_discovered_urls("sitemap_pages")
            )
            state.set_discovered_urls("pages", page_urls)

            state.set_phase("crawl_products")

        # ============================================================
        # FASE 3: Content crawlen
        # ============================================================
        logger.info("=" * 60)
        logger.info("FASE 3: Content crawlen")
        logger.info("=" * 60)

        # 3a: Producten
        if state.phase == "crawl_products":
            logger.info("-" * 40)
            logger.info("3a: Producten crawlen")
            product_crawler = ProductCrawler(crawler, state)
            await product_crawler.crawl_all(state.get_discovered_urls("products"))
            state.set_phase("crawl_faqs")

        # 3b: FAQs
        if state.phase == "crawl_faqs":
            logger.info("-" * 40)
            logger.info("3b: FAQs crawlen")
            faq_crawler = FAQCrawler(crawler, state)
            await faq_crawler.crawl_all(state.get_discovered_urls("faqs"))
            state.set_phase("crawl_blogs")

        # 3c: Blogs
        if state.phase == "crawl_blogs":
            logger.info("-" * 40)
            logger.info("3c: Blogs crawlen")
            blog_crawler = BlogCrawler(crawler, state)
            await blog_crawler.crawl_all(state.get_discovered_urls("blogs"))
            state.set_phase("crawl_pages")

        # 3d: Pagina's
        if state.phase == "crawl_pages":
            logger.info("-" * 40)
            logger.info("3d: Pagina's crawlen")
            page_crawler = PageCrawler(crawler, state)
            await page_crawler.crawl_all(state.get_discovered_urls("pages"))
            state.set_phase("crawl_parts")

    # 3e: Onderdelen (Playwright - eigen browser sessie)
    if state.phase == "crawl_parts":
        logger.info("-" * 40)
        logger.info("3e: Onderdelen crawlen (Playwright)")
        try:
            parts_crawler = PartsCrawler(state)
            await parts_crawler.discover_and_crawl()
        except Exception as e:
            logger.error(f"Onderdelen crawl overgeslagen: {e}")
        state.set_phase("generate")

    # ============================================================
    # FASE 4: JSON genereren
    # ============================================================
    if state.phase == "generate":
        logger.info("=" * 60)
        logger.info("FASE 4: Kennisbank genereren")
        logger.info("=" * 60)

        generator = KnowledgeBaseGenerator()
        entries = generator.generate(state.all_results())
        generator.save(entries)

        state.set_phase("done")

    # Samenvatting
    elapsed = time.monotonic() - start_time
    results = state.all_results()
    logger.info("=" * 60)
    logger.info("KLAAR!")
    logger.info(f"Producten:   {len(results.get('products', []))}")
    logger.info(f"FAQs:        {len(results.get('faqs', []))}")
    logger.info(f"Blogs:       {len(results.get('blogs', []))}")
    logger.info(f"Pagina's:    {len(results.get('pages', []))}")
    logger.info(f"Onderdelen:  {len(results.get('parts', []))}")
    logger.info(f"Totale tijd: {elapsed:.0f}s ({elapsed / 60:.1f} min)")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="EXIT Toys Website Crawler")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Volledige recrawl (wist bestaande state)",
    )
    args = parser.parse_args()

    setup_logging()
    logger.info("EXIT Toys Crawler gestart")

    try:
        asyncio.run(run_crawler(force=args.force))
    except KeyboardInterrupt:
        logger.info("Crawler onderbroken door gebruiker. State is opgeslagen - hervat later.")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Onverwachte fout: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
