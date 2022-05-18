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
    BotCommand('start', 'restart'),
    BotCommand('categories', 'Category and group management'),
    # BotCommand('subscriptions', 'Управление подписками'),
    BotCommand('stats', 'Statistics for the current month')
]


button_categories = 'Categories'
button_other = 'Other...'

button_add_group = '➕ Add category group'
button_back_to_category_groups = '🔙 Another group...'
button_category_groups = 'Category groups'
button_subscriptions = 'Subscriptions (coming soon)'
button_cancel = 'Cancel'

msg_welcome = 'Welcome!'
msg_cancel = 'Canceled.'

msg_select_category_group_for_manage = 'Select a category group to manage:'
msg_select_group_to_change = 'Choose which group to transfer the category to <b>{}</b>'
msg_input_name_for_new_category = 'Enter the name of the new category:'
msg_input_name_for_new_group = 'Enter the name of the new group:'
msg_input_name_for_specific_category = 'Enter a new category name <b>{}</b>:'
msg_input_name_for_specific_group = 'Enter a new group name <b>{}</b>:'
msg_category_add_success = 'Category <b>{}</b> added to group <b>{}</b>.'
msg_group_add_success = 'Group <b>{}</b> added.'
msg_category_rename_success = 'Category <b>{}</b> renamed.'
msg_category_move_success = 'Category <b>{}</b> moved to group <b>{}</b>.'
msg_group_rename_success = 'Group <b>{}</b> renamed.'
msg_incorrect_amount = 'Invalid amount format!'
msg_select_cat_for_transaction = 'Sum: {}\n\n<i>Select a category:</i>'
msg_category_group_removed = 'Group <b>{}</b> deleted.'
msg_group_name_already_exists = 'A group with the same name already exists!'
msg_category_already_exists = 'A category with that name already exists!'
msg_cannot_remove_group_with_categories = 'Unable to delete a group with created categories!'
msg_group_not_found = 'Group not found!'
msg_input_spends_remind = "Don't forget to enter your today's expenses!"

cat_manage_title = 'Group category management'
cat_manage_add_cat = 'Add category'
cat_manage_edit_cat = 'Change category name'
cat_manage_move_cat = 'Move to another group'
cat_manage_group_is_empty = 'There are no categories in this group yet, it can be safely deleted:'

transaction_manage_title = 'Waste added successfully!'
transaction_manage_summ = 'Sum:'
transaction_manage_category = 'Category:'
transaction_manage_group = 'Category group:'
transaction_manage_date = 'Date:'

group_manage_edit_name = 'Change group name'

plot_spends_title = 'Spending for'
plot_in_category = 'in category'

msg_cant_parse_stats_args = 'Failed to recognize arguments. You can send the number of the month and/or year.'
msg_no_stats_for_month = 'No spending found this month!'
stats_details_button_prefix = 'More: '

month_names = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December',
}

