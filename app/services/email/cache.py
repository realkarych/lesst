from __future__ import annotations

import os
import shutil
from pathlib import PurePath

from mailparser import MailParser

from app.settings.paths import ROOT_DIR


class EmailCacheDirectory:

    def __init__(self, user_id: int, email_id: str | None = None) -> None:
        self._user_id = user_id
        self._email_id = email_id
        self._path = self._build_path()

    def __enter__(self) -> EmailCacheDirectory:
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.remove()

    def save_attachments(self, email: MailParser) -> None:
        if email.attachments:
            email.write_attachments(base_path=str(self._path))

    def get_saved_attachments_paths(self) -> tuple[str] | None:
        attachments_paths = list()
        for file_name in os.listdir(self._path):
            attachments_paths.append(str(self._path / file_name))
        if not attachments_paths:
            return None
        return tuple(attachments_paths)

    def remove(self) -> None:
        shutil.rmtree(self._path, ignore_errors=True)

    def _build_path(self) -> PurePath:
        cache_dir = PurePath(ROOT_DIR / "app/.cache")
        if self._email_id:
            path = PurePath(cache_dir / f"{self._user_id}/{self._email_id}")
        else:
            path = PurePath(cache_dir / str(self._user_id))
        return path
