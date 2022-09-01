import calendar
import re
from datetime import date, timedelta
from typing import List

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from finance_bot import db
from finance_bot import texts
from finance_bot import keyboards
from finance_bot.misc import bot
from finance_bot.models import Subscription, Transaction
from finance_bot.settings import env
from finance_bot.states import AddSubscriptionState
from finance_bot.texts import StorageKeys


def get_next_month() -> date:
    day = date.today()
    current_month = day.month
    while day.month == current_month:
        day += timedelta(days=1)

    return day


def get_next_payment_date(day: int) -> date:
    today = date.today()

    if day < today.day:
        tdate = get_next_month()
    else:
        tdate = today

    current_month_length = calendar.monthrange(tdate.year, tdate.month)[1]

    if day > current_month_length:
        day = current_month_length

    return date(tdate.year, tdate.month, day)


def compose_subscriptions(subscriptions: List[Subscription]) -> str:
    if not subscriptions:
        return texts.msg_no_subscriptions_found

    sub_lines = []
    separator = '\n-----------------------------------------------\n'

    for sub in subscriptions:
        next_payment_date = get_next_payment_date(sub.day_of_month)
        sub_line = f'<b>{sub.group_name} / {sub.category_name} / {sub.name}</b>\n' \
                   f'<b>{texts.new_sub_manage_amount}</b> {env.CURRENCY_CHAR}{sub.amount}\n' \
                   f'<b>{texts.sub_manage_date}</b> {next_payment_date.isoformat()}\n' \
                   f'<b>{texts.sub_manage_manage}</b> /manage_subscription_{sub.id}'
        sub_lines.append(sub_line)

    lines = separator.join(sub_lines)
    resp = f'{texts.sub_manage_title}\n\n' \
           f'{lines}\n\n' \
           f'{texts.sub_manage_add_new} /add_subscription'
    return resp


async def prepare_subscription_management_menu(msg: Message, state: FSMContext):
    subscriptions = await db.get_subscriptions()
    resp = compose_subscriptions(subscriptions)
    sent = await msg.reply(resp)
    await state.update_data({StorageKeys.last_subscription_menu_msg_id: sent.message_id})


async def init_new_subscription(msg: Message):
    await AddSubscriptionState.waiting_for_name.set()
    await msg.reply(texts.msg_new_sub_input_name, reply_markup=keyboards.cancel_kb)


async def handle_subscription_name(msg: Message, state: FSMContext):
    await state.update_data({StorageKeys.new_sub_name: msg.text})
    await AddSubscriptionState.next()
    await msg.reply(texts.msg_new_sub_input_amount, reply_markup=keyboards.cancel_kb)


async def handle_subscription_amount(msg: Message, state: FSMContext):
    try:
        amount = int(msg.text)
    except ValueError:
        return await msg.answer(texts.new_sub_incorrect_amount, reply_markup=keyboards.cancel_kb)

    await state.update_data({StorageKeys.new_sub_amount: amount})
    await AddSubscriptionState.next()
    await msg.reply(texts.msg_new_sub_input_day, reply_markup=keyboards.cancel_kb)


async def handle_subscription_day(msg: Message, state: FSMContext):
    try:
        day = int(msg.text)
        assert 0 < day < 32
    except (ValueError, AssertionError):
        return await msg.answer(texts.new_sub_incorrect_day, reply_markup=keyboards.cancel_kb)

    await state.update_data({StorageKeys.new_sub_day: day})
    await AddSubscriptionState.next()
    groups = await db.get_category_groups()

    await msg.reply(
        texts.msg_new_sub_input_category,
        reply_markup=keyboards.get_category_group_options_for_subscription(groups)
    )


async def init_category_selection_for_subscription(call: CallbackQuery):
    await call.answer()
    group_id = int(call.data.split(':')[1])
    categories = await db.get_categories_for_group(group_id)
    kb = keyboards.get_category_options_for_subscription(categories)
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)


async def init_category_group_selection_for_subscription(call: CallbackQuery):
    await call.answer()
    groups = await db.get_category_groups()
    kb = keyboards.get_category_group_options_for_subscription(groups)
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)


async def create_subscription(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    subscription_category_id = int(call.data.split(':')[1])

    subscription_name = data.get(StorageKeys.new_sub_name)
    subscription_day = data.get(StorageKeys.new_sub_day)
    subscription_amount = data.get(StorageKeys.new_sub_amount)

    subscription = Subscription(
        name=subscription_name,
        amount=subscription_amount,
        day_of_month=subscription_day,
        category_id=subscription_category_id,
        user_id=call.from_user.id
    )
    await db.save_subscription(subscription)
    await bot.edit_message_text(
        text=texts.new_sub_manage_done.format(subscription_name),
        chat_id=call.from_user.id,
        message_id=call.message.message_id
    )


async def manage_subscription_menu(msg: Message, regexp_command: re.Match):
    subscription_id = int(regexp_command.group(1))

    try:
        subscription = await db.get_subscription(subscription_id)
    except ValueError:
        return await msg.reply(texts.sub_not_found)
    next_payment_date = get_next_payment_date(subscription.day_of_month)

    resp = f'<b>{subscription.group_name} / {subscription.category_name} / {subscription.name}</b>\n\n' \
           f'<b>{texts.new_sub_manage_amount}</b> {env.CURRENCY_CHAR}{subscription.amount}\n' \
           f'<b>{texts.sub_manage_date}</b> {next_payment_date.isoformat()}\n'
    kb = keyboards.get_subscription_management_kb(subscription_id)
    await msg.reply(resp, reply_markup=kb)


async def remove_subscription(call: CallbackQuery):
    await call.answer()
    subscription_id = int(call.data.split(':')[1])
    await db.remove_subscription(subscription_id)
    await bot.send_message(call.from_user.id, texts.sub_deleted)


async def process_subscription(call: CallbackQuery):
    await call.answer()
    subscription_id = int(call.data.split(':')[1])
    subscription = await db.get_subscription(subscription_id)
    transaction = Transaction(
        amount=subscription.amount * env.AMOUNT_PRECISION,
        category_id=subscription.category_id
    )
    await db.save_transaction(transaction)

    resp = f'<i>{texts.transaction_manage_title}</i>\n\n' \
           f'<b>{texts.transaction_manage_summ}</b> {subscription.amount}\n' \
           f'<b>{texts.transaction_manage_category}</b> {subscription.category_name}\n' \
           f'<b>{texts.transaction_manage_group}</b> {subscription.group_name}\n' \
           f'<b>{texts.transaction_manage_date}</b> {transaction.created_at.strftime("%d/%m/%Y")}'

    await bot.edit_message_text(
        text=resp,
        chat_id=call.from_user.id,
        message_id=call.message.message_id
    )

# todo: edit subscription name/date/amount/category
