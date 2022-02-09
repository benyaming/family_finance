from aiogram.types import BotCommand


class CallbackPrefixes:
    transaction_category_groups_requested = '0:'
    transaction_categories_requested = '1:'
    transaction_category_selected = '2:'

    management_categories_for_groups_requested = '3:'

    new_category = 'q:'
    cancel = 'z:'


class StorageKeys:
    last_category_msg_id = 'last_category_management_message:'


commands = [
    BotCommand('start', 'Перезагрузить'),
    BotCommand('categories', 'Управление категориями'),
    BotCommand('subscriptions', 'Управление подписками'),
]


button_categories = 'Категории'
button_other = 'Другое...'

button_back_to_category_groups = '🔙 Другая группа...'
button_category_groups = 'Группы категорий'
button_subscriptions = 'Подписки (скоро)'
button_cancel = 'Отмена'

message_select_category_group_for_manage = 'Выберите группу категорий для управления:'
