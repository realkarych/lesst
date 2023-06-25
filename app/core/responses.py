from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union

from aiogram import Bot
from aiogram import types
from aiogram.enums import ChatAction
from aiogram.types import FSInputFile, InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo

from app.exceptions import UnexpectedError, AppException


class AttachmentType(str, Enum):
    DOCUMENT = "document"
    PHOTO = "photo"
    VIDEO = "video"
    ROUND_VIDEO = "round_video"
    VOICE = "voice"
    AUDIO = "audio"
    MEDIA_GROUP = "media_group"


@dataclass(frozen=True)
class Attachment:
    type_: AttachmentType
    file: FSInputFile | list[Union[InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo]]


async def send_response(
        message: types.Message | types.CallbackQuery,
        bot: Bot,
        text: str | None = None,
        text_nodes: list[str] | None = None,
        chat_id: int | None = None,
        topic_id: int | None = None,
        markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup | None = None,
        chat_action: ChatAction | None = ChatAction.TYPING,
        attachment: Attachment | None = None,
        disable_notification: bool = False,
        web_preview: bool = True,
        reply_to_message_id: int | None = None
) -> None:
    if text and text_nodes:
        raise AppException("Provide text or text_nodes. Not both!")
    if not attachment and not text and not text_nodes:
        raise AppException("Provide text or text_nodes or attachment")

    if not chat_id:
        chat_id = message.from_user.id
    if chat_action:
        await bot.send_chat_action(chat_id=chat_id, message_thread_id=topic_id, action=chat_action)

    if not attachment:
        if not text_nodes and text:
            text_nodes = [text]
        for node in text_nodes:
            await bot.send_message(
                chat_id=chat_id,
                message_thread_id=topic_id,
                text=node,
                reply_markup=markup,
                disable_web_page_preview=not web_preview,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id
            )

    if attachment:
        match attachment.type_:
            case AttachmentType.DOCUMENT:
                await bot.send_document(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    document=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.PHOTO:
                await bot.send_photo(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    photo=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.VIDEO:
                await bot.send_video(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    video=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.ROUND_VIDEO:
                await bot.send_video_note(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    video_note=attachment.file,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.VOICE:
                await bot.send_voice(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    voice=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.AUDIO:
                await bot.send_audio(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    audio=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.MEDIA_GROUP:
                await bot.send_media_group(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    media=attachment.file,
                    reply_to_message_id=reply_to_message_id,
                    disable_notification=disable_notification,
                )
            case _:
                raise UnexpectedError("Provided unknown attachment type to send_response() method")
