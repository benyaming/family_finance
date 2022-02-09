from typing import List

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from finance_bot import db
from finance_bot.texts import CallbackPrefixes
from finance_bot import texts
from finance_bot.models import Category, CategoryGroup


main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
main_kb.add(texts.button_categories, texts.button_subscriptions)

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cancel_kb.add(texts.button_cancel)


async def get_top_category_options(amount: int) -> InlineKeyboardMarkup:
    categories = await db.get_top_categories()
    kb = InlineKeyboardMarkup()
    for category in categories:
        kb.add(InlineKeyboardButton(
            text=category.name,
            callback_data=f'{CallbackPrefixes.transaction_category_selected}{category.id}:{amount}'
        ))
    kb.add(InlineKeyboardButton(
        text=texts.button_other,
        callback_data=f'{CallbackPrefixes.transaction_category_groups_requested}{amount}'
    ))
    return kb


def get_category_group_options_for_transaction(
        groups: List[CategoryGroup],
        amount: int
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for group in groups:
        kb.add(InlineKeyboardButton(
            text=group.name,
            callback_data=f'{CallbackPrefixes.transaction_categories_requested}{group.id}:{amount}'
        ))
    return kb


def get_category_group_options_for_management(groups: List[CategoryGroup]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for group in groups:
        kb.add(InlineKeyboardButton(
            text=group.name,
            callback_data=f'{CallbackPrefixes.management_categories_for_groups_requested}:{group.id}'
        ))
    return kb


def get_category_options(categories: List[Category], amount: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for category in categories:
        kb.add(InlineKeyboardButton(
            text=category.name,
            callback_data=f'{CallbackPrefixes.transaction_category_selected}{category.id}:{amount}'
        ))
    kb.add(InlineKeyboardButton(
        text=texts.button_back_to_category_groups,
        callback_data=f'{CallbackPrefixes.transaction_category_groups_requested}{amount}'
    ))
    return kb
