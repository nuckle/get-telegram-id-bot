import logging
import sys
import hashlib
from os import getenv

import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, URLInputFile

from dotenv import load_dotenv, find_dotenv

from uploader import upload

load_dotenv(find_dotenv())
TOKEN = getenv('TOKEN')
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()


def hash(string):
    return hashlib.md5(str(string).encode()).hexdigest()


@router.inline_query()
async def inline_id(inline_query: InlineQuery):
    user = inline_query.from_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username

    user_profile_photo_object = await user.get_profile_photos(limit=1)
    user_profile_photo_id = user_profile_photo_object.photos[0][0].file_id
    user_profile_photo_file_object = await bot.get_file(user_profile_photo_id)
    user_profile_photo_file_path = user_profile_photo_file_object.file_path

    user_profile_photo_url = (f'https://api.telegram.org/file/bot'
                              f'{TOKEN}/{user_profile_photo_file_path}')

    # can't use URL from telegram api directly
    # for more info see https://github.com/aiogram/aiogram/issues/411
    external_url = await upload(user_profile_photo_url,
                                f'{hash(user_profile_photo_file_path)}.jpg')

    msg = InlineQueryResultArticle(
        type='article',
        thumbnail_url=external_url,
        id=hash(user_id),
        title=first_name,
        input_message_content=InputTextMessageContent(
            message_text=(f'First name: {first_name}\n'
                          f'Last name: {last_name}\n'
                          f'Username: @{username} \n'
                          f'ID: <code>{user_id}</code>\n')),
        description=f'ID: {user_id}'
    )

    await bot.answer_inline_query(inline_query.id,
                                  results=[msg], cache_time=10)


@dp.message(CommandStart())
async def send_id(message: types.Message) -> None:
    id = message.from_user.id
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    await message.answer(
        f'First name: {first_name}\n'
        f'Last name: {last_name}\n'
        f'Username: @{username} \n'
        f'ID: <code>{id}</code>\n'
        f'Current chat ID: <code>{chat_id}</code>',
        parse_mode='html')


@router.message(F.content_type.in_({'contact'}))
async def get_contact(message: types.Message):
    contact_user = message.contact
    if contact_user.user_id is not None:
        chat_id = message.chat.id
        first_name = contact_user.first_name
        last_name = contact_user.last_name
        phone = contact_user.phone_number
        user_id = contact_user.user_id
        await message.answer(
            f'First name: {first_name}\n'
            f'Last name: {last_name}\n'
            f'Phone: {phone}\n'
            f'ID: <code>{user_id}</code>\n'
            f'Current chat ID: <code>{chat_id}</code>',
            parse_mode='html')
    else:
        await message.answer('The profile is hidden')


@router.message(F.forward_from)
async def check_msg(message: types.Message):
    forward_user = message.forward_from
    if forward_user is not None:
        chat_id = message.chat.id
        first_name = forward_user.first_name
        last_name = forward_user.last_name
        username = forward_user.username
        user_id = forward_user.id
        await message.answer(f'First name: {first_name}\n'
                             f'Last name: {last_name}\n'
                             f'Username: @{username} \n'
                             f'ID: <code>{user_id}</code>\n'
                             f'Current chat ID: <code>{chat_id}</code>',
                             parse_mode='html')
    else:
        await message.answer('The profile is hidden')


async def main() -> None:
    # Initialize Bot instance with a default parse mode
    # which will be passed to all API calls
    dp.include_router(router)
    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
