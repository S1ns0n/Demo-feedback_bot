from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.utils import keyboard

from bot.keyboards.menu_keyboards import create_menu_scenarios_list_keyboard, go_to_menu_keyboard
from bot.utils.scenario_loader import get_available_scenarios
from bot.utils.scenario_loader import load_scenario
from bot.handlers.scenario_handler import send_scenario_step
from bot.states.user_state import UserState
from bot.config import IMAGE_DIR

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    """Команда начала работы с ботом"""
    welcome_text = ("Здравствуйте!\n"
                    "Мы рады приветствовать вас в нашем боте!\n"
                    "Здесь вы можете посмотреть общую программу курса и пройти некоторые из её дней:\n"
                    " • Чтобы посмотреть программу, зайдите в меню и выберите пункт “Содержание программы”;\n"
                    " • Чтобы пройти демонстрационный день, зайдите в меню и выберите любой интересующий вас день из предложенных. В любой момент вы можете вернуться к меню и переключиться на другой день, или вновь вернуться к содержанию.\n\n"
                    )




    await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile(f"{IMAGE_DIR}/1_hello.PNG"),
                         caption=welcome_text,
                         parse_mode=ParseMode.HTML,
                         reply_markup=go_to_menu_keyboard())


@router.callback_query(F.data == "go_to_menu")
async def go_to_menu_callback(callback: CallbackQuery, bot: Bot):
    try:
        await bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None)
    except:
        pass
    await cmd_start_scenario(callback.message, bot)

@router.message(Command("menu"))
async def cmd_start_scenario(message: Message, bot: Bot):
    """Выбор сценария из списка"""
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id-1,
            reply_markup=None)
    except:
        pass

    keyboard = create_menu_scenarios_list_keyboard()
    await message.answer("Меню:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("start_scenario_"))
async def handle_scenario_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора сценария"""
    scenario_name = callback.data.replace("start_scenario_", "")

    scenario = load_scenario(scenario_name)

    if not scenario:
        await callback.answer("❌ Сценарий не найден или поврежден", show_alert=True)
        return

    # Запускаем выбранный сценарий
    await state.set_state(UserState.in_scenario)
    await state.update_data(
        scenario=scenario,
        current_step=0
    )

    await callback.message.edit_reply_markup(reply_markup=None)

    await send_scenario_step(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "refresh_scenarios")
async def handle_refresh_scenarios(callback: CallbackQuery):
    """Обновление списка сценариев"""
    keyboard = create_menu_scenarios_list_keyboard()
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer("🔄 Список обновлен")

@router.callback_query(F.data == "programm_list")
async def handle_programm_list(callback: CallbackQuery, bot: Bot):
    """Отправляет программу в текстовом формате"""
    try:
        await bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None)
    except:
        pass
    program_text = ("Содержание программы:\n\n"
                    " • <b>День 1:</b> <u>общая информация</u> о программе и работе бота;\n\n"
                    " • <b>Дни 2/20:</b> входное и выходное <u>тестирование;</u>\n\n"
                    " • <b>Дни 3-6:</b> <u>типы слушания</u> — как не упускать важную информацию, понимать потребности и эмоции коллег, развивать навыки поддержки для создания доверительной атмосферы и повышения сплоченности команды;\n\n"
                    " • <b>Дни 7-8:</b> <u>введение в контекст</u> и прояснение информации — как говорить с клиентом/ коллегой/ тимлидом/ проджектом/ на одном языке, договариваться об оптимальных условиях, выстраивать диалог без недопониманий и тысячи дополнительных вопросов, увеличивая скорость закрытия задач;\n\n"
                    " • <b>Дни 9-12:</b> как <u>просить</u>, <u>отказывать</u> и <u>реагировать на критику</u> — "
                    "\n   • как делать правильный запрос для любой цели, так, чтобы вам помогли,"
                    "\n   • как выражать свою точку зрения, корректно отказываться от задач, которые не соответствуют профессиональным компетенциям или рабочим приоритетам, сохраняя репутацию и хорошие отношения,"
                    "\n   • как конструктивно выйти из ситуации, где вас критикуют;\n\n"
                    " • <b>Дни 13-19:</b> как эффективно давать обратную связь."
                    )

    await bot.send_message(chat_id=callback.message.chat.id,
                           text=program_text,
                           parse_mode=ParseMode.HTML, reply_markup=go_to_menu_keyboard())

    await callback.answer()


@router.callback_query(F.data.in_(["no_scenarios", "error_scenarios"]))
async def handle_scenario_errors(callback: CallbackQuery):
    """Обработка ошибок сценариев"""
    await callback.answer("❌ Нет доступных сценариев или произошла ошибка", show_alert=True)
