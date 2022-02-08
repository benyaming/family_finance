from aiogram.types import ContentType
from aiogram.dispatcher.filters import RegexpCommandsFilter

from finance_bot import texts
from finance_bot import states
from finance_bot.misc import dp
from finance_bot.texts import CallbackPrefixes
from finance_bot.handlers import categories
from finance_bot.handlers import category_groups
from finance_bot.handlers import service
from finance_bot.handlers import transactions


def register_handlers():
    dp.register_message_handler(service.cmd_start, commands=['start'])
    dp.register_message_handler(service.handle_cancel, text=texts.button_cancel, state='*')

    # Categories
    dp.register_message_handler(categories.categories_menu, text=texts.button_categories)
    dp.register_message_handler(categories.categories_menu, commands=['categories'])
    dp.register_message_handler(categories.rename_category, RegexpCommandsFilter(regexp_commands=[r'rename_category_([0-9]*)']))
    dp.register_message_handler(categories.new_category, RegexpCommandsFilter(regexp_commands=[r'new_category']))
    dp.register_message_handler(categories.rename_category, state=states.RenameCategoryState.waiting_for_new_name)
    dp.register_message_handler(categories.add_category_name, state=states.AddCategoryState.waiting_for_new_name)

    # Category groups

    # Transactions
    dp.register_message_handler(transactions.init_transaction, content_types=ContentType.TEXT)
    dp.register_callback_query_handler(transactions.init_category_group_selection, text_startswith=CallbackPrefixes.category_groups_requested)
    dp.register_callback_query_handler(transactions.init_category_selection , text_startswith=CallbackPrefixes.categories_requested)
    dp.register_callback_query_handler(transactions.create_transaction, text_startswith=CallbackPrefixes.category_selected)
