from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union

from aiogram import Bot
from aiogram import types
from aiogram.enums import ChatAction, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo, Message, \
    InlineKeyboardMarkup, ReplyKeyboardMarkup, CallbackQuery

from app.core.states.callbackdata_ids import EMAIL_PIPELINE_MESSAGE
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
        message: Message | CallbackQuery,
        bot: Bot,
        text: str | None = None,
        text_nodes: list[str] | None = None,
        chat_id: int | None = None,
        topic_id: int | None = None,
        markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup | None = None,
        chat_action: ChatAction | None = ChatAction.TYPING,
        attachment: Attachment | None = None,
        disable_notification: bool = False,
        web_preview: bool = False,
        reply_to_message_id: int | None = None
) -> Message | list[Message]:
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
        first_message = None
        for node in text_nodes:
            msg = await bot.send_message(
                chat_id=chat_id,
                message_thread_id=topic_id,
                text=node,
                reply_markup=markup,
                disable_web_page_preview=not web_preview,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id
            )
            if not first_message:
                first_message = msg
        return first_message

    if attachment:
        match attachment.type_:
            case AttachmentType.DOCUMENT:
                return await bot.send_document(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    document=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.PHOTO:
                return await bot.send_photo(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    photo=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.VIDEO:
                return await bot.send_video(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    video=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.ROUND_VIDEO:
                return await bot.send_video_note(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    video_note=attachment.file,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.VOICE:
                return await bot.send_voice(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    voice=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.AUDIO:
                return await bot.send_audio(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    audio=attachment.file,
                    caption=text,
                    reply_to_message_id=reply_to_message_id,
                    reply_markup=markup,
                    disable_notification=disable_notification
                )
            case AttachmentType.MEDIA_GROUP:
                return await bot.send_media_group(
                    chat_id=chat_id,
                    message_thread_id=topic_id,
                    media=attachment.file,
                    reply_to_message_id=reply_to_message_id,
                    disable_notification=disable_notification,
                )
            case _:
                raise UnexpectedError("Provided unknown attachment type to send_response() method")


async def edit_or_build_email_message(
        bot: Bot,
        m: Message,
        message_id: int,
        text: str,
        markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None,
        state: FSMContext,
        disable_web_page_preview: bool = True,
        parse_mode: ParseMode | None = ParseMode.HTML
) -> None:
    """
    Method implements updates email message. If it has been removed by user, creates new and update message id in
    MemoryStorage
    """

    try:
        await bot.edit_message_text(
            chat_id=m.from_user.id,
            message_id=message_id,
            text=text,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=markup,
            parse_mode=parse_mode
        )

    except TelegramBadRequest:
        new_message = await m.answer(
            text=text,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=markup,
            parse_mode=parse_mode
        )
        await state.update_data({EMAIL_PIPELINE_MESSAGE: new_message.message_id})
