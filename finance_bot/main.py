import asyncio
import os

import betterlogging as logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
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


# ---------------------------- CREATE GLOVBALS ---------------------------------

logging.basic_colorized_config(level=logging.INFO)
bot = Bot(token=env.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(FilterMiddleware())

# ---------------------------- HANDLERS ----------------------------------------


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer('Добро пожаловать!\nВвод трат в формате:\n\n{сумма}')


# @dp.message_handler(commands=['t'])
# async def t(m: types.Message):
#     kb = await get_category_menu()
#     await m.answer('test', reply_markup=kb)


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


def get_main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    kb.add('Добавить трату', 'Управление категориями')
    return kb


async def get_category_menu(amount: int) -> types.InlineKeyboardMarkup:
    categories = await db.get_categories()
    kb = types.InlineKeyboardMarkup()
    for category in categories:
        kb.add(types.InlineKeyboardButton(
            text=category.name,
            callback_data=f'{CallbackPrefixes.select_amount}{category.id}:{amount}'
        ))
    kb.add(types.InlineKeyboardButton(
        text='➕ Добавить категорию',
        callback_data=f'{CallbackPrefixes.new_category}{amount}'
    ))

    return kb


if __name__ == '__main__':
    if os.name == 'nt':
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
        
    executor.start_polling(dp, on_startup=on_start)
