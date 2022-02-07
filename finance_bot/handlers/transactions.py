from aiogram.types import Message, CallbackQuery

from finance_bot import db
from finance_bot import keyboards
from finance_bot.settings import env
from finance_bot.models import Transaction


async def create_transaction(message: Message):
    try:
        raw_amount = float(message.text)
        amount = int(raw_amount * env.AMOUNT_PRECISION)
    except ValueError:
        return await message.answer('Неверный формат суммы')

    kb = await keyboards.get_category_menu(amount)
    await message.answer(f'Сумма: {raw_amount}\n\n<i>Выберите категорию:</i>', reply_markup=kb)


async def select_transaction_category(call: CallbackQuery):
    category_id, amount = call.data.split(':')[1:]
    category = await db.get_category(category_id)
    transaction = Transaction(amount=amount, category_id=category_id)
    await db.save_transaction(transaction)

    msg_text = f'<i>Трата успешно добавлена!</i>\n\n' \
               f'<b>Сумма:</b> {transaction.amount / env.AMOUNT_PRECISION:.2f}\n' \
               f'<b>Категория:</b> {category.name}\n' \
               f'<b>Дата:</b> {transaction.created_at.strftime("%d/%m/%Y")}'
    await call.message.edit_text(msg_text)
