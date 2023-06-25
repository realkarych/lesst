from __future__ import annotations

import os
import shutil
from pathlib import PurePath

from mailparser import MailParser

from app.settings.paths import ROOT_DIR


class EmailCacheDirectory:

    def __init__(self, user_id: int) -> None:
        self._user_id = user_id

    def __enter__(self) -> EmailCacheDirectory:
        self._path = self._build_base_path()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._remove()

    def save_attachments(self, email: MailParser, email_id: int) -> tuple[str] | None:
        """: Returns saved attachments paths"""
        if email.attachments:
            email.write_attachments(base_path=str(self._build_path(email_id)))
        return self._get_saved_attachments_paths(email_id)

    def _get_saved_attachments_paths(self, email_id: int) -> tuple[str] | None:
        attachments_paths = list()
        path = self._build_path(email_id)
        for file_name in os.listdir(path):
            attachments_paths.append(str(path / file_name))
        if not attachments_paths:
            return None
        return tuple(attachments_paths)

    def _remove(self) -> None:
        shutil.rmtree(self._path, ignore_errors=True)

    def _build_base_path(self) -> PurePath:
        cache_dir = PurePath(ROOT_DIR / "app/.cache")
        path = PurePath(cache_dir / str(self._user_id))
        return path

    def _build_path(self, email_id: int) -> PurePath:
        path = PurePath(self._path / str(email_id))
        return path
