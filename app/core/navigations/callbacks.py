from typing import Final
from enum import Enum

RETURN_TO_SERVICES: Final[str] = "return_to_services"
RETURN_TO_EMAIL: Final[str] = "return_to_email"


class Draft(str, Enum):
    SEND: Final[str] = "draft_send"
    REMOVE: Final[str] = "draft_remove"
    EDIT_TEXT: Final[str] = "draft_edit_text"
    EDIT_SUBJECT: Final[str] = "draft_edit_subject"
    EDIT_RECIPIENT_ADDRESS: Final[str] = "draft_edit_recipient_address"
    EDIT_ATTACHMENTS: Final[str] = "draft_edit_attachments"

    def __repr__(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value
