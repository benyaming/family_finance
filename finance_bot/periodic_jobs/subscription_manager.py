import logging

from finance_bot.models import Subscription
from finance_bot import db
from finance_bot import texts
from finance_bot.misc import bot
from finance_bot import keyboards


logger = logging.getLogger(__name__)


async def process_subscriptions():
    subscriptions = await db.get_subscriptions_for_today()
    logger.info(f'found {len(subscriptions)} subscriptions')
    for subscription in subscriptions:
        logger.info(f'processing subscription: {subscription}')
        await execute_subscription(subscription)


async def execute_subscription(subscription: Subscription):
    resp = f'<b>{texts.sub_process_title}: {subscription.name}</b>\n\n' \
           f'<b>{texts.transaction_manage_summ}</b> {subscription.amount}\n' \
           f'<b>{texts.transaction_manage_category}</b> {subscription.category_name}\n' \
           f'<b>{texts.transaction_manage_group}</b> {subscription.group_name}\n\n' \
           f'<i>{texts.sub_confirm_note}</i>'

    kb = keyboards.get_confirm_subscription_kb(subscription.id)
    await bot.send_message(subscription.user_id, resp, reply_markup=kb)
