"""Locale configuratie voor de EXIT Toys crawler."""

from locales.base import LocaleConfig
from locales.de import DE_CONFIG
from locales.nl import NL_CONFIG

LOCALES: dict[str, LocaleConfig] = {
    "nl": NL_CONFIG,
    "de": DE_CONFIG,
}


def get_locale_config(locale: str) -> LocaleConfig:
    """Haal de locale configuratie op."""
    if locale not in LOCALES:
        raise ValueError(f"Onbekende locale: {locale}. Kies uit: {list(LOCALES.keys())}")
    return LOCALES[locale]
