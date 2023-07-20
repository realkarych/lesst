import base64
import logging
import quopri
import re

from bs4 import BeautifulSoup

from app.settings.settings import EMAIL_NODE_SIZE


def form_mail_text_nodes(text: str) -> list[str]:
    max_characters = EMAIL_NODE_SIZE  # Telegram API limit per message
    text_builder = []
    text = re.sub(" +", " ", text)
    text = re.sub("\n+", "\n", text)
    text = re.sub("\t+", "  ", text)
    nodes_count = (len(text) // max_characters) + 1
    for node_index in range(nodes_count):
        text_builder.append(text[node_index * max_characters:(node_index + 1) * max_characters])
    return text_builder


def get_email_text(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            count = 0
            if part.get_content_maintype() == "text" and count == 0:
                extract_part = _get_letter_type(part)
                if part.get_content_subtype() == "html":
                    letter_text = _get_email_text_from_html(extract_part)
                else:
                    letter_text = extract_part.rstrip().lstrip()
                count += 1
                return (
                    letter_text.replace("<", "").replace(">", "").replace("\xa0", " ")
                )
    else:
        count = 0
        if msg.get_content_maintype() == "text" and count == 0:
            extract_part = _get_letter_type(msg)
            if msg.get_content_subtype() == "html":
                letter_text = _get_email_text_from_html(extract_part)
            else:
                letter_text = extract_part
            count += 1
            return letter_text.replace("<", "").replace(">", "").replace("\xa0", " ")


def _get_email_text_from_html(body):
    body = body.replace("<div><div>", "<div>").replace("</div></div>", "</div>")
    try:
        soup = BeautifulSoup(body, "html.parser")
        paragraphs = soup.find_all("div")
        text = ""
        for paragraph in paragraphs:
            text += paragraph.text + "\n"
        return text.replace("\xa0", " ")
    except Exception as exp:
        logging.error(exp)
        return False


def _get_letter_type(part):
    if part["Content-Transfer-Encoding"] in (None, "7bit", "8bit", "binary"):
        return part.get_payload()
    elif part["Content-Transfer-Encoding"] == "base64":
        encoding = part.get_content_charset()
        return base64.b64decode(part.get_payload()).decode(encoding)
    elif part["Content-Transfer-Encoding"] == "quoted-printable":
        encoding = part.get_content_charset()
        return quopri.decodestring(part.get_payload()).decode(encoding)
    else:  # all possible types: quoted-printable, base64, 7bit, 8bit, and binary
        return part.get_payload()

