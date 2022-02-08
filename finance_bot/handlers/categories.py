import re
from typing import List

from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.utils.parts import safe_split_text

from finance_bot import db
from finance_bot.misc import bot
from finance_bot import keyboards as kb
from finance_bot.models import Category
from finance_bot.states import RenameCategoryState, AddCategoryState


async def categories_menu(msg: Message, state: FSMContext):
    categories = await db.get_all_categories()
    resp_parts = compose_categories(categories)
    sent_msgs = [await msg.answer(part) for part in resp_parts]
    await state.update_data({'last_categories_messages': [m.message_id for m in sent_msgs]})


async def rename_category(msg: Message, regexp_command: re.Match, state: FSMContext):
    category_id = regexp_command.group(1)
    await state.update_data({'category_id': category_id})
    await RenameCategoryState.waiting_for_new_name.set()
    await msg.answer('Введите новое имя категории:', reply_markup=kb.cancel_kb)


async def new_category(msg: Message):
    await AddCategoryState.waiting_for_new_name.set()
    await msg.answer('Введите имя новой категории:', reply_markup=kb.cancel_kb)


async def update_category_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data['category_id']
    msg_ids = data.get('last_categories_messages')

    new_name = msg.text
    await db.rename_category(category_id, new_name)
    await state.finish()
    await msg.answer('Категория переименована!', reply_markup=kb.main_kb)

    if msg_ids:
        categories = await db.get_all_categories()
        resp_parts = compose_categories(categories)
        for msg_id, part in zip(msg_ids, resp_parts):
            await bot.edit_message_text(part, chat_id=msg.chat.id, message_id=msg_id)


async def add_category_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    msg_ids = data.get('last_categories_messages')

    new_name = msg.text
    await db.save_category(new_name)
    await state.finish()
    await msg.answer('Категория добавлена!', reply_markup=kb.main_kb)

    if msg_ids:
        categories = await db.get_all_categories()
        resp_parts = compose_categories(categories)
        for msg_id, part in zip(msg_ids, resp_parts):
            await bot.edit_message_text(part, chat_id=msg.chat.id, message_id=msg_id)


def compose_categories(categories: List[Category]) -> List[str]:
    categories_lines = []
    for category in categories:
        line = f'<b>{category.name}</b>\n' \
               f'Переименовать: /rename_category_{category.id}'
        categories_lines.append(line)
    separator = '\n-----------------------------------------------\n'
    category_str = separator.join(categories_lines)
    resp = f'Управление категориями:\n\n' \
           f'{category_str}{separator}' \
           f'Добавить категорию: /new_category'

    resp_parts = safe_split_text(resp, split_separator=separator)
    return resp_parts
