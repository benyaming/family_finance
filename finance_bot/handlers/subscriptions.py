from datetime import date, timedelta
from typing import List

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from finance_bot import db
from finance_bot import texts
from finance_bot import keyboards
from finance_bot.models import Subscription
from finance_bot.states import AddSubscriptionState
from finance_bot.texts import StorageKeys


def get_nex_payment_date(day: int) -> date:
    payment_date = date.today()
    while payment_date.day != day:
        payment_date += timedelta(days=1)
    return payment_date


def compose_subscriptions(subscriptions: List[Subscription]) -> str:
    if not subscriptions:
        return texts.msg_no_subscriptions_found

    sub_lines = []
    separator = '\n-----------------------------------------------\n'

    for sub in subscriptions:
        next_payment_date = get_nex_payment_date(sub.day_of_month)
        sub_line = f'<b>{sub.group_name} / {sub.category_name} / {sub.name}</b>\n' \
                   f'<b>{texts.sub_manage_date}</b> {next_payment_date.isoformat()}\n' \
                   f'<b>{texts.sub_manage_remove}</b> /remove_subscription_{sub.id}'
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
    await state.update_data({StorageKeys.new_sub_amount: msg.text})
    await AddSubscriptionState.next()
    await msg.reply(texts.msg_new_sub_input_day, reply_markup=keyboards.cancel_kb)


async def handle_subscription_day(msg: Message, state: FSMContext):
    await state.update_data({StorageKeys.new_sub_day: msg.text})
    await AddSubscriptionState.next()
    groups = await db.get_category_groups()

    await msg.reply(
        texts.msg_new_sub_input_category,
        reply_markup=keyboards.get_category_group_options_for_subscription(groups)
    )


# todo: transactions group navigation
# todo: remove cancel kb in the last question
# todo: numbers and dates validators
# todo: save subscription
# todo: show amount in composed menu
# todo: subscription task execution
# todo: cancel subscription
# todo: crud for subscriptions
