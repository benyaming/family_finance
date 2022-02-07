from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from finance_bot import db
from finance_bot.texts import CallbackPrefixes
from finance_bot import texts


main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
main_kb.add(texts.button_categories, texts.button_subscriptions)

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cancel_kb.add(texts.button_cancel)


async def get_category_menu(amount: int) -> InlineKeyboardMarkup:
    categories = await db.get_all_categories()
    kb = InlineKeyboardMarkup()
    for category in categories:
        kb.add(InlineKeyboardButton(
            text=category.name,
            callback_data=f'{CallbackPrefixes.select_amount}{category.id}:{amount}'
        ))
    return kb
