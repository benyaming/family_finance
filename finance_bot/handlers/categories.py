import re
from typing import List

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from finance_bot import db
from finance_bot import texts
from finance_bot.misc import bot
from finance_bot import keyboards
from finance_bot.models import Category, CategoryGroup
from finance_bot.texts import StorageKeys
from finance_bot.states import RenameCategoryState, AddCategoryState, AddGroupState, \
    RenameGroupState


def compose_categories(group: CategoryGroup, categories: List[Category]) -> str:
    categories_lines = []
    for category in categories:
        line = f'<b>{category.name}</b>\n' \
               f'Изменить имя категории: /rename_cat_{category.id}\n' \
               f'Перенести в другую группу: /move_cat_{category.id}' \

        categories_lines.append(line)
    separator = '\n-----------------------------------------------\n'
    category_str = separator.join(categories_lines)
    resp = f'Управление категориями группы <b>{group.name}</b>:\n\n' \
           f'{category_str}{separator}' \
           f'Добавить категорию: /new_cat_{group.id}\n' \
           f'Изменить имя группы: /rename_group_{group.id}\n' \

    return resp


async def prepare_groups_selection_menu(msg: Message, state: FSMContext):
    await state.reset_state(with_data=False)
    category_groups = await db.get_category_groups(with_empty=True)
    kb = keyboards.get_category_group_options_for_management(category_groups)
    sent = await msg.reply(texts.message_select_category_group_for_manage, reply_markup=kb)
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
    resp = texts.message_select_group_to_change.format(category.name)
    sent = await msg.reply(resp, reply_markup=kb)
    await state.update_data({'category_to_move_id': category_id})
    await state.update_data({StorageKeys.last_select_group_menu_to_delete_msg_id: sent.message_id})


async def rename_category(msg: Message, regexp_command: re.Match, state: FSMContext):
    await state.reset_state(with_data=False)
    category_id = int(regexp_command.group(1))
    await state.update_data({'category_id': category_id})
    await RenameCategoryState.waiting_for_new_name.set()
    await msg.answer('Введите новое имя категории:', reply_markup=keyboards.cancel_kb)


async def rename_group(msg: Message, regexp_command: re.Match, state: FSMContext):
    await state.reset_state(with_data=False)
    group_id = int(regexp_command.group(1))
    await state.update_data({'group_id': group_id})
    await RenameGroupState.waiting_for_new_name.set()
    await msg.answer('Введите новое имя группы:', reply_markup=keyboards.cancel_kb)


async def new_category(msg: Message, regexp_command: re.Match, state: FSMContext):
    await state.reset_state(with_data=False)
    grop_id = int(regexp_command.group(1))
    await state.update_data({'group_id': grop_id})
    await AddCategoryState.waiting_for_new_name.set()
    await msg.answer('Введите имя новой категории:', reply_markup=keyboards.cancel_kb)


async def add_new_group(call: CallbackQuery):
    await call.answer()
    await AddGroupState.waiting_for_new_name.set()
    await bot.send_message(call.from_user.id, texts.message_input_new_group_name, reply_markup=keyboards.cancel_kb)


async def add_category_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data['group_id']
    group = await db.get_category_group(group_id)
    storage_data = data.get(StorageKeys.last_category_msg_id, {})

    new_name = msg.text
    await db.save_category(new_name, group_id)
    await state.reset_state(with_data=False)
    await msg.answer(f'Категория добавлена в группу {group.name}!')

    if group_id in storage_data.keys():
        msg_id = storage_data[group_id]
        categories = await db.get_categories_for_group(group.id)
        resp = compose_categories(group, categories)
        await bot.edit_message_text(resp, chat_id=msg.chat.id, message_id=msg_id)


async def add_group_name(msg: Message, state: FSMContext):
    new_name = msg.text
    await db.save_category_group(new_name)
    await msg.answer('Группа добавлена!')
    await state.reset_state(with_data=False)

    data = await state.get_data()
    if StorageKeys.last_groups_menu_msg_id in data.keys():
        msg_id = data[StorageKeys.last_groups_menu_msg_id]
        groups = await db.get_category_groups(with_empty=True)
        kb = keyboards.get_category_group_options_for_management(groups)
        await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg_id, reply_markup=kb)


async def update_category_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data['category_id']
    category = await db.get_category(category_id)
    storage_data = data.get(StorageKeys.last_category_msg_id, {})

    category.name = msg.text
    await db.update_category(category)
    await state.reset_state(with_data=False)
    await msg.answer('Категория переименована!', reply_markup=ReplyKeyboardRemove())

    if category.group_id in storage_data.keys():
        msg_id = storage_data[category.group_id]
        group = await db.get_category_group(category.group_id)
        categories = await db.get_categories_for_group(group.id)
        resp = compose_categories(group, categories)
        await bot.edit_message_text(resp, chat_id=msg.chat.id, message_id=msg_id)


async def update_group_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data['group_id']

    new_name = msg.text
    await db.rename_category_group(group_id, new_name)
    await state.reset_state(with_data=False)
    await msg.answer('Группа переименована!', reply_markup=ReplyKeyboardRemove())

    if StorageKeys.last_groups_menu_msg_id in data.keys():
        msg_id = data[StorageKeys.last_groups_menu_msg_id]
        groups = await db.get_category_groups(with_empty=True)
        kb = keyboards.get_category_group_options_for_management(groups)
        await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg_id, reply_markup=kb)


async def change_group_for_category(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()

    new_group_id = int(call.data.split(':')[1])
    category_id = data['category_to_move_id']
    category = await db.get_category(category_id)
    old_group_id = category.group_id
    category.group_id = new_group_id
    await db.update_category(category)

    group = await db.get_category_group(category.group_id)
    resp = texts.message_category_moved_success.format(category.name, group.name)
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
