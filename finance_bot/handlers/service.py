from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from finance_bot import texts


async def cmd_start(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(texts.msg_welcome, reply_markup=ReplyKeyboardRemove())


async def handle_cancel(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer(texts.msg_cancel, reply_markup=ReplyKeyboardRemove())
