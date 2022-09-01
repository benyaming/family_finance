from typing import List

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from finance_bot import db
from finance_bot.texts import CallbackPrefixes
from finance_bot import texts
from finance_bot.models import Category, CategoryGroup


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


def get_category_options_for_subscription(categories: List[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for category in categories:
        kb.add(InlineKeyboardButton(
            text=category.name,
            callback_data=f'{CallbackPrefixes.subscription_category_selected}{category.id}'
        ))
    kb.add(InlineKeyboardButton(
        text=texts.button_back_to_category_groups,
        callback_data=f'{CallbackPrefixes.subscription_category_groups_requested}'
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


def get_category_group_options_for_subscription(
        groups: List[CategoryGroup]
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for group in groups:
        kb.add(InlineKeyboardButton(
            text=group.name,
            callback_data=f'{CallbackPrefixes.subscription_categories_requested}{group.id}'
        ))
    return kb


def get_category_group_options_for_management(groups: List[CategoryGroup]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for group in groups:
        kb.add(InlineKeyboardButton(
            text=group.name,
            callback_data=f'{CallbackPrefixes.management_categories_for_groups_requested}:{group.id}'
        ))
    kb.add(InlineKeyboardButton(
        text=texts.button_add_group,
        callback_data=CallbackPrefixes.management_groups_add_new_group
    ))
    return kb


def get_category_group_options_for_move_category(groups: List[CategoryGroup]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for group in groups:
        kb.add(InlineKeyboardButton(
            text=group.name,
            callback_data=f'{CallbackPrefixes.management_categories_move_to_another_group}{group.id}'
        ))
    return kb


def get_detailed_stats_kb(
        group_ids: List[int],
        group_names: List[str],
        month: int,
        year: int
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for group_id, group_name in zip(group_ids, group_names):
        kb.add(InlineKeyboardButton(
            text=f'{texts.stats_details_button_prefix}{group_name}',
            callback_data=f'{CallbackPrefixes.detailed_stats_for_group_requested}{group_id}:{month}:{year}'
        ))
    return kb


def get_subscription_management_kb(subscription_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    # kb.add(InlineKeyboardButton(
    #     text=texts.button_edit_sub_name,
    #     callback_data=f'{CallbackPrefixes.subscription_edit_name}{subscription_id}'
    # ))
    # kb.add(InlineKeyboardButton(
    #     text=texts.button_edit_sub_amount,
    #     callback_data=f'{CallbackPrefixes.subscription_edit_amount}{subscription_id}'
    # ))
    # kb.add(InlineKeyboardButton(
    #     text=texts.button_edit_sub_date,
    #     callback_data=f'{CallbackPrefixes.subscription_edit_date}{subscription_id}'
    # ))
    # kb.add(InlineKeyboardButton(
    #     text=texts.button_edit_sub_category,
    #     callback_data=f'{CallbackPrefixes.subscription_edit_category}{subscription_id}'
    # ))
    kb.add(InlineKeyboardButton(
        text=texts.button_remove_sub,
        callback_data=f'{CallbackPrefixes.subscription_remove}{subscription_id}'
    ))
    return kb


def get_confirm_subscription_kb(subscription_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text=texts.button_process_subscription,
        callback_data=f'{CallbackPrefixes.subscription_confirm}{subscription_id}'
    ))
    return kb
