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
    category_id = 'category_id'
    category_to_move_id = 'category_to_move_id'
    group_id = 'group_id'


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

msg_welcome = 'Добро пожаловать!'
msg_cancel = 'Отменено.'

msg_select_category_group_for_manage = 'Выберите группу категорий для управления:'
msg_select_group_to_change = 'Выберите, в какую группу перенести категорию <b>{}</b>'
msg_input_name_for_new_category = 'Введите название новой категории:'
msg_input_name_for_new_group = 'Введите название новой группы:'
msg_input_name_for_specific_category = 'Введите новое название категории <b>{}</b>:'
msg_input_name_for_specific_group = 'Введите новое название группы <b>{}</b>:'
msg_category_add_success = 'Категория <b>{}</b> добавлена в группу <b>{}</b>.'
msg_group_add_success = 'Группа <b>{}</b> добавлена.'
msg_category_rename_success = 'Категория <b>{}</b> переименована.'
msg_category_move_success = 'Категория <b>{}</b> перемещена в группу <b>{}</b>.'
msg_group_rename_success = 'Группа <b>{}</b> переименована.'
msg_incorrect_amount = 'Неверный формат суммы'
msg_select_cat_for_transaction = 'Сумма: {}\n\n<i>Выберите категорию:</i>'

cat_manage_title = 'Управление категориями группы'
cat_manage_add_cat = 'Добавить категорию'
cat_manage_edit_cat = 'Изменить имя категории'
cat_manage_move_cat = 'Перенести в другую группу'

transaction_manage_title = 'Трата успешно добавлена!'
transaction_manage_summ = 'Сумма:'
transaction_manage_category = 'Категория:'
transaction_manage_group = 'Группа категорий:'
transaction_manage_date = 'Дата:'


group_manage_edit_name = 'Изменить имя группы'

