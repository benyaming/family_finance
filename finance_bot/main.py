import asyncio
import os
import re
from typing import List

import betterlogging as logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.filters import RegexpCommandsFilter
from psycopg import AsyncConnection


from finance_bot.settings import env
from finance_bot.models import Category, Transaction
from finance_bot.misc import Misc
from finance_bot import db


class FilterMiddleware(BaseMiddleware):

    async def trigger(self, action, args):
        if action != 'pre_process_update':
            return

        update = args[0]
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        else:
            logging.warning(f'Unknown message type: {update}')
            raise CancelHandler()

        if user_id not in env.ADMITTED_USERS:
            logging.warning(f'Access denied: {update}')
            raise CancelHandler()


class CallbackPrefixes:
    select_amount = '0:'
    new_category = '1:'
    cancel = '2:'


async def on_start(_):
    session = await AsyncConnection.connect(env.DB_DSN)
    Misc.db_conn = session


# -------------------------------- STATES -------------------------------------
class RenameCategoryState(StatesGroup):
    waiting_for_new_name = State()


class AddCategoryState(StatesGroup):
    waiting_for_new_name = State()


# ---------------------------- CREATE GLOBALS ---------------------------------

logging.basic_colorized_config(level=logging.INFO)
bot = Bot(token=env.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(FilterMiddleware())


# --------------------------------- UTILS --------------------------------------
def compose_categories(categories: List[Category]) -> str:
    categories_lines = []
    for category in categories:
        line = f'<b>{category.name}</b>\n' \
               f'Переименовать: /rename_category_{category.id}'
        categories_lines.append(line)
    category_str = '\n-----------------------------------------------\n'.join(categories_lines)
    resp = f'Управление категориями:\n\n' \
           f'{category_str}\n' \
           f'-----------------------------------------------\n' \
           f'Добавить категорию: /new_category'
    return resp

# ------------------------------- HANDLERS -------------------------------------


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Добро пожаловать!', reply_markup=main_kb)


@dp.message_handler(text='Отмена', state='*')
async def handle_cancel(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer('Отменено', reply_markup=main_kb)


# @dp.message_handler(commands=['t'])
# async def t(m: types.Message):
#     kb = await get_category_menu()
#     await m.answer('test', reply_markup=kb)


@dp.message_handler(text_startswith='Категории')
async def handle_categories_menu(msg: types.Message, state: FSMContext):
    categories = await db.get_categories()
    resp = compose_categories(categories)
    sent_msg = await msg.answer(resp)

    await state.update_data({'last_categories_message': sent_msg.message_id})


@dp.message_handler(RegexpCommandsFilter(regexp_commands=[r'rename_category_([0-9]*)']))
async def handle_rename_category(msg: types.Message, regexp_command: re.Match, state: FSMContext):
    category_id = regexp_command.group(1)
    await state.update_data({'category_id': category_id})
    await RenameCategoryState.waiting_for_new_name.set()
    await msg.answer('Введите новое имя категории:', reply_markup=cancel_kb)


@dp.message_handler(RegexpCommandsFilter(regexp_commands=[r'new_category']))
async def handle_new_category(msg: types.Message):
    await AddCategoryState.waiting_for_new_name.set()
    await msg.answer('Введите имя новой категории:', reply_markup=cancel_kb)


@dp.message_handler(state=RenameCategoryState.waiting_for_new_name)
async def handle_new_category_name(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    category_id = data['category_id']
    msg_id = data.get('last_categories_message')

    new_name = msg.text
    await db.rename_category(category_id, new_name)
    await state.finish()
    await msg.answer('Категория переименована!', reply_markup=main_kb)

    if msg_id:
        categories = await db.get_categories()
        resp = compose_categories(categories)
        await bot.edit_message_text(resp, chat_id=msg.chat.id, message_id=msg_id)


@dp.message_handler(state=AddCategoryState.waiting_for_new_name)
async def handle_new_category_name(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get('last_categories_message')

    new_name = msg.text
    await db.save_category(new_name)
    await state.finish()
    await msg.answer('Категория добавлена!', reply_markup=main_kb)

    if msg_id:
        categories = await db.get_categories()
        resp = compose_categories(categories)
        await bot.edit_message_text(resp, chat_id=msg.chat.id, message_id=msg_id)


@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    try:
        raw_amount = float(message.text)
        amount = int(raw_amount * env.AMOUNT_PRECISION)
    except ValueError:
        return await message.answer('Неверный формат суммы')

    kb = await get_category_menu(amount)
    await message.answer(f'Сумма: {raw_amount}\n\n<i>Выберите категорию:</i>', reply_markup=kb)


@dp.callback_query_handler(text_startswith=CallbackPrefixes.select_amount)
async def handle_transaction(call: types.CallbackQuery):
    category_id, amount = call.data.split(':')[1:]
    category = await db.get_category(category_id)
    transaction = Transaction(amount=amount, category_id=category_id)
    await db.save_transaction(transaction)

    msg_text = f'<i>Трата успешно добавлена!</i>\n\n' \
               f'<b>Сумма:</b> {transaction.amount / env.AMOUNT_PRECISION:.2f}\n' \
               f'<b>Категория:</b> {category.name}\n' \
               f'<b>Дата:</b> {transaction.created_at.strftime("%d/%m/%Y")}'
    await call.message.edit_text(msg_text)

# -------------------------------------------------------------------------------- #


main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
main_kb.add('Категории', 'Подписки (скоро)')

cancel_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
cancel_kb.add('Отмена')


async def get_category_menu(amount: int) -> types.InlineKeyboardMarkup:
    categories = await db.get_categories()
    kb = types.InlineKeyboardMarkup()
    for category in categories:
        kb.add(types.InlineKeyboardButton(
            text=category.name,
            callback_data=f'{CallbackPrefixes.select_amount}{category.id}:{amount}'
        ))
    return kb


if __name__ == '__main__':
    if os.name == 'nt':
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
        
    executor.start_polling(dp, on_startup=on_start)
