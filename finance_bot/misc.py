from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from finance_bot.settings import env
from finance_bot.middleware import SequrityMiddleware


bot = Bot(token=env.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(SequrityMiddleware())
