from finance_bot import texts

from finance_bot.settings import env
from finance_bot.misc import bot


async def remind_to_input_spends():
    for user in env.ADMITTED_USERS:
        await bot.send_message(user, texts.msg_input_spends_remind, disable_notification=True)
