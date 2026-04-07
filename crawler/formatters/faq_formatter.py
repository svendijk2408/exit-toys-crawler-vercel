"""FAQ formatter - zet FAQ data om naar trigger/content format."""


class FAQFormatter:
    """Formatteert FAQ data naar kennisbank entries."""

    def __init__(self, labels: dict[str, str]):
        self.labels = labels

    def format(self, faq: dict) -> dict:
        """Converteer een FAQ dict naar trigger/content entry."""
        question = faq.get("question", "")
        answer = faq.get("answer", "")
        main_category = faq.get("main_category", "")
        sub_topic = faq.get("sub_topic", "")

        # Trigger: vraag + categorie zoekwoorden
        trigger_parts = [question]
        if main_category:
            trigger_parts.append(main_category.lower())
        if sub_topic and sub_topic.lower() != main_category.lower():
            trigger_parts.append(sub_topic.lower())

        trigger = " ".join(trigger_parts)

        # Content: vraag + antwoord
        content = f"{self.labels['question']}: {question}\n\n{self.labels['answer']}: {answer}"

        return {"trigger": trigger, "content": content}
