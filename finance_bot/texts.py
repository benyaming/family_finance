from aiogram.types import BotCommand


class CallbackPrefixes:
    transaction_category_groups_requested = '0:'
    transaction_categories_requested = '1:'
    transaction_category_selected = '2:'

    management_categories_for_groups_requested = '3:'
    management_categories_move_to_another_group = '4:'

    management_groups_add_new_group = '5:'

    detailed_stats_for_group_requested = '6:'

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
    BotCommand('categories', 'Управление категориями и группами'),
    # BotCommand('subscriptions', 'Управление подписками'),
    BotCommand('stats', 'Статистика за текущий месяц')
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
msg_category_group_removed = 'Группа <b>{}</b> удалена.'
msg_group_name_already_exists = 'Группа с таким названием уже существует!'
msg_category_already_exists = 'Категория с таким названием уже существует!'
msg_cannot_remove_group_with_categories = 'Невозможно удалить группу с созданными категориями!'
msg_group_not_found = 'Группа не найдена!'
msg_input_spends_remind = 'Не забудьте ввести свои сегодняшние траты!'

cat_manage_title = 'Управление категориями группы'
cat_manage_add_cat = 'Добавить категорию'
cat_manage_edit_cat = 'Изменить имя категории'
cat_manage_move_cat = 'Перенести в другую группу'
cat_manage_group_is_empty = 'В этой группе пока нет категорий, ее можно безопасно удалить:'

transaction_manage_title = 'Трата успешно добавлена!'
transaction_manage_summ = 'Сумма:'
transaction_manage_category = 'Категория:'
transaction_manage_group = 'Группа категорий:'
transaction_manage_date = 'Дата:'

group_manage_edit_name = 'Изменить имя группы'

plot_spends_title = 'Траты за'
plot_in_category = 'в категории'

msg_cant_parse_stats_args = 'Не удалось распознать аргументы. Можно отправить номер месяца и/или год.'
msg_no_stats_for_month = 'За этот месяц не найдено трат!'
stats_details_button_prefix = 'Подробнее: '

month_names = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь',
}

