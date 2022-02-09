import re
from typing import List

from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from finance_bot import db
from finance_bot import texts
from finance_bot.misc import bot
from finance_bot import keyboards
from finance_bot.models import Category, CategoryGroup
from finance_bot.texts import StorageKeys
from finance_bot.states import RenameCategoryState, AddCategoryState


def compose_categories(group: CategoryGroup, categories: List[Category]) -> str:
    categories_lines = []
    for category in categories:
        line = f'<b>{category.name}</b>\n' \
               f'Переименовать: /rename_category_{category.id}'
        categories_lines.append(line)
    separator = '\n-----------------------------------------------\n'
    category_str = separator.join(categories_lines)
    resp = f'Управление категориями группы <b>{group.name}</b>:\n\n' \
           f'{category_str}{separator}' \
           f'Добавить категорию: /new_category_{group.id}'

    return resp


async def init_category_management_selection(msg: Message):
    category_groups = await db.get_category_groups()
    kb = keyboards.get_category_group_options_for_management(category_groups)
    await msg.reply(texts.message_select_category_group_for_manage, reply_markup=kb)


async def prepare_category_management_menu(call: CallbackQuery, state: FSMContext):
    await call.answer()
    category_group_id = int(call.data.split(':')[-1])
    group = await db.get_category_group(category_group_id)
    categories = await db.get_categories_for_group(category_group_id)
    msg = await bot.send_message(call.from_user.id, compose_categories(group, categories))

    storage_data = (await state.get_data()).get(StorageKeys.last_category_msg_id, {})
    storage_data[category_group_id] = msg.message_id
    await state.update_data({StorageKeys.last_category_msg_id: storage_data})


async def rename_category(msg: Message, regexp_command: re.Match, state: FSMContext):
    category_id = int(regexp_command.group(1))
    await state.update_data({'category_id': category_id})
    await RenameCategoryState.waiting_for_new_name.set()
    await msg.answer('Введите новое имя категории:', reply_markup=keyboards.cancel_kb)


async def new_category(msg: Message, regexp_command: re.Match, state: FSMContext):
    grop_id = int(regexp_command.group(1))
    await state.update_data({'group_id': grop_id})
    await AddCategoryState.waiting_for_new_name.set()
    await msg.answer('Введите имя новой категории:', reply_markup=keyboards.cancel_kb)


async def add_category_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data['group_id']
    group = await db.get_category_group(group_id)
    storage_data = data.get(StorageKeys.last_category_msg_id, {})

    new_name = msg.text
    await db.save_category(new_name, group_id)
    await state.reset_state(with_data=False)
    await msg.answer(f'Категория добавлена в группу {group.name}!', reply_markup=keyboards.main_kb)

    if group_id in storage_data.keys():
        msg_id = storage_data[group_id]
        categories = await db.get_categories_for_group(group.id)
        resp = compose_categories(group, categories)
        await bot.edit_message_text(resp, chat_id=msg.chat.id, message_id=msg_id)


async def update_category_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data['category_id']
    category = await db.get_category(category_id)
    storage_data = data.get(StorageKeys.last_category_msg_id, {})

    new_name = msg.text
    await db.rename_category(category_id, new_name)
    await state.reset_state(with_data=False)
    await msg.answer('Категория переименована!', reply_markup=keyboards.main_kb)

    if category.group_id in storage_data.keys():
        msg_id = storage_data[category.group_id]
        group = await db.get_category_group(category.group_id)
        categories = await db.get_categories_for_group(group.id)
        resp = compose_categories(group, categories)
        await bot.edit_message_text(resp, chat_id=msg.chat.id, message_id=msg_id)
