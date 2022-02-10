from aiogram.types import BotCommand


class CallbackPrefixes:
    transaction_category_groups_requested = '0:'
    transaction_categories_requested = '1:'
    transaction_category_selected = '2:'

    management_categories_for_groups_requested = '3:'
    management_categories_move_to_another_group = '4:'

    management_groups_add_new_group = '5:'

    new_category = 'q:'
    cancel = 'z:'


class StorageKeys:
    last_category_msg_id = 'last_category_management_message:'
    last_groups_menu_msg_id = 'last_groups_menu_msg_id'
    last_select_group_menu_to_delete_msg_id = 'last_select_group_menu_to_delete_msg_id'


commands = [
    BotCommand('start', 'Перезагрузить'),
    BotCommand('categories', 'Управление категориями'),
    BotCommand('subscriptions', 'Управление подписками'),
]


button_categories = 'Категории'
button_other = 'Другое...'

button_add_group = '➕ Добавить группу категорий'
button_back_to_category_groups = '🔙 Другая группа...'
button_category_groups = 'Группы категорий'
button_subscriptions = 'Подписки (скоро)'
button_cancel = 'Отмена'

message_select_category_group_for_manage = 'Выберите группу категорий для управления:'
message_input_new_group_name = 'Введите название новой группы категорий:'
message_select_group_to_change = 'Выберите, в какую группу перенести категорию <b>{}</b>'
message_category_moved_success = 'Категория <b>{}</b> перенесена в группу <b>{}</b>'
