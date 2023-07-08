import re

from app.settings.limits import EMAIL_NODE_SIZE


def form_mail_text_nodes(text: str) -> list[str]:
    max_characters = EMAIL_NODE_SIZE  # Telegram API limit per message
    text_builder = []
    text = re.sub(" +", " ", text)
    text = re.sub("\n+", "\n", text)
    text = re.sub("\t+", " ", text)
    text = re.sub("\r+", " ", text)
    nodes_count = (len(text) // max_characters) + 1
    for node_index in range(nodes_count):
        text_builder.append(text[node_index * max_characters:(node_index + 1) * max_characters])
    return text_builder
