import re
from typing import List
from datetime import datetime as dt

import psycopg.errors
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, User
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

from finance_bot import db
from finance_bot import texts
from finance_bot.misc import bot
from finance_bot import keyboards
from finance_bot.models import Category, CategoryGroup, Limit
from finance_bot.settings import env
from finance_bot.texts import StorageKeys
from finance_bot.states import (
    RenameCategoryState,
    AddCategoryState,
    AddGroupState,
    RenameGroupState,
    SetLimitState
)


separator = '\n-----------------------------------------------\n'


def compose_categories(group: CategoryGroup, categories: List[Category]) -> str:
    categories_lines = []
    for category in categories:
        line = f'<b>{category.name}</b>\n' \
               f'{texts.cat_manage_edit_cat}: /rename_cat_{category.id}\n' \
               f'{texts.cat_manage_move_cat}: /move_cat_{category.id}' \

        categories_lines.append(line)

    empty_case = f'{texts.cat_manage_group_is_empty} /remove_group_{group.id}'

    category_str = separator.join(categories_lines) if categories else empty_case

    if group.limit:
        limit_str = texts.limits_header.format(group.limit, env.CURRENCY_CHAR, group.id, group.id)
    else:
        limit_str = texts.limits_no_limit.format(group.id)

    resp = f'{texts.cat_manage_title} <b>{group.name}</b>:\n\n' \
           f'{limit_str}\n\n' \
           f'{category_str}{separator}' \
           f'{texts.cat_manage_add_cat}: /new_cat_{group.id}\n' \
           f'{texts.group_manage_edit_name}: /rename_group_{group.id}\n'

    return resp


def compose_limits(limits: list[Limit]) -> str:
    if len(limits) == 0:
        return texts.limits_no_found

    limits_rows = []

    for limit in limits:
        if limit.usage_percentage < 70:
            indicator = '🟢'
        elif limit.usage_percentage < 100:
            indicator = '🟡'
        else:
            indicator = '🔴'

        row = f'{indicator} <b>{limit.group_name}</b>\n' \
              f'{texts.limits_spent} {limit.spent}{env.CURRENCY_CHAR} / {limit.limit}{env.CURRENCY_CHAR} (<b>{limit.usage_percentage}%</b>)\n' \
              f'{texts.limits_rest} {limit.rest if limit.rest > 0 else 0}{env.CURRENCY_CHAR}'
        limits_rows.append(row)

    rows = separator.join(limits_rows)

    resp = f'{texts.limits_dt_header} {dt.now().isoformat(sep=" ", timespec="minutes")}\n\n{rows}'
    return resp


async def _update_last_group_menu(data: dict):
    if msg_id := data.get(StorageKeys.last_groups_menu_msg_id):
        groups = await db.get_category_groups(with_empty=True)
        kb = keyboards.get_category_group_options_for_management(groups)
        user_id = User.get_current().id

        try:
            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=msg_id,
                reply_markup=kb
            )
        except MessageNotModified:
            pass


async def _update_last_category_menu(data: dict, group: CategoryGroup):
    storage_data = data.get(StorageKeys.last_category_msg_id, {})
    if msg_id := storage_data.get(group.id):
        categories = await db.get_categories_for_group(group.id)
        resp = compose_categories(group, categories)
        user_id = User.get_current().id

        try:
            await bot.edit_message_text(resp, chat_id=user_id, message_id=msg_id)
        except MessageNotModified:
            pass


async def prepare_groups_selection_menu(msg: Message, state: FSMContext):
    await state.reset_state(with_data=False)
    category_groups = await db.get_category_groups(with_empty=True)
    kb = keyboards.get_category_group_options_for_management(category_groups)
    sent = await msg.reply(texts.msg_select_category_group_for_manage, reply_markup=kb)
    await state.update_data({StorageKeys.last_groups_menu_msg_id: sent.message_id})


async def prepare_category_management_menu(call: CallbackQuery, state: FSMContext):
    await call.answer()
    category_group_id = int(call.data.split(':')[-1])
    group = await db.get_category_group(category_group_id)
    categories = await db.get_categories_for_group(category_group_id)
    msg = await bot.send_message(call.from_user.id, compose_categories(group, categories))

    storage_data = (await state.get_data()).get(StorageKeys.last_category_msg_id, {})
    storage_data[category_group_id] = msg.message_id
    await state.update_data({StorageKeys.last_category_msg_id: storage_data})


