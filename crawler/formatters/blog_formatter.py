"""Blog formatter - zet blog data om naar trigger/content format."""


class BlogFormatter:
    """Formatteert blog data naar kennisbank entries."""

    def __init__(self, labels: dict[str, str], blog_categories: dict[str, str]):
        self.labels = labels
        self.categories = blog_categories

    def format(self, blog: dict) -> dict:
        """Converteer een blog dict naar trigger/content entry."""
        title = blog.get("title", "")
        author = blog.get("author", "")
        date = blog.get("date", "")
        content_text = blog.get("content", "")

        # Trigger: titel + "blog" + relevante zoekwoorden
        trigger_parts = [title, "blog"]

        # Voeg categorie-gerelateerde woorden toe
        title_lower = title.lower()
        for keyword, category in self.categories.items():
            if keyword in title_lower:
                trigger_parts.append(category)
                break

        trigger = " ".join(trigger_parts)

        # Content: volledige blogpost
        content_parts = [title]
        if author:
            content_parts.append(f"{self.labels['author']}: {author}")
        if date:
            content_parts.append(f"{self.labels['date']}: {date}")
        content_parts.append(f"URL: {blog.get('url', '')}")
        content_parts.append("")
        content_parts.append(content_text)

        content = "\n".join(content_parts)

        return {"trigger": trigger, "content": content}
