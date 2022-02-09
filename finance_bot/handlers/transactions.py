from aiogram.types import Message, CallbackQuery

from finance_bot import db
from finance_bot import keyboards
from finance_bot.settings import env
from finance_bot.models import Transaction
from finance_bot.misc import bot


async def init_transaction(message: Message):
    try:
        raw_amount = float(message.text)
        amount = int(raw_amount * env.AMOUNT_PRECISION)
    except ValueError:
        return await message.answer('Неверный формат суммы')

    kb = await keyboards.get_top_category_options(amount)
    await message.answer(f'Сумма: {raw_amount}\n\n<i>Выберите категорию:</i>', reply_markup=kb)


async def init_category_group_selection(call: CallbackQuery):
    await call.answer()
    amount = int(call.data.split(':')[1])
    groups = await db.get_category_groups()
    kb = keyboards.get_category_group_options_for_transaction(groups, amount)
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)


async def init_category_selection(call: CallbackQuery):
    await call.answer()
    group_id, amount = call.data.split(':')[1:]
    categories = await db.get_categories_for_group(group_id)
    kb = keyboards.get_category_options(categories, amount)
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)


async def create_transaction(call: CallbackQuery):
    await call.answer()
    category_id, amount = call.data.split(':')[1:]
    category = await db.get_category(category_id)
    transaction = Transaction(amount=amount, category_id=category_id)
    await db.save_transaction(transaction)

    msg_text = f'<i>Трата успешно добавлена!</i>\n\n' \
               f'<b>Сумма:</b> {transaction.amount / env.AMOUNT_PRECISION:.2f}\n' \
               f'<b>Категория:</b> {category.name}\n' \
               f'<b>Дата:</b> {transaction.created_at.strftime("%d/%m/%Y")}'
    await call.message.edit_text(msg_text)
