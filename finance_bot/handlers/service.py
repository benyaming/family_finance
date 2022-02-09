from aiogram.dispatcher import FSMContext
from aiogram.types import Message


async def cmd_start(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Добро пожаловать!')


async def handle_cancel(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer('Отменено')
