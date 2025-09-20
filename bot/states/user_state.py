from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    in_scenario = State()
    waiting_answer = State()