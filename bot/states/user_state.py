from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    in_scenario = State()
    waiting_answer = State()
    waiting_text_input = State()
    waiting_branch = State()
    waiting_survey = State()