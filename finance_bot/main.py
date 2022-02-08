import asyncio
import os

import betterlogging as logging
from aiogram import Dispatcher, executor
from psycopg import AsyncConnection


from finance_bot.settings import env
from finance_bot.misc import dp, bot
from finance_bot.texts import commands
from finance_bot.handlers import register_handlers


logging.basic_colorized_config(level=logging.INFO)


async def on_start(dp_: Dispatcher):
    db_conn = await AsyncConnection.connect(env.DB_DSN)
    dp_['db_conn'] = db_conn

    await bot.set_my_commands(commands)


if __name__ == '__main__':
    if os.name == 'nt':
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    register_handlers()
    executor.start_polling(dp, on_startup=on_start)