async def prepare_change_group_menu(msg: Message, regexp_command: re.Match, state: FSMContext):
    category_id = int(regexp_command.group(1))
    category = await db.get_category(category_id)
    groups = await db.get_category_groups(with_empty=True)
    groups = [group for group in groups if group.id != category.group_id]

    kb = keyboards.get_category_group_options_for_move_category(groups)
    resp = texts.msg_select_group_to_change.format(category.name)
    sent = await msg.reply(resp, reply_markup=kb)
    await state.update_data({StorageKeys.category_to_move_id: category_id})
    await state.update_data({StorageKeys.last_select_group_menu_to_delete_msg_id: sent.message_id})


async def rename_category(msg: Message, regexp_command: re.Match, state: FSMContext):
    await state.reset_state(with_data=False)
    category_id = int(regexp_command.group(1))
    category = await db.get_category(category_id)
    await state.update_data({StorageKeys.category_id: category_id})
    await RenameCategoryState.waiting_for_new_name.set()
    await msg.answer(
        texts.msg_input_name_for_specific_category.format(category.name),
        reply_markup=keyboards.cancel_kb
    )


async def rename_group(msg: Message, regexp_command: re.Match, state: FSMContext):
    await state.reset_state(with_data=False)
    group_id = int(regexp_command.group(1))
    group = await db.get_category_group(group_id)
    await state.update_data({StorageKeys.group_id: group_id})
    await RenameGroupState.waiting_for_new_name.set()
    await msg.answer(
        texts.msg_input_name_for_specific_group.format(group.name),
        reply_markup=keyboards.cancel_kb
    )


async def new_category(msg: Message, regexp_command: re.Match, state: FSMContext):
    await state.reset_state(with_data=False)
    grop_id = int(regexp_command.group(1))
    await state.update_data({StorageKeys.group_id: grop_id})
    await AddCategoryState.waiting_for_new_name.set()
    await msg.answer(texts.msg_input_name_for_new_category, reply_markup=keyboards.cancel_kb)


async def remove_group(msg: Message, regexp_command: re.Match, state: FSMContext):
    group_id = int(regexp_command.group(1))

    try:
        group = await db.get_category_group(group_id)
    except TypeError:
        return await msg.answer(texts.msg_group_not_found)

    categories = await db.get_categories_for_group(group_id)
    if len(categories) > 0:
        return await msg.answer(texts.msg_cannot_remove_group_with_categories)

    await db.remove_category_group(group_id)
    await msg.answer(texts.msg_category_group_removed.format(group.name))
    await _update_last_group_menu(await state.get_data())


async def add_new_group(call: CallbackQuery):
    await call.answer()
    await AddGroupState.waiting_for_new_name.set()
    await bot.send_message(call.from_user.id, texts.msg_input_name_for_new_group, reply_markup=keyboards.cancel_kb)


async def add_category_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data['group_id']
    group = await db.get_category_group(group_id)
    new_name = msg.text

    try:
        await db.save_category(new_name, group_id)
    except psycopg.errors.UniqueViolation:
        return await msg.reply(texts.msg_category_already_exists)

    await state.reset_state(with_data=False)
    await msg.answer(texts.msg_category_add_success.format(new_name, group.name), reply_markup=ReplyKeyboardRemove())

    if group_id in data.get(StorageKeys.last_category_msg_id, {}).keys():
        msg_id = data[StorageKeys.last_category_msg_id][group_id]
        categories = await db.get_categories_for_group(group.id)
        resp = compose_categories(group, categories)
        await bot.edit_message_text(resp, chat_id=msg.chat.id, message_id=msg_id)


async def handle_group_name(msg: Message, state: FSMContext):
    new_name = msg.text
    await state.update_data({StorageKeys.new_group_group_name: new_name})
    await AddGroupState.next()

    await msg.reply(texts.limits_input_amount, reply_markup=keyboards.done_kb)


