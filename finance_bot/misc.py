from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from finance_bot.settings import env
from finance_bot.middleware import SequrityMiddleware


bot = Bot(token=env.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(SequrityMiddleware())

scheduler = AsyncIOScheduler()
subscriptions_trigger = CronTrigger(hour=20, minute=0)
reminder_trigger = CronTrigger(hour=21, minute=00)
