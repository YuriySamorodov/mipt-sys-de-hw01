from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='1')],
        [KeyboardButton(text='2')]
    ],
    resize_keyboard=True,
)