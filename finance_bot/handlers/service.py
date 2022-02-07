from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from finance_bot.keyboards import main_kb


async def cmd_start(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Добро пожаловать!', reply_markup=main_kb)


async def handle_cancel(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer('Отменено', reply_markup=main_kb)
