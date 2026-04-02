"""Page formatter - zet pagina data om naar trigger/content format."""


class PageFormatter:
    """Formatteert pagina data naar kennisbank entries."""

    def format(self, page: dict) -> dict:
        """Converteer een pagina dict naar trigger/content entry."""
        title = page.get("title", "")
        content_text = page.get("content", "")
        meta_desc = page.get("meta_description", "")
        url = page.get("url", "")

        # Trigger: titel + relevante zoekwoorden
        trigger_parts = [title]

        # Voeg contextwoorden toe op basis van URL/inhoud
        url_lower = url.lower()
        content_lower = content_text.lower()

        keyword_map = {
            "contact": "EXIT Toys contactgegevens klantenservice telefoon email",
            "verzend": "verzending levering bezorging",
            "retour": "retourneren terugsturen",
            "garantie": "garantie reparatie",
            "veiligheid": "veiligheid normen keurmerken",
            "keuzehulp": "keuzehulp vergelijken welke kiezen",
            "onderhoud": "onderhoud schoonmaken",
            "over-exit": "over EXIT Toys bedrijf",
        }

        for key, words in keyword_map.items():
            if key in url_lower or key in content_lower:
                trigger_parts.append(words)
                break

        trigger = " ".join(trigger_parts)

        # Content
        content_parts = []
        if meta_desc:
            content_parts.append(meta_desc)
            content_parts.append("")
        content_parts.append(content_text)

        content = "\n".join(content_parts)

        return {"trigger": trigger, "content": content}
