"""Product parser - extractie van productdata uit HTML + JSON-LD."""

from __future__ import annotations

import json
import logging
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ProductParser:
    """Parst productpagina's en extraheert alle relevante data."""

    def __init__(self, in_stock_text: str = "Op voorraad", out_of_stock_text: str = "Niet op voorraad"):
        self.in_stock_text = in_stock_text
        self.out_of_stock_text = out_of_stock_text

    def parse(self, url: str, html: str) -> dict | None:
        """Parse een productpagina en retourneer gestructureerde data."""
        soup = BeautifulSoup(html, "lxml")

        # Controleer of dit echt een productpagina is
        product_div = soup.find("div", id="div_webshopproductversions")
        if not product_div:
            return None

        data = {
            "url": url,
            "type": "product",
        }

        # JSON-LD data (primaire bron)
        jsonld = self._parse_jsonld(soup)
        if jsonld:
            data["name"] = jsonld.get("name", "")
            data["sku"] = jsonld.get("sku", "")
            data["description_short"] = jsonld.get("description", "")
            data["brand"] = jsonld.get("brand", {}).get("name", "EXIT Toys")
            data["category"] = jsonld.get("category", "")
            data["model"] = jsonld.get("model", "")
            data["color"] = jsonld.get("color", "")
            data["size"] = jsonld.get("size", "")
            data["gtin13"] = jsonld.get("gtin13", "")
            offers = jsonld.get("offers", {})
            data["price"] = offers.get("price", "")
            data["currency"] = offers.get("priceCurrency", "EUR")
            data["availability"] = self.in_stock_text if "InStock" in offers.get("availability", "") else self.out_of_stock_text
        else:
            # Fallback naar HTML data-attributen
            data["name"] = product_div.get("data-name", "")
            data["sku"] = product_div.get("data-id", "")
            data["price"] = product_div.get("data-price", "")
            data["currency"] = product_div.get("data-currency", "EUR")
            data["category"] = product_div.get("data-section", "")
            data["model"] = product_div.get("data-group", "")

        # Titel uit H1
        h1 = soup.select_one("#div_productchoices h1")
        if h1:
            data["name"] = h1.get_text(strip=True)

        # Beschrijving uit productcontent
        data["description"] = self._parse_description(soup)

        # Specificaties (gegroepeerd)
        data["specifications"] = self._parse_specifications(soup)

        # USPs
        data["usps"] = self._parse_usps(soup)

        # On-page FAQs
        data["faqs"] = self._parse_product_faqs(soup)

        # Levertijd
        shipping = soup.select_one("#div_productchoices .shipping .title")
        if shipping:
            data["delivery"] = shipping.get_text(strip=True)

        return data

    def _parse_jsonld(self, soup: BeautifulSoup) -> dict | None:
        """Extract Product JSON-LD structured data."""
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                ld = json.loads(script.string)
                # Kan een array of een enkel object zijn
                if isinstance(ld, list):
                    for item in ld:
                        if item.get("@type") == "Product":
                            return item
                elif isinstance(ld, dict) and ld.get("@type") == "Product":
                    return ld
            except (json.JSONDecodeError, TypeError):
                continue
        return None

    def _parse_description(self, soup: BeautifulSoup) -> str:
        """Extract productbeschrijving inclusief 'lees meer' content."""
        desc_div = soup.select_one(".content.productcontent")
        if not desc_div:
            return ""

        # Verwijder knoppen en navigatie-elementen
        for elem in desc_div.select("button, .readmore, .backtooverview"):
            elem.decompose()

        # Haal alle tekst op (inclusief hidden/lees-meer content)
        hidden = desc_div.select_one(".hidden")
        if hidden:
            # Maak hidden content zichtbaar voor extractie
            hidden["class"] = []

        parts = []
        for elem in desc_div.find_all(["h4", "h3", "h2", "p", "li"]):
            text = elem.get_text(strip=True)
            if text:
                parts.append(text)

        return "\n".join(parts)

    def _parse_specifications(self, soup: BeautifulSoup) -> list[dict]:
        """Extract gegroepeerde specificaties."""
        spec_groups = []
        features_container = soup.select_one(".content.features")
        if not features_container:
            return spec_groups

        for group in features_container.select(".features"):
            title_elem = group.select_one(".head .ctitle")
            if not title_elem:
                continue

            group_data = {
                "group": title_elem.get_text(strip=True),
                "specs": [],
            }

            for feature in group.select(".items .feature"):
                key_elem = feature.select_one(".key")
                value_elem = feature.select_one(".value")
                if key_elem and value_elem:
                    key = key_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    if key and value:
                        group_data["specs"].append({"key": key, "value": value})

            if group_data["specs"]:
                spec_groups.append(group_data)

        return spec_groups

    def _parse_usps(self, soup: BeautifulSoup) -> list[str]:
        """Extract USP punten."""
        usps = []
        for li in soup.select("#div_productchoices .usps ul li"):
            text = li.get_text(strip=True)
            if text:
                usps.append(text)
        return usps

    def _parse_product_faqs(self, soup: BeautifulSoup) -> list[dict]:
        """Extract on-page FAQ's van een productpagina."""
        faqs = []
        faq_container = soup.select_one(".faqsitem")
        if not faq_container:
            return faqs

        current_category = ""
        for elem in faq_container.select(".subtitle, .question, .answer"):
            if "subtitle" in elem.get("class", []):
                current_category = elem.get_text(strip=True)
            elif "question" in elem.get("class", []):
                faqs.append({
                    "category": current_category,
                    "question": elem.get_text(strip=True),
                    "answer": "",
                })
            elif "answer" in elem.get("class", []) and faqs:
                faqs[-1]["answer"] = elem.get_text(strip=True)

        return [f for f in faqs if f["question"] and f["answer"]]
