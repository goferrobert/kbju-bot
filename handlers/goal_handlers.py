from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
import logging

from states.fsm_states import GoalStates
from utils.texts import get_goal_request, get_kbju_explanation
from utils.buttons import get_goal_keyboard, get_main_menu_inline_keyboard
from crud.user_crud import get_user, user_exists, update_user
from models.database import SessionLocal
from utils.calculations import calculate_bodyfat, calculate_kbju
from crud.record_crud import get_latest_record

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

async def start_goal_change(message: types.Message, state: FSMContext):
    """Начать изменение цели"""
    logging.info(f"start_goal_change: user={message.from_user.id}")
    db = SessionLocal()
    user = get_user(db, message.from_user.id)
    if not user:
        await message.answer("❌ Сначала пройдите анкету! Используйте /start")
        return
    
    await message.answer("🎯 Выберите новую цель:", reply_markup=get_goal_keyboard())
    await GoalStates.goal.set()
    db.close()

async def process_goal_change_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработать изменение цели"""
    await callback.answer()
    
    goal = callback.data.split('_')[1]  # goal_healthy -> healthy
    goal_names = {
        'healthy': 'Здоровое тело',
        'athletic': 'Спортивное тело',
        'lean': 'Сухое тело'
    }
    
    goal_text = goal_names.get(goal, goal)
    
    # Обновляем сообщение с выбором
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ Выбрано: {goal_text}"
    )
    
    db = SessionLocal()
    user = get_user(db, callback.from_user.id)
    latest_record = get_latest_record(db, callback.from_user.id)
    db.close()
    
    if latest_record:
        user_data = {
            'sex': user.sex,
            'height': latest_record.height,
            'weight': latest_record.weight,
            'waist': latest_record.waist,
            'neck': latest_record.neck,
            'hip': latest_record.hip,
            'steps': latest_record.steps,
            'sport_type': latest_record.sport_type,
            'sport_freq': latest_record.sport_freq,
            'goal': goal
        }
        from utils.calculations import calculate_step_multiplier
        step_multiplier = calculate_step_multiplier(user_data['steps'])
        user_data['step_multiplier'] = step_multiplier
        bodyfat = calculate_bodyfat(user_data)
        kbju = calculate_kbju(user_data, bodyfat)
        await callback.message.answer(
            f"✅ Цель изменена на: {goal_text}"
        )
        await callback.message.answer(
            get_kbju_explanation(goal, kbju),
            parse_mode='Markdown'
        )
    else:
        await callback.message.answer(
            f"✅ Цель изменена на: {goal_text}\n\n📝 Сделайте замеры для расчета новых КБЖУ"
        )
    await callback.message.answer("🏠 Главное меню", reply_markup=get_main_menu_inline_keyboard())
    await state.finish()

def register_goal_handlers(dp: Dispatcher):
    """Регистрация обработчиков целей"""
    dp.register_message_handler(start_goal_change, text="🎯 Цели")
    dp.register_callback_query_handler(process_goal_change_callback, text_startswith='goal_', state=GoalStates.goal) 