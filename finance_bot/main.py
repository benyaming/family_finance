import asyncio
import os

import betterlogging as logging
from aiogram import Dispatcher, executor
from psycopg import AsyncConnection

from finance_bot.periodic_jobs.reminder import remind_to_input_spends
from finance_bot.periodic_jobs.subscription_manager import process_subscriptions
from finance_bot.settings import env
from finance_bot.misc import dp, bot, scheduler, reminder_trigger, subscription_trigger
from finance_bot.texts import commands
from finance_bot.handlers import register_handlers
from finance_bot.db import init_db


logging.basic_colorized_config(level=logging.DEBUG)
logger = logging.getLogger(__file__)


async def on_start(dp_: Dispatcher):
    db_conn = await AsyncConnection.connect(env.DB_DSN)
    dp_['db_conn'] = db_conn

    await bot.set_my_commands(commands)

    logger.info('Initializing database...')
    await init_db()
    logger.info('...Done.')


if __name__ == '__main__':
    if os.name == 'nt':
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    register_handlers()

    if env.IS_REMINDER_ENABLED:
        scheduler.add_job(remind_to_input_spends, trigger=reminder_trigger)
    scheduler.add_job(process_subscriptions, trigger=subscription_trigger)

    scheduler.start()
    executor.start_polling(dp, on_startup=on_start)
