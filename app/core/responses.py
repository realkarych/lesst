from __future__ import annotations

import logging
from contextlib import suppress

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message, InlineKeyboardMarkup, ReplyKeyboardMarkup

from app.core import messages
from app.core.states.callbackdata_ids import EMAIL_PIPELINE_MESSAGE
from app.dtos.topic import TopicDTO
from app.services.email.base.entities import IncomingEmail


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
    Method implements updating email message. If it has been removed by user, creates new and update message id in
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

        await _update_email_message_id_memory_storage(state=state, message_id=new_message.message_id)


async def send_topic_email(bot: Bot, email: IncomingEmail, topic: TopicDTO,
                           disable_notification: bool = False) -> None:
    first_sent_message = await _send_text_email_messages(
        bot=bot, email=email, topic=topic, disable_notification=disable_notification
    )
    await _send_email_attachments(
        bot=bot, email=email, topic=topic, sent_text_message_to_reply=first_sent_message
    )


async def _update_email_message_id_memory_storage(state: FSMContext, message_id: int) -> None:
    await state.update_data({EMAIL_PIPELINE_MESSAGE: message_id})


async def _send_text_email_messages(bot: Bot, email: IncomingEmail, topic: TopicDTO,
                                    disable_notification: bool) -> Message:
    """returns first sent message"""

    first_sent_message = None
    for text in _get_email_texts(email):
        with suppress(TelegramBadRequest):
            try:
                msg = await bot.send_message(chat_id=topic.forum_id, message_thread_id=topic.topic_id,
                                             text=text, disable_notification=disable_notification)
            except Exception as e:
                msg = await bot.send_message(chat_id=topic.forum_id, message_thread_id=topic.topic_id,
                                             text=text, disable_notification=disable_notification,
                                             parse_mode=None)
                logging.warning("Parse mode error: " + str(e) + "\n" + "In text: " + text)

            if not first_sent_message:
                first_sent_message = msg

    if not email.text:
        with suppress(TelegramBadRequest):
            msg = await bot.send_message(chat_id=topic.forum_id, message_thread_id=topic.topic_id,
                                         text=messages.email_message_without_text(email),
                                         disable_notification=disable_notification)
            first_sent_message = msg

    return first_sent_message


async def _send_email_attachments(bot: Bot, email: IncomingEmail, topic: TopicDTO,
                                  sent_text_message_to_reply: Message) -> None:
    if email.attachments_paths:
        for attachment_path in email.attachments_paths:
            with suppress(TelegramBadRequest, TelegramNetworkError, FileNotFoundError):
                await bot.send_document(
                    chat_id=topic.forum_id,
                    message_thread_id=topic.topic_id,
                    reply_to_message_id=sent_text_message_to_reply.message_id,
                    document=FSInputFile(str(attachment_path))
                )


def _get_email_texts(email: IncomingEmail) -> list[str] | list[None]:
    if not email.text:
        return []
    first_text_part_index = 0
    last_text_part_index = len(email.text) - 1 if len(email.text) > 0 else 0
    texts = []
    if first_text_part_index == last_text_part_index:
        texts.append(messages.single_email_message(email))
        return texts
    for text_part, text_batch in enumerate(email.text):
        if text_part == first_text_part_index:
            texts.append(messages.first_email_message(email))
        elif text_part == last_text_part_index:
            texts.append(messages.last_email_message(email))
        else:
            texts.append(text_batch)
    return texts
