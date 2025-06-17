from telegram import Update
from telegram.ext import ContextTypes
from datetime import date

from app.handlers.base import BaseHandler
from app.db.models import User, UserRecord
from app.utils.validation import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

class MyDataHandler(BaseHandler):
    """Handler for user data display."""

    # Константы для форматирования
    DATA_FORMAT = {
        "name": "👤 Имя: <b>{value}</b>",
        "age": "🎂 Возраст: <b>{value}</b>",
        "height": "📏 Рост: <b>{value} см</b>",
        "weight": "⚖️ Вес: <b>{value} кг</b>",
        "waist": "📉 Талия: <b>{value} см</b>",
        "neck": "📏 Шея: <b>{value} см</b>",
        "hip": "🦵 Бёдра: <b>{value} см</b>",
        "body_fat": "💪 Жир: <b>{value}%</b>",
        "step_level": "🚶 Шаги: <b>Уровень {value}</b>",
        "sport": "💪 Тренировки: <b>{value}</b>",
        "kbju": {
            "title": "\n<b>🍽 Твоя дневная норма:</b>",
            "calories": "🔥 Калории: <b>{value}</b>",
            "protein": "🥩 Белки: <b>{value} г</b>",
            "fat": "🧈 Жиры: <b>{value} г</b>",
            "carbs": "🍞 Углеводы: <b>{value} г</b>"
        }
    }

    def calculate_age(self, birth_date: date) -> int:
        """
        Расчет возраста пользователя.
        
        Args:
            birth_date: Дата рождения
            
        Returns:
            int: Возраст в годах
        """
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    def format_sport_info(self, sport_type: str, sport_freq: str) -> str:
        """
        Форматирование информации о тренировках.
        
        Args:
            sport_type: Тип тренировок
            sport_freq: Частота тренировок
            
        Returns:
            str: Отформатированная строка
        """
        if not sport_type or sport_type == "нет":
            return None
        return f"{sport_type.replace('sport_', '').capitalize()} — {sport_freq} р/нед"

    @BaseHandler.handle_errors
    async def show_user_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User = None, record: UserRecord = None, skip_kbju: bool = False) -> None:
        """
        Показ сводки данных пользователя.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            user: Пользователь (опционально)
            record: Запись пользователя (опционально)
            skip_kbju: Пропустить отображение КБЖУ
        """
        if not user:
            user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        if not record:
            record = await self.get_latest_record(user.id)
        if not record:
            raise ValidationError("Нет данных о записях пользователя")

        # Формируем список строк для отображения
        lines = ["<b>📁 Мои данные:</b>"]

        # Добавляем основные данные
        lines.append(self.DATA_FORMAT["name"].format(value=user.name or user.first_name))
        
        age = self.calculate_age(user.date_of_birth) if user.date_of_birth else "—"
        lines.append(self.DATA_FORMAT["age"].format(value=age))
        
        if user.height:
            lines.append(self.DATA_FORMAT["height"].format(value=user.height))
        
        if record.weight:
            lines.append(self.DATA_FORMAT["weight"].format(value=record.weight))

        # Добавляем измерения
        if record.waist:
            lines.append(self.DATA_FORMAT["waist"].format(value=record.waist))
        if record.neck:
            lines.append(self.DATA_FORMAT["neck"].format(value=record.neck))
        if record.hip:
            lines.append(self.DATA_FORMAT["hip"].format(value=record.hip))
        if record.body_fat:
            lines.append(self.DATA_FORMAT["body_fat"].format(value=record.body_fat))

        # Добавляем активность
        if record.step_level:
            lines.append(self.DATA_FORMAT["step_level"].format(value=record.step_level))
        
        sport_info = self.format_sport_info(record.sport_type, record.sport_freq)
        if sport_info:
            lines.append(self.DATA_FORMAT["sport"].format(value=sport_info))

        # Добавляем КБЖУ
        if not skip_kbju and record.calories and record.protein and record.fat and record.carbs:
            lines.append(self.DATA_FORMAT["kbju"]["title"])
            lines.append(self.DATA_FORMAT["kbju"]["calories"].format(value=record.calories))
            lines.append(self.DATA_FORMAT["kbju"]["protein"].format(value=record.protein))
            lines.append(self.DATA_FORMAT["kbju"]["fat"].format(value=record.fat))
            lines.append(self.DATA_FORMAT["kbju"]["carbs"].format(value=record.carbs))

        await self.send_message(update, "\n".join(lines), parse_mode="HTML")

def get_my_data_handler() -> MyDataHandler:
    """Get the my data handler instance."""
    return MyDataHandler()
