from aiogram.types import ContentType
from aiogram.dispatcher.filters import RegexpCommandsFilter

from finance_bot import texts
from finance_bot import states
from finance_bot.misc import dp
from finance_bot.texts import CallbackPrefixes
from finance_bot.handlers import categories
from finance_bot.handlers import service
from finance_bot.handlers import transactions
from finance_bot.handlers import stats
from finance_bot.handlers import subscriptions


def register_handlers():
    dp.register_message_handler(service.cmd_start, commands=['start'])
    dp.register_message_handler(service.handle_cancel, text=texts.button_cancel, state='*')

    # Categories
    dp.register_message_handler(categories.prepare_groups_selection_menu, commands=['categories'], state='*')
    dp.register_message_handler(categories.rename_category, RegexpCommandsFilter(regexp_commands=[r'rename_cat_([0-9]*)']), state='*')
    dp.register_message_handler(categories.rename_group, RegexpCommandsFilter(regexp_commands=[r'rename_group_([0-9]*)']), state='*')
    dp.register_message_handler(categories.new_category, RegexpCommandsFilter(regexp_commands=[r'new_cat_([0-9]*)']), state='*')
    dp.register_message_handler(categories.prepare_change_group_menu, RegexpCommandsFilter(regexp_commands=[r'move_cat_([0-9]*)']), state='*')
    dp.register_message_handler(categories.remove_group, RegexpCommandsFilter(regexp_commands=[r'remove_group_([0-9]*)']), state='*')

    dp.register_message_handler(categories.prepare_groups_selection_menu, text=texts.button_categories)
    dp.register_message_handler(categories.update_category_name, state=states.RenameCategoryState.waiting_for_new_name)
    dp.register_message_handler(categories.update_group_name, state=states.RenameGroupState.waiting_for_new_name)
    dp.register_message_handler(categories.add_category_name, state=states.AddCategoryState.waiting_for_new_name)
    dp.register_message_handler(categories.handle_group_name, state=states.AddGroupState.waiting_for_new_name)
    dp.register_message_handler(categories.handle_group_limit, state=states.AddGroupState.waiting_for_limit)

    dp.register_callback_query_handler(categories.prepare_category_management_menu, text_startswith=CallbackPrefixes.management_categories_for_groups_requested)
    dp.register_callback_query_handler(categories.add_new_group, text_startswith=CallbackPrefixes.management_groups_add_new_group)
    dp.register_callback_query_handler(categories.change_group_for_category, text_startswith=CallbackPrefixes.management_categories_move_to_another_group)

    # Limits
    dp.register_message_handler(categories.get_limits_dashboard, commands=['limits'], state='*')
    dp.register_message_handler(categories.init_set_group_limit, RegexpCommandsFilter(regexp_commands=[r'set_limit_([0-9]*)']), state='*')
    dp.register_message_handler(categories.remove_group_limit, RegexpCommandsFilter(regexp_commands=[r'remove_limit_([0-9]*)']), state='*')
    dp.register_message_handler(categories.update_group_limit, state=states.SetLimitState.waiting_for_amount)

    # Subscriptions
    dp.register_message_handler(subscriptions.prepare_subscription_management_menu, commands=['subscriptions'])
    dp.register_message_handler(subscriptions.init_new_subscription, commands=['add_subscription'])
    dp.register_message_handler(subscriptions.handle_subscription_name, state=states.AddSubscriptionState.waiting_for_name)
    dp.register_message_handler(subscriptions.handle_subscription_day, state=states.AddSubscriptionState.waiting_for_date)
    dp.register_message_handler(subscriptions.handle_subscription_amount, state=states.AddSubscriptionState.waiting_for_amount)
    dp.register_message_handler(subscriptions.manage_subscription_menu, RegexpCommandsFilter(regexp_commands=[r'manage_subscription_([0-9]*)']), state='*')
    dp.register_callback_query_handler(subscriptions.init_category_selection_for_subscription, text_startswith=CallbackPrefixes.subscription_categories_requested)
    dp.register_callback_query_handler(subscriptions.init_category_group_selection_for_subscription, text_startswith=CallbackPrefixes.subscription_category_groups_requested)
    dp.register_callback_query_handler(subscriptions.create_subscription, text_startswith=CallbackPrefixes.subscription_category_selected)
    dp.register_callback_query_handler(subscriptions.remove_subscription, text_startswith=CallbackPrefixes.subscription_remove)
    dp.register_callback_query_handler(subscriptions.process_subscription, text_startswith=CallbackPrefixes.subscription_confirm)

    # Transactions
    dp.register_callback_query_handler(transactions.init_category_group_selection, text_startswith=CallbackPrefixes.transaction_category_groups_requested)
    dp.register_callback_query_handler(transactions.init_category_selection, text_startswith=CallbackPrefixes.transaction_categories_requested)
    dp.register_callback_query_handler(transactions.create_transaction, text_startswith=CallbackPrefixes.transaction_category_selected)

    # Stats
    dp.register_message_handler(stats.group_stats_for_month, commands=['stats'], state='*')
    dp.register_callback_query_handler(stats.category_stats_for_month, text_startswith=CallbackPrefixes.detailed_stats_for_group_requested, state='*')

    # This should be the last one
    dp.register_message_handler(transactions.init_transaction, content_types=ContentType.TEXT)
