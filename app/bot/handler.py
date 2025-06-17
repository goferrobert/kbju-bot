from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from app.utils.messages import Messages
from app.utils.validation import (
    validate_name,
    validate_birth_date,
    validate_gender,
    validate_height,
    validate_weight,
    validate_measurement,
    validate_steps,
    validate_activity_level,
    validate_training_type,
    validate_training_intensity,
    validate_training_duration,
    validate_goal,
    validate_body_type,
    validate_work_type,
    validate_diseases,
    validate_allergies,
    validate_food_preferences
)
from app.utils.calculations import (
    calculate_body_fat,
    calculate_bmr,
    calculate_tdee,
    calculate_macros
)
from app.db.database import Database
from app.utils.logger import logger

# Conversation states
(
    NAME,
    BIRTH_DATE,
    GENDER,
    HEIGHT,
    WEIGHT,
    WAIST,
    NECK,
    HIP,
    WORK_TYPE,
    DISEASES,
    ALLERGIES,
    FOOD_PREFERENCES,
    STEPS,
    TRAINING_FREQUENCY,
    TRAINING_TYPE,
    TRAINING_INTENSITY,
    TRAINING_DURATION,
    GOAL,
    BODY_TYPE
) = range(19)

class BotHandler:
    """Main bot handler class."""
    
    def __init__(self, db: Database):
        """Initialize bot handler."""
        self.db = db
        self.conversation_handler = self._create_conversation_handler()
    
    def _create_conversation_handler(self) -> ConversationHandler:
        """Create conversation handler."""
        return ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_name)],
                BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_birth_date)],
                GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_gender)],
                HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_height)],
                WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_weight)],
                WAIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_waist)],
                NECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_neck)],
                HIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_hip)],
                WORK_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_work_type)],
                DISEASES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_diseases)],
                ALLERGIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_allergies)],
                FOOD_PREFERENCES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_food_preferences)],
                STEPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_steps)],
                TRAINING_FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_training_frequency)],
                TRAINING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_training_type)],
                TRAINING_INTENSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_training_intensity)],
                TRAINING_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_training_duration)],
                GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_goal)],
                BODY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_body_type)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
    
    async def start(self, update: Update, context: CallbackContext) -> int:
        """Start conversation."""
        user = update.effective_user
        
        # Check if user exists
        db_user = self.db.get_user(user.id)
        if db_user:
            # User exists, show main menu
            await update.message.reply_text(
                Messages.format('welcome', name=db_user.first_name),
                reply_markup=Messages.get_keyboard('main')
            )
            return ConversationHandler.END
        
        # New user, start registration
        await update.message.reply_text(Messages.format('name'))
        return NAME
    
    async def process_name(self, update: Update, context: CallbackContext) -> int:
        """Process user name."""
        name = validate_name(update.message.text)
        if not name:
            await update.message.reply_text(Messages.format_error("Неверное имя"))
            return NAME
        
        context.user_data['name'] = name
        await update.message.reply_text(Messages.format('birth_date'))
        return BIRTH_DATE
    
    async def process_birth_date(self, update: Update, context: CallbackContext) -> int:
        """Process birth date."""
        birth_date = validate_birth_date(update.message.text)
        if not birth_date:
            await update.message.reply_text(Messages.format_error("Неверная дата рождения"))
            return BIRTH_DATE
        
        context.user_data['birth_date'] = birth_date
        await update.message.reply_text(Messages.format('gender'))
        return GENDER
    
    async def process_gender(self, update: Update, context: CallbackContext) -> int:
        """Process gender."""
        gender = validate_gender(update.message.text)
        if not gender:
            await update.message.reply_text(Messages.format_error("Неверный пол"))
            return GENDER
        
        context.user_data['gender'] = gender
        await update.message.reply_text(Messages.format('height'))
        return HEIGHT
    
    async def process_height(self, update: Update, context: CallbackContext) -> int:
        """Process height."""
        height = validate_height(update.message.text)
        if not height:
            await update.message.reply_text(Messages.format_error("Неверный рост"))
            return HEIGHT
        
        context.user_data['height'] = height
        await update.message.reply_text(Messages.format('weight'))
        return WEIGHT
    
    async def process_weight(self, update: Update, context: CallbackContext) -> int:
        """Process weight."""
        weight = validate_weight(update.message.text)
        if not weight:
            await update.message.reply_text(Messages.format_error("Неверный вес"))
            return WEIGHT
        
        context.user_data['weight'] = weight
        await update.message.reply_text(Messages.format('waist'))
        return WAIST
    
    async def process_waist(self, update: Update, context: CallbackContext) -> int:
        """Process waist measurement."""
        waist = validate_measurement(update.message.text)
        if not waist:
            await update.message.reply_text(Messages.format_error("Неверный обхват талии"))
            return WAIST
        
        context.user_data['waist'] = waist
        await update.message.reply_text(Messages.format('neck'))
        return NECK
    
    async def process_neck(self, update: Update, context: CallbackContext) -> int:
        """Process neck measurement."""
        neck = validate_measurement(update.message.text)
        if not neck:
            await update.message.reply_text(Messages.format_error("Неверный обхват шеи"))
            return NECK
        
        context.user_data['neck'] = neck
        await update.message.reply_text(Messages.format('hip'))
        return HIP
    
    async def process_hip(self, update: Update, context: CallbackContext) -> int:
        """Process hip measurement."""
        hip = validate_measurement(update.message.text)
        if not hip:
            await update.message.reply_text(Messages.format_error("Неверный обхват бедер"))
            return HIP
        
        context.user_data['hip'] = hip
        await update.message.reply_text(Messages.format('work_type'))
        return WORK_TYPE
    
    async def process_work_type(self, update: Update, context: CallbackContext) -> int:
        """Process work type."""
        work_type = validate_work_type(update.message.text)
        if not work_type:
            await update.message.reply_text(Messages.format_error("Неверный тип работы"))
            return WORK_TYPE
        
        context.user_data['work_type'] = work_type
        await update.message.reply_text(Messages.format('diseases'))
        return DISEASES
    
    async def process_diseases(self, update: Update, context: CallbackContext) -> int:
        """Process diseases."""
        diseases = validate_diseases(update.message.text)
        if diseases is None:
            await update.message.reply_text(Messages.format_error("Неверный формат заболеваний"))
            return DISEASES
        
        context.user_data['diseases'] = diseases
        await update.message.reply_text(Messages.format('allergies'))
        return ALLERGIES
    
    async def process_allergies(self, update: Update, context: CallbackContext) -> int:
        """Process allergies."""
        allergies = validate_allergies(update.message.text)
        if allergies is None:
            await update.message.reply_text(Messages.format_error("Неверный формат аллергий"))
            return ALLERGIES
        
        context.user_data['allergies'] = allergies
        await update.message.reply_text(Messages.format('food_preferences'))
        return FOOD_PREFERENCES
    
    async def process_food_preferences(self, update: Update, context: CallbackContext) -> int:
        """Process food preferences."""
        preferences = validate_food_preferences(update.message.text)
        if preferences is None:
            await update.message.reply_text(Messages.format_error("Неверный формат предпочтений"))
            return FOOD_PREFERENCES
        
        context.user_data['food_preferences'] = preferences
        await update.message.reply_text(Messages.format('steps'))
        return STEPS
    
    async def process_steps(self, update: Update, context: CallbackContext) -> int:
        """Process steps."""
        steps = validate_steps(update.message.text)
        if not steps:
            await update.message.reply_text(Messages.format_error("Неверное количество шагов"))
            return STEPS
        
        context.user_data['steps'] = steps
        await update.message.reply_text(Messages.format('training_frequency'))
        return TRAINING_FREQUENCY
    
    async def process_training_frequency(self, update: Update, context: CallbackContext) -> int:
        """Process training frequency."""
        frequency = validate_activity_level(update.message.text)
        if not frequency:
            await update.message.reply_text(Messages.format_error("Неверная частота тренировок"))
            return TRAINING_FREQUENCY
        
        context.user_data['training_frequency'] = frequency
        await update.message.reply_text(Messages.format('training_type'))
        return TRAINING_TYPE
    
    async def process_training_type(self, update: Update, context: CallbackContext) -> int:
        """Process training type."""
        training_type = validate_training_type(update.message.text)
        if not training_type:
            await update.message.reply_text(Messages.format_error("Неверный тип тренировок"))
            return TRAINING_TYPE
        
        context.user_data['training_type'] = training_type
        await update.message.reply_text(Messages.format('training_intensity'))
        return TRAINING_INTENSITY
    
    async def process_training_intensity(self, update: Update, context: CallbackContext) -> int:
        """Process training intensity."""
        intensity = validate_training_intensity(update.message.text)
        if not intensity:
            await update.message.reply_text(Messages.format_error("Неверная интенсивность"))
            return TRAINING_INTENSITY
        
        context.user_data['training_intensity'] = intensity
        await update.message.reply_text(Messages.format('training_duration'))
        return TRAINING_DURATION
    
    async def process_training_duration(self, update: Update, context: CallbackContext) -> int:
        """Process training duration."""
        duration = validate_training_duration(update.message.text)
        if not duration:
            await update.message.reply_text(Messages.format_error("Неверная длительность"))
            return TRAINING_DURATION
        
        context.user_data['training_duration'] = duration
        await update.message.reply_text(Messages.format('goal'))
        return GOAL
    
    async def process_goal(self, update: Update, context: CallbackContext) -> int:
        """Process goal."""
        goal = validate_goal(update.message.text)
        if not goal:
            await update.message.reply_text(Messages.format_error("Неверная цель"))
            return GOAL
        
        context.user_data['goal'] = goal
        await update.message.reply_text(Messages.format('body_type'))
        return BODY_TYPE
    
    async def process_body_type(self, update: Update, context: CallbackContext) -> int:
        """Process body type and finish registration."""
        body_type = validate_body_type(update.message.text)
        if not body_type:
            await update.message.reply_text(Messages.format_error("Неверный тип телосложения"))
            return BODY_TYPE
        
        # Get user data
        user_data = context.user_data
        user = update.effective_user
        
        try:
            # Calculate body fat
            body_fat = calculate_body_fat(
                gender=user_data['gender'],
                weight=user_data['weight'],
                height=user_data['height'],
                waist=user_data['waist'],
                neck=user_data['neck'],
                hip=user_data.get('hip')
            )
            
            # Calculate BMR and TDEE
            bmr, tdee = calculate_bmr(
                gender=user_data['gender'],
                weight=user_data['weight'],
                height=user_data['height'],
                age=user_data['birth_date'].year,
                activity_level=user_data['work_type']
            )
            
            # Calculate macros
            macros = calculate_macros(
                tdee=tdee,
                goal=user_data['goal']
            )
            
            # Create user in database
            self.db.create_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user_data['name'],
                last_name=user.last_name,
                birth_date=user_data['birth_date'],
                gender=user_data['gender'],
                height=user_data['height'],
                work_type=user_data['work_type'],
                chronic_diseases=user_data['diseases'],
                allergies=user_data['allergies'],
                food_preferences=user_data['food_preferences']
            )
            
            # Add initial record
            self.db.add_user_record(
                telegram_id=user.id,
                weight=user_data['weight'],
                waist=user_data['waist'],
                neck=user_data['neck'],
                hip=user_data.get('hip'),
                body_fat=body_fat,
                steps=user_data['steps'],
                bmr=bmr
            )
            
            # Set user goal
            self.db.set_user_goal(
                telegram_id=user.id,
                body_type=body_type,
                target_weight=user_data['weight'] * 0.9 if user_data['goal'] == 'weight_loss' else user_data['weight'],
                target_body_fat=body_fat * 0.9 if user_data['goal'] == 'weight_loss' else body_fat,
                calories=macros['calories'],
                proteins=macros['proteins'],
                fats=macros['fats'],
                carbs=macros['carbs']
            )
            
            # Show success message
            await update.message.reply_text(
                Messages.format_success("Регистрация завершена!"),
                reply_markup=Messages.get_keyboard('main')
            )
            
            # Clear user data
            context.user_data.clear()
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            await update.message.reply_text(
                Messages.format_error("Произошла ошибка при регистрации. Попробуйте позже.")
            )
            return ConversationHandler.END
    
    async def cancel(self, update: Update, context: CallbackContext) -> int:
        """Cancel conversation."""
        await update.message.reply_text(
            Messages.format_info("Регистрация отменена"),
            reply_markup=Messages.get_keyboard('main')
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    async def handle_callback(self, update: Update, context: CallbackContext) -> None:
        """Handle callback queries."""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'stats':
            # Get user stats
            user = self.db.get_user(query.from_user.id)
            if not user:
                await query.message.reply_text(Messages.format_error("Пользователь не найден"))
                return
            
            records = self.db.get_user_records(query.from_user.id, limit=2)
            if not records:
                await query.message.reply_text(Messages.format_error("Нет данных для отображения"))
                return
            
            current = records[0]
            previous = records[1] if len(records) > 1 else None
            
            stats = {
                'weight': current.weight,
                'weight_change': current.weight - previous.weight if previous else 0,
                'body_fat': current.body_fat,
                'body_fat_change': current.body_fat - previous.body_fat if previous else 0,
                'steps': current.steps,
                'steps_goal': 10000,  # TODO: Get from settings
                'training': {
                    'frequency': user.training_frequency,
                    'type': user.training_type,
                    'intensity': user.training_intensity
                }
            }
            
            await query.message.reply_text(
                Messages.format_stats(stats),
                reply_markup=Messages.get_keyboard('main')
            )
            
        elif query.data == 'goals':
            # Get user goals
            goal = self.db.get_user_goal(query.from_user.id)
            if not goal:
                await query.message.reply_text(Messages.format_error("Цели не установлены"))
                return
            
            await query.message.reply_text(
                Messages.format_goal(goal),
                reply_markup=Messages.get_keyboard('main')
            )
            
        elif query.data == 'settings':
            # Get user settings
            settings = self.db.get_user_settings(query.from_user.id)
            if not settings:
                await query.message.reply_text(Messages.format_error("Настройки не найдены"))
                return
            
            await query.message.reply_text(
                Messages.format_settings(settings),
                reply_markup=Messages.get_keyboard('settings')
            )
            
        elif query.data == 'notifications':
            # Get user notifications
            notifications = self.db.get_user_notifications(query.from_user.id)
            
            await query.message.reply_text(
                Messages.format_notifications(notifications),
                reply_markup=Messages.get_keyboard('notifications')
            )
            
        elif query.data == 'help':
            await query.message.reply_text(
                Messages.format_help('commands'),
                reply_markup=Messages.get_keyboard('help')
            )
            
        elif query.data.startswith('help_'):
            section = query.data.split('_')[1]
            await query.message.reply_text(
                Messages.format_help(section),
                reply_markup=Messages.get_keyboard('help')
            )
            
        elif query.data == 'back_to_main':
            await query.message.reply_text(
                Messages.format('welcome', name=query.from_user.first_name),
                reply_markup=Messages.get_keyboard('main')
            ) 