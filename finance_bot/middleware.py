import logging

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from finance_bot.settings import env


logger = logging.getLogger(__name__)


class SequrityMiddleware(BaseMiddleware):

    async def trigger(self, action, args):
        if action != 'pre_process_update':
            return

        update = args[0]
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        else:
            logger.warning(f'Unknown message type: {update}')
            raise CancelHandler()

        if user_id not in env.ADMITTED_USERS:
            logger.warning(f'Access denied: {update}')
            raise CancelHandler()
