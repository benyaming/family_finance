from aiogram.types import Message, CallbackQuery

from finance_bot import db
from finance_bot import texts
from finance_bot import keyboards
from finance_bot.settings import env
from finance_bot.models import Transaction
from finance_bot.misc import bot


async def init_transaction(message: Message):
    try:
        raw_amount = float(message.text)
        amount = int(raw_amount * env.AMOUNT_PRECISION)
    except ValueError:
        return await message.answer(texts.msg_incorrect_amount)

    kb = await keyboards.get_top_category_options(amount)
    await message.answer(texts.msg_select_cat_for_transaction.format(raw_amount), reply_markup=kb)


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
    group = await db.get_category_group(category.group_id)
    transaction = Transaction(amount=amount, category_id=category_id)
    await db.save_transaction(transaction)

    if group.limit:
        limit = await db.get_limit_for_group(group.id)

        if limit.usage_percentage < 70:
            indicator = '🟢'
        elif limit.usage_percentage < 100:
            indicator = '🟡'
        else:
            indicator = '🔴'

        group_str = f'\n{indicator} <b>{limit.group_name}</b>\n' \
                    f'{texts.limits_spent} {limit.spent}{env.CURRENCY_CHAR} / ' \
                    f'{limit.limit}{env.CURRENCY_CHAR} (<b>{limit.usage_percentage}%</b>)\n' \
                    f'{texts.limits_rest} {limit.rest if limit.rest > 0 else 0}{env.CURRENCY_CHAR}\n\n'
    else:
        group_str = f'<b>{texts.transaction_manage_group}</b> {group.name}\n'

    msg_text = f'<i>{texts.transaction_manage_title}</i>\n\n' \
               f'<b>{texts.transaction_manage_summ}</b> {transaction.amount / env.AMOUNT_PRECISION:.2f}\n' \
               f'<b>{texts.transaction_manage_category}</b> {category.name}\n' \
               f'{group_str}' \
               f'<b>{texts.transaction_manage_date}</b> {transaction.created_at.strftime("%d/%m/%Y")}'
    await call.message.edit_text(msg_text)
