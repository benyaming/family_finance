from aiogram.dispatcher.filters.state import StatesGroup, State


class RenameCategoryState(StatesGroup):
    waiting_for_new_name = State()


class AddCategoryState(StatesGroup):
    waiting_for_new_name = State()
