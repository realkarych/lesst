from __future__ import annotations

from pathlib import Path, PurePath
from typing import Final

from app.services.email.base.entities import EmailServers

ROOT_DIR: Final[Path] = Path(__file__).parent.parent.parent

TEMPLATES_DIR: Final[PurePath] = PurePath(ROOT_DIR / "app/templates/")
RU_TEMPLATES_DIR: Final[PurePath] = PurePath(TEMPLATES_DIR / "ru.ftl")
EN_TEMPLATES_DIR: Final[PurePath] = PurePath(TEMPLATES_DIR / "en.ftl")

MEDIA_DIR: Final[PurePath] = PurePath(ROOT_DIR / "app/media/")
YANDEX_IMAP_IMAGE_PATH: Final[str] = str(MEDIA_DIR.joinpath("yandex_imap.png"))
GOOGLE_IMAP_IMAGE_PATH: Final[str] = str(MEDIA_DIR.joinpath("google_imap.png"))
MAIL_RU_IMAP_IMAGE_PATH: Final[str] = str(MEDIA_DIR.joinpath("mailru_imap.png"))
ACTIVATE_TOPICS_IMAGE_PATH: Final[str] = str(MEDIA_DIR.joinpath("activate_topics.png"))
GROUP_SETTINGS_IMAGE_PATH: Final[str] = str(MEDIA_DIR.joinpath("group_settings.png"))
BOT_LOGO_IMAGE_PATH: Final[str] = str(MEDIA_DIR.joinpath("bot_logo.png"))


def get_imap_image_path(email_service: EmailServers) -> str:
    match email_service:
        case EmailServers.yandex:
            path = YANDEX_IMAP_IMAGE_PATH
        case EmailServers.gmail:
            path = GOOGLE_IMAP_IMAGE_PATH
        case EmailServers.mail_ru:
            path = MAIL_RU_IMAP_IMAGE_PATH
        case _:
            path = GOOGLE_IMAP_IMAGE_PATH
    return path
