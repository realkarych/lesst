from __future__ import annotations

import os
from pathlib import Path, PurePath


ROOT_DIR: Path = Path(__file__).parent.parent.parent

TEMPLATES_DIR: PurePath = PurePath(ROOT_DIR / "app/templates/")
RU_TEMPLATES_DIR: PurePath = PurePath(TEMPLATES_DIR / "ru.ftl")
EN_TEMPLATES_DIR: PurePath = PurePath(TEMPLATES_DIR / "en.ftl")


MEDIA_DIR: PurePath = PurePath(ROOT_DIR / "app/media/")
YANDEX_IMAP_IMAGE_PATH: str = str(MEDIA_DIR.joinpath("yandex_imap.png"))
GOOGLE_IMAP_IMAGE_PATH: str = str(MEDIA_DIR.joinpath("google_imap.png"))
MAIL_RU_IMAP_IMAGE_PATH: str = str(MEDIA_DIR.joinpath("mailru_imap.png"))
ACTIVATE_TOPICS_IMAGE_PATH: str = str(MEDIA_DIR.joinpath("activate_topics.png"))
GROUP_SETTINGS_IMAGE_PATH: str = str(MEDIA_DIR.joinpath("group_settings.png"))
BOT_LOGO_IMAGE_PATH: str = str(MEDIA_DIR.joinpath("bot_logo.png"))
