"""Configuratie voor EXIT Toys website crawler."""

import os
from pathlib import Path

# CI-detectie: GitHub Actions zet CI=true
IS_CI = os.environ.get("CI", "").lower() == "true"

# Project paden
PROJECT_DIR = Path(__file__).parent

if IS_CI:
    OUTPUT_DIR = Path("/tmp/crawler-output")
    STATE_DIR = Path("/tmp/crawler-state")
    LOGS_DIR = Path("/tmp/crawler-logs")
else:
    OUTPUT_DIR = PROJECT_DIR / "output"
    STATE_DIR = PROJECT_DIR / "state"
    LOGS_DIR = PROJECT_DIR / "logs"

# Output bestanden
KNOWLEDGE_BASE_FILE = OUTPUT_DIR / "exittoys_knowledge_base.json"
KB_PRODUCTEN_FILE = OUTPUT_DIR / "producten.json"
KB_FAQS_FILE = OUTPUT_DIR / "faqs.json"
KB_PAGINAS_FILE = OUTPUT_DIR / "paginas.json"
KNOWLEDGE_BASE_COPY = None if IS_CI else Path.home() / "Downloads" / "exittoys_knowledge_base.json"

# Product categorieën: slug → zoekwoorden (case-insensitive match op trigger+content)
PRODUCT_CATEGORIES = {
    "trampolines": ["trampoline"],
    "zwembaden": ["zwembad", "pool"],
    "speelhuisjes": ["speelhuis"],
    "sport": ["sport", "voetbal", "rebounder", "fitness"],
    "getset": ["getset", "speel- en sporttoestel"],
    "zandbak": ["zandbak"],
    "schommel": ["schommel"],
    "onderdelen": ["onderdeel"],
    "overig": [],  # catch-all
}

# Per-categorie output bestanden
KB_PRODUCTEN_CATEGORY_FILES = {
    slug: OUTPUT_DIR / f"producten-{slug}.json"
    for slug in PRODUCT_CATEGORIES
}

# State bestanden
STATE_FILE = STATE_DIR / "state.json"

# Website (custom CMS door dicode BV - GEEN Shopify)
BASE_URL = "https://www.exittoys.nl"
SITEMAPS = [
    f"{BASE_URL}/sitemap-products.xml",
    f"{BASE_URL}/sitemap-pages.xml",
    f"{BASE_URL}/sitemap-faqs.xml",
    f"{BASE_URL}/sitemap-blog.xml",
]

# Rate limiting
MAX_CONCURRENT = 3
REQUESTS_PER_SECOND = 2.0
REQUEST_TIMEOUT = 30
RETRY_COUNT = 3
RETRY_BACKOFF = 2  # exponential backoff factor

# Batch grootte voor checkpointing
BATCH_SIZE = 50

# User agent
USER_AGENT = "ExitToysCrawler/1.0 (kennisbank; contact: info@exittoys.nl)"

# URL patronen voor categorisatie
FAQ_INDEX_URL = f"{BASE_URL}/klantenservice/veelgestelde-vragen"
BLOG_INDEX_URL = f"{BASE_URL}/exit-toys/blog"
PARTS_BASE_URL = f"{BASE_URL}/onderdelen"

# Categoriepagina's voor product-discovery (paden uit sitemap-pages)
CATEGORY_PAGES = [
    "/trampolines",
    "/zwembaden",
    "/speelhuisjes",
    "/sport",
    "/getset-speel-en-sporttoestellen",
    "/zandbak",
    "/schommel",
    "/onderdelen",
    "/trampolines/allure-trampolines",
    "/trampolines/elegant-trampolines",
    "/trampolines/silhouette-trampolines",
    "/trampolines/black-edition-trampolines",
    "/trampolines/peak-trampolines",
    "/trampolines/dynamic-trampolines",
    "/trampolines/interra-trampolines",
    "/trampolines/twist-trampolines",
    "/trampolines/tiggy-trampolines",
    "/trampolines/trampoline-accessoires",
    "/zwembaden/zwembaden-overkappingen",
    "/zwembaden/wood-zwembaden",
    "/zwembaden/stone-zwembaden",
    "/zwembaden/leather-zwembaden",
    "/zwembaden/lime-zwembaden",
    "/zwembaden/frame-zwembaden",
    "/zwembaden/zwembad-accessoires",
    "/speelhuisjes/houten-speelhuisjes",
    "/speelhuisjes/speelhuisje-accessoires",
    "/sport/voetbal",
    "/sport/rebounder",
    "/sport/fitnesstoestellen-getset",
]

# Pagina's om te skippen
SKIP_PATHS = {
    "/", "/zoeken", "/sitemap", "/cookies", "/winkelwagen",
    "/account", "/checkout",
}

# Logging
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Maak directories aan
for d in [OUTPUT_DIR, STATE_DIR, LOGS_DIR]:
    d.mkdir(exist_ok=True, parents=True)
