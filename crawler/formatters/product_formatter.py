"""Product formatter - zet productdata om naar trigger/content format."""


class ProductFormatter:
    """Formatteert productdata naar kennisbank entries."""

    def format(self, product: dict) -> dict:
        """Converteer een product dict naar trigger/content entry."""
        name = product.get("name", "")
        sku = product.get("sku", "")
        category = product.get("category", "")
        model = product.get("model", "")
        size = product.get("size", "")

        # Trigger: productnaam, categorie, serie, artikelnr + zoekwoorden
        trigger_parts = [name]
        if category:
            trigger_parts.append(category)
        if model and model not in name:
            trigger_parts.append(model)
        if size and size not in name:
            trigger_parts.append(size)
        if sku:
            trigger_parts.append(sku)

        # Gewicht toevoegen als het er is
        weight = self._get_spec_value(product, "Gewicht")
        if weight:
            trigger_parts.append(f"Gewicht {weight}")

        trigger = " ".join(trigger_parts)

        # Prijs formatteren met decimalen
        price = product.get("price", "")
        if price:
            try:
                price_formatted = f"{float(price):.2f}"
            except (ValueError, TypeError):
                price_formatted = price
        else:
            price_formatted = ""

        # Content opbouwen
        content_parts = []
        content_parts.append(f"Product: {name}")

        if price_formatted:
            content_parts.append(f"Prijs: €{price_formatted}")
        if sku:
            content_parts.append(f"Artikelnummer: {sku}")
        if category:
            content_parts.append(f"Categorie: {category}")
        if model:
            content_parts.append(f"Serie: {model}")

        # Type uit specificaties
        product_type = self._get_spec_value(product, "Type")
        if product_type:
            content_parts.append(f"Type: {product_type}")
        elif product.get("type") == "onderdeel":
            content_parts.append("Type: Onderdeel")

        if size:
            content_parts.append(f"Afmetingen: {size}")

        # Kleur
        color = product.get("color", "") or self._get_spec_value(product, "Kleur")
        if color:
            content_parts.append(f"Kleur: {color}")

        content_parts.append(f"URL: {product.get('url', '')}")

        # Beschrijving
        desc = product.get("description", "")
        if desc:
            content_parts.append(f"\nBeschrijving:\n{desc}")

        # USPs
        usps = product.get("usps", [])
        if usps:
            content_parts.append("\nKenmerken:")
            for usp in usps:
                content_parts.append(f"- {usp}")

        # Specificaties
        specs = product.get("specifications", [])
        if specs:
            content_parts.append("\nSpecificaties:")
            for group in specs:
                content_parts.append(f"[{group['group']}]")
                for spec in group["specs"]:
                    content_parts.append(f"{spec['key']}: {spec['value']}")

        # Levertijd
        delivery = product.get("delivery", "")
        if delivery:
            content_parts.append(f"\n{delivery}")

        # On-page FAQs
        faqs = product.get("faqs", [])
        if faqs:
            content_parts.append("\nVeelgestelde vragen:")
            for faq in faqs:
                content_parts.append(f"V: {faq['question']}")
                content_parts.append(f"A: {faq['answer']}")

        content = "\n".join(content_parts)

        return {"trigger": trigger, "content": content}

    def _get_spec_value(self, product: dict, key: str) -> str:
        """Zoek een specifieke spec waarde."""
        for group in product.get("specifications", []):
            for spec in group["specs"]:
                if spec["key"].lower() == key.lower():
                    return spec["value"]
        return ""