async def handle_group_limit(msg: Message, state: FSMContext):
    data = await state.get_data()
    new_name = data[StorageKeys.new_group_group_name]

    if msg.text == texts.button_done:
        limit = None
    else:
        try:
            limit = int(msg.text)
        except ValueError:
            return await msg.reply(texts.limits_incorrect_amount)

    try:
        await db.save_category_group(new_name, limit)
    except psycopg.errors.UniqueViolation:
        return await msg.answer(texts.msg_group_name_already_exists)

    await msg.answer(texts.msg_group_add_success.format(new_name), reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)
    await _update_last_group_menu(await state.get_data())


async def update_category_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data[StorageKeys.category_id]
    category = await db.get_category(category_id)
    storage_data = data.get(StorageKeys.last_category_msg_id, {})

    category.name = msg.text
    await db.update_category(category)
    await state.reset_state(with_data=False)
    await msg.answer(
        texts.msg_category_rename_success.format(category.name),
        reply_markup=ReplyKeyboardRemove()
    )

    if category.group_id in storage_data.keys():
        msg_id = storage_data[category.group_id]
        group = await db.get_category_group(category.group_id)
        categories = await db.get_categories_for_group(group.id)
        resp = compose_categories(group, categories)
        try:
            await bot.edit_message_text(resp, chat_id=msg.chat.id, message_id=msg_id)
        except MessageNotModified:
            pass


async def update_group_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data['group_id']

    new_name = msg.text
    await db.rename_category_group(group_id, new_name)
    await state.reset_state(with_data=False)
    await msg.answer(
        texts.msg_group_rename_success.format(new_name),
        reply_markup=ReplyKeyboardRemove()
    )
    await _update_last_group_menu(await state.get_data())


async def change_group_for_category(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()

    new_group_id = int(call.data.split(':')[1])
    category_id = data[StorageKeys.category_to_move_id]
    category = await db.get_category(category_id)
    old_group_id = category.group_id
    category.group_id = new_group_id
    await db.update_category(category)

    group = await db.get_category_group(category.group_id)
    resp = texts.msg_category_move_success.format(category.name, group.name)
    await bot.send_message(call.from_user.id, resp)

    if StorageKeys.last_select_group_menu_to_delete_msg_id in data:
        msg_id = data.pop(StorageKeys.last_select_group_menu_to_delete_msg_id)
        await bot.delete_message(chat_id=call.from_user.id, message_id=msg_id)
        await state.update_data(data)

    if old_group_id in data.get(StorageKeys.last_category_msg_id, {}):
        msg_id = data[StorageKeys.last_category_msg_id][old_group_id]
        group = await db.get_category_group(old_group_id)
        categories = await db.get_categories_for_group(group.id)
        resp = compose_categories(group, categories)
        await bot.edit_message_text(resp, chat_id=call.from_user.id, message_id=msg_id)


async def init_set_group_limit(msg: Message, regexp_command: re.Match, state: FSMContext):
    group_id = int(regexp_command.group(1))

    try:
        group = await db.get_category_group(group_id)
    except TypeError:
        return await msg.answer(texts.msg_group_not_found)

    await state.update_data({StorageKeys.new_limit_group_id: group_id})
    await SetLimitState.waiting_for_amount.set()
    await msg.reply(texts.limits_update_amount.format(group.id), reply_markup=keyboards.cancel_kb)


async def update_group_limit(msg: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data[StorageKeys.new_limit_group_id]

    new_limit = int(msg.text)
    await db.set_limit_for_category_group(group_id, new_limit)
    await state.reset_state(with_data=False)
    await msg.answer(
        texts.limits_limit_set_success,
        reply_markup=ReplyKeyboardRemove()
    )

    group = await db.get_category_group(group_id)
    await _update_last_category_menu(await state.get_data(), group)


async def remove_group_limit(msg: Message, regexp_command: re.Match, state: FSMContext):
    group_id = int(regexp_command.group(1))

    await db.set_limit_for_category_group(group_id, None)
    await state.reset_state(with_data=False)
    await msg.answer(
        texts.limits_limit_set_success,
        reply_markup=ReplyKeyboardRemove()
    )

    group = await db.get_category_group(group_id)
    await _update_last_category_menu(await state.get_data(), group)


async def get_limits_dashboard(msg: Message):
    limits = await db.get_limits()
    resp = compose_limits(limits)
    await msg.reply(resp)
