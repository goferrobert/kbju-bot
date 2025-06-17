from typing import Any, Dict, List, Optional, Union
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from app.utils.config import config

class Messages:
    """Message formatting and keyboard utilities."""
    
    # Message templates
    TEMPLATES = {
        'welcome': (
            "👋 Привет, {name}!\n\n"
            "Я бот для отслеживания вашего фитнес-прогресса. "
            "Я помогу вам достичь ваших целей в фитнесе и здоровом образе жизни.\n\n"
            "Давайте начнем с базовой информации о вас."
        ),
        'name': "Как вас зовут?",
        'birth_date': "Укажите вашу дату рождения в формате ДД.ММ.ГГГГ",
        'gender': "Укажите ваш пол:\n1. Мужской\n2. Женский",
        'height': "Укажите ваш рост в сантиметрах",
        'weight': "Укажите ваш текущий вес в килограммах",
        'waist': "Укажите обхват талии в сантиметрах",
        'neck': "Укажите обхват шеи в сантиметрах",
        'hip': "Укажите обхват бедер в сантиметрах",
        'work_type': (
            "Укажите тип вашей работы:\n"
            "1. Сидячая\n"
            "2. Стоячая\n"
            "3. Умеренная\n"
            "4. Тяжелая"
        ),
        'diseases': (
            "Укажите хронические заболевания (если есть).\n"
            "Введите через запятую или напишите 'нет'"
        ),
        'allergies': (
            "Укажите аллергии (если есть).\n"
            "Введите через запятую или напишите 'нет'"
        ),
        'food_preferences': (
            "Укажите предпочтения в еде.\n"
            "Введите через запятую или напишите 'нет'"
        ),
        'steps': "Укажите количество шагов за сегодня",
        'training_frequency': "Сколько раз в неделю вы тренируетесь?",
        'training_type': (
            "Укажите тип тренировок:\n"
            "1. Силовые\n"
            "2. Кардио\n"
            "3. Функциональные\n"
            "4. Смешанные"
        ),
        'training_intensity': (
            "Укажите интенсивность тренировок:\n"
            "1. Низкая\n"
            "2. Средняя\n"
            "3. Высокая"
        ),
        'training_duration': (
            "Укажите длительность тренировок:\n"
            "1. До 30 минут\n"
            "2. 30-60 минут\n"
            "3. Более 60 минут"
        ),
        'goal': (
            "Выберите вашу цель:\n"
            "1. Похудение\n"
            "2. Поддержание веса\n"
            "3. Набор массы"
        ),
        'body_type': (
            "Выберите желаемый тип телосложения:\n"
            "1. Атлетическое\n"
            "2. Худощавое\n"
            "3. Здоровое"
        ),
        'settings': (
            "⚙️ Настройки\n\n"
            "Выберите раздел для настройки:"
        ),
        'notifications': (
            "🔔 Уведомления\n\n"
            "Выберите тип уведомлений:"
        ),
        'help': (
            "📚 Помощь\n\n"
            "Выберите раздел:"
        ),
        'error': "❌ Ошибка: {message}",
        'success': "✅ {message}",
        'info': "ℹ️ {message}",
        'warning': "⚠️ {message}"
    }
    
    # Keyboard layouts
    KEYBOARDS = {
        'main': [
            [
                InlineKeyboardButton("📊 Статистика", callback_data="stats"),
                InlineKeyboardButton("🎯 Цели", callback_data="goals")
            ],
            [
                InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
                InlineKeyboardButton("🔔 Уведомления", callback_data="notifications")
            ],
            [
                InlineKeyboardButton("❓ Помощь", callback_data="help")
            ]
        ],
        'settings': [
            [
                InlineKeyboardButton("🌍 Язык", callback_data="settings_language"),
                InlineKeyboardButton("📏 Единицы", callback_data="settings_units")
            ],
            [
                InlineKeyboardButton("🎨 Тема", callback_data="settings_theme"),
                InlineKeyboardButton("🔔 Уведомления", callback_data="settings_notifications")
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
            ]
        ],
        'notifications': [
            [
                InlineKeyboardButton("⚖️ Вес", callback_data="notify_weight"),
                InlineKeyboardButton("👣 Шаги", callback_data="notify_steps")
            ],
            [
                InlineKeyboardButton("🏋️ Тренировки", callback_data="notify_training"),
                InlineKeyboardButton("🥗 Питание", callback_data="notify_nutrition")
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
            ]
        ],
        'help': [
            [
                InlineKeyboardButton("📝 Команды", callback_data="help_commands"),
                InlineKeyboardButton("❓ FAQ", callback_data="help_faq")
            ],
            [
                InlineKeyboardButton("📞 Контакты", callback_data="help_contacts"),
                InlineKeyboardButton("📚 Документация", callback_data="help_docs")
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
            ]
        ]
    }
    
    @classmethod
    def format(cls, template: str, **kwargs) -> str:
        """
        Format message template.
        
        Args:
            template: Template name
            **kwargs: Template parameters
        
        Returns:
            Formatted message
        """
        if template not in cls.TEMPLATES:
            raise ValueError(f"Template '{template}' not found")
        
        return cls.TEMPLATES[template].format(**kwargs)
    
    @classmethod
    def get_keyboard(cls, name: str) -> InlineKeyboardMarkup:
        """
        Get keyboard layout.
        
        Args:
            name: Keyboard name
        
        Returns:
            InlineKeyboardMarkup object
        """
        if name not in cls.KEYBOARDS:
            raise ValueError(f"Keyboard '{name}' not found")
        
        return InlineKeyboardMarkup(cls.KEYBOARDS[name])
    
    @classmethod
    def format_stats(cls, stats: Dict[str, Any]) -> str:
        """
        Format statistics message.
        
        Args:
            stats: Statistics data
        
        Returns:
            Formatted message
        """
        message = "📊 Статистика\n\n"
        
        # Weight stats
        if 'weight' in stats:
            message += (
                f"Вес: {stats['weight']} кг\n"
                f"Изменение: {stats.get('weight_change', 0):+.1f} кг\n"
            )
        
        # Body fat stats
        if 'body_fat' in stats:
            message += (
                f"Процент жира: {stats['body_fat']}%\n"
                f"Изменение: {stats.get('body_fat_change', 0):+.1f}%\n"
            )
        
        # Steps stats
        if 'steps' in stats:
            message += (
                f"Шаги: {stats['steps']}\n"
                f"Цель: {stats.get('steps_goal', 10000)}\n"
            )
        
        # Training stats
        if 'training' in stats:
            message += (
                f"Тренировки: {stats['training']['frequency']} раз в неделю\n"
                f"Тип: {stats['training']['type']}\n"
                f"Интенсивность: {stats['training']['intensity']}\n"
            )
        
        return message
    
    @classmethod
    def format_goal(cls, goal: Dict[str, Any]) -> str:
        """
        Format goal message.
        
        Args:
            goal: Goal data
        
        Returns:
            Formatted message
        """
        message = "🎯 Цели\n\n"
        
        # Weight goal
        if 'target_weight' in goal:
            message += f"Целевой вес: {goal['target_weight']} кг\n"
        
        # Body fat goal
        if 'target_body_fat' in goal:
            message += f"Целевой процент жира: {goal['target_body_fat']}%\n"
        
        # Nutrition goals
        if 'calories' in goal:
            message += (
                f"\nПитание:\n"
                f"Калории: {goal['calories']} ккал\n"
                f"Белки: {goal.get('proteins', 0)}г\n"
                f"Жиры: {goal.get('fats', 0)}г\n"
                f"Углеводы: {goal.get('carbs', 0)}г\n"
            )
        
        return message
    
    @classmethod
    def format_settings(cls, settings: Dict[str, Any]) -> str:
        """
        Format settings message.
        
        Args:
            settings: Settings data
        
        Returns:
            Formatted message
        """
        message = "⚙️ Настройки\n\n"
        
        # Language
        if 'language' in settings:
            message += f"Язык: {settings['language']}\n"
        
        # Units
        if 'units' in settings:
            message += f"Единицы измерения: {settings['units']}\n"
        
        # Theme
        if 'theme' in settings:
            message += f"Тема: {settings['theme']}\n"
        
        # Notifications
        if 'notifications_enabled' in settings:
            message += f"Уведомления: {'Включены' if settings['notifications_enabled'] else 'Выключены'}\n"
        
        return message
    
    @classmethod
    def format_notifications(cls, notifications: List[Dict[str, Any]]) -> str:
        """
        Format notifications message.
        
        Args:
            notifications: List of notifications
        
        Returns:
            Formatted message
        """
        message = "🔔 Уведомления\n\n"
        
        if not notifications:
            message += "Нет активных уведомлений"
            return message
        
        for notification in notifications:
            message += (
                f"Тип: {notification['type']}\n"
                f"Время: {notification['time']}\n"
                f"Статус: {'Активно' if notification['is_active'] else 'Неактивно'}\n\n"
            )
        
        return message
    
    @classmethod
    def format_help(cls, section: str) -> str:
        """
        Format help message.
        
        Args:
            section: Help section
        
        Returns:
            Formatted message
        """
        if section == 'commands':
            return (
                "📝 Команды\n\n"
                "/start - Начать работу с ботом\n"
                "/stats - Показать статистику\n"
                "/goals - Управление целями\n"
                "/settings - Настройки\n"
                "/notifications - Уведомления\n"
                "/help - Помощь"
            )
        elif section == 'faq':
            return (
                "❓ Часто задаваемые вопросы\n\n"
                "Q: Как часто нужно вводить данные?\n"
                "A: Рекомендуется вводить вес и обмеры раз в неделю, шаги - ежедневно.\n\n"
                "Q: Как рассчитывается процент жира?\n"
                "A: Используется формула ВМС США, учитывающая пол, рост и обмеры.\n\n"
                "Q: Как настроить уведомления?\n"
                "A: Перейдите в раздел 'Уведомления' и выберите нужные типы."
            )
        elif section == 'contacts':
            return (
                "📞 Контакты\n\n"
                "По всем вопросам обращайтесь:\n"
                "Email: support@example.com\n"
                "Telegram: @support"
            )
        elif section == 'docs':
            return (
                "📚 Документация\n\n"
                "Подробная документация доступна по ссылке:\n"
                "https://example.com/docs"
            )
        else:
            return "Раздел не найден"
    
    @classmethod
    def format_error(cls, message: str) -> str:
        """
        Format error message.
        
        Args:
            message: Error message
        
        Returns:
            Formatted message
        """
        return cls.format('error', message=message)
    
    @classmethod
    def format_success(cls, message: str) -> str:
        """
        Format success message.
        
        Args:
            message: Success message
        
        Returns:
            Formatted message
        """
        return cls.format('success', message=message)
    
    @classmethod
    def format_info(cls, message: str) -> str:
        """
        Format info message.
        
        Args:
            message: Info message
        
        Returns:
            Formatted message
        """
        return cls.format('info', message=message)
    
    @classmethod
    def format_warning(cls, message: str) -> str:
        """
        Format warning message.
        
        Args:
            message: Warning message
        
        Returns:
            Formatted message
        """
        return cls.format('warning', message=message) 