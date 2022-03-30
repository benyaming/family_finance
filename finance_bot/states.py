from aiogram.dispatcher.filters.state import StatesGroup, State


class RenameCategoryState(StatesGroup):
    waiting_for_new_name = State()


class RenameGroupState(StatesGroup):
    waiting_for_new_name = State()


class AddCategoryState(StatesGroup):
    waiting_for_new_name = State()


class AddGroupState(StatesGroup):
    waiting_for_new_name = State()


class AddSubscriptionState(StatesGroup):
    waiting_for_name = State()
    waiting_for_amount = State()
    waiting_for_date = State()
