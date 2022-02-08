from aiogram.types import BotCommand


class CallbackPrefixes:
    category_groups_requested = '0:'
    categories_requested = '1:'
    category_selected = '2:'

    new_category = 'q:'
    cancel = 'z:'


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
