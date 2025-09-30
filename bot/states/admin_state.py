from aiogram.fsm.state import State, StatesGroup

class AdminState(StatesGroup):
    delete_user_id = State()
    add_user_id = State()