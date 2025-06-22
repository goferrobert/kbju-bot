import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import io
from typing import Optional, List, Tuple

from app.handlers.base import BaseHandler
from app.db.models import UserRecord
from app.utils.validation import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ProgressHandler(BaseHandler):
    """Handler for user progress tracking and visualization."""

    # Константы для форматирования
    MESSAGES = {
        "title": "📊 <b>Ваш прогресс за {period}:</b>\n\n",
        "weight": (
            "⚖️ <b>Вес:</b>\n"
            "• Начальный: {start:.1f} кг\n"
            "• Текущий: {current:.1f} кг\n"
            "• Изменение: {change:+.1f} кг ({percent:+.1f}%)\n\n"
        ),
        "body_fat": (
            "📏 <b>Процент жира:</b>\n"
            "• Начальный: {start:.1f}%\n"
            "• Текущий: {current:.1f}%\n"
            "• Изменение: {change:+.1f}% ({percent:+.1f}%)\n\n"
        ),
        "progress": {
            "Нормальное тело": {
                "weight_loss": "• Отличный прогресс в снижении веса!\n",
                "weight_gain": "• Внимание: наблюдается набор веса.\n",
                "stable": "• Стабильный вес, продолжайте в том же духе.\n"
            },
            "Спортивное тело": {
                "muscle_gain": "• Отличный набор мышечной массы!\n",
                "weight_loss": "• Внимание: наблюдается потеря веса.\n",
                "stable": "• Стабильный вес, продолжайте тренировки.\n"
            },
            "Сухое тело": {
                "fat_loss": "• Отличный прогресс в снижении жира!\n",
                "weight_gain": "• Внимание: наблюдается набор веса.\n",
                "stable": "• Стабильный вес, продолжайте в том же духе.\n"
            }
        }
    }

    def describe_period(self, days: int) -> str:
        """
        Описание периода в человекочитаемом формате.
        
        Args:
            days: Количество дней
            
        Returns:
            str: Описание периода
        """
        if days < 7:
            return f"{days} дней"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} {'неделю' if weeks == 1 else 'недели' if 1 < weeks < 5 else 'недель'}"
        else:
            months = days // 30
            return f"{months} {'месяц' if months == 1 else 'месяца' if 1 < months < 5 else 'месяцев'}"

    def smart_progress_message(
        self,
        weight_change: float,
        fat_change: Optional[float],
        goal: str
    ) -> str:
        """
        Формирование умного сообщения о прогрессе.
        
        Args:
            weight_change: Разница в весе
            fat_change: Разница в проценте жира
            goal: Цель пользователя
            
        Returns:
            str: Сообщение о прогрессе
        """
        message = "🎯 <b>Анализ прогресса:</b>\n"
        progress_messages = self.MESSAGES["progress"][goal]

        if goal == "Нормальное тело":
            if weight_change < -2:
                message += progress_messages["weight_loss"]
            elif weight_change > 2:
                message += progress_messages["weight_gain"]
            else:
                message += progress_messages["stable"]
        elif goal == "Спортивное тело":
            if weight_change > 2 and fat_change and fat_change < 1:
                message += progress_messages["muscle_gain"]
            elif weight_change < -2:
                message += progress_messages["weight_loss"]
            else:
                message += progress_messages["stable"]
        else:  # Сухое тело
            if weight_change < -1 and fat_change and fat_change < -1:
                message += progress_messages["fat_loss"]
            elif weight_change > 1:
                message += progress_messages["weight_gain"]
            else:
                message += progress_messages["stable"]

        return message

    def create_progress_graph(self, records: List[UserRecord]) -> Optional[io.BytesIO]:
        """
        Создание графика прогресса.
        
        Args:
            records: Список записей пользователя
            
        Returns:
            Optional[io.BytesIO]: Объект BytesIO с сохраненным графиком или None, если данных недостаточно
        """
        if len(records) < 2:
            return None

        plt.figure(figsize=(10, 6))
        dates = [r.created_at for r in records]
        weights = [r.weight for r in records]
        body_fat = [r.body_fat for r in records if r.body_fat]

        # Plot weight
        plt.plot(dates, weights, 'b-', label='Вес (кг)', linewidth=2)
        plt.scatter(dates, weights, color='blue', s=50)

        # Plot body fat if available
        if body_fat:
            fat_dates = [r.created_at for r in records if r.body_fat]
            plt.plot(fat_dates, body_fat, 'r-', label='Процент жира (%)', linewidth=2)
            plt.scatter(fat_dates, body_fat, color='red', s=50)

        plt.title('Прогресс изменений', fontsize=14)
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Значение', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()

        # Format x-axis dates
        plt.gcf().autofmt_xdate()

        # Save plot to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        return buf

    def calculate_changes(self, first_record: UserRecord, last_record: UserRecord) -> Tuple[float, float, Optional[float], Optional[float]]:
        """
        Расчет изменений между первой и последней записью.
        
        Args:
            first_record: Первая запись
            last_record: Последняя запись
            
        Returns:
            Tuple[float, float, Optional[float], Optional[float]]: 
                (изменение веса, процент изменения веса, изменение жира, процент изменения жира)
        """
        weight_change = last_record.weight - first_record.weight
        weight_percent = (weight_change / first_record.weight) * 100

        fat_change = None
        fat_percent = None
        if first_record.body_fat and last_record.body_fat:
            fat_change = last_record.body_fat - first_record.body_fat
            fat_percent = (fat_change / first_record.body_fat) * 100

        return weight_change, weight_percent, fat_change, fat_percent

    @BaseHandler.handle_errors
    async def show_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Показ прогресса пользователя.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        records = await self.get_all_records(user.id)
        if not records or len(records) < 2:
            raise ValidationError("Недостаточно данных для анализа прогресса")

        # Анализируем изменения
        first_record = records[0]
        last_record = records[-1]
        days_passed = (last_record.created_at - first_record.created_at).days

        # Рассчитываем изменения
        weight_change, weight_percent, fat_change, fat_percent = self.calculate_changes(first_record, last_record)

        # Формируем сообщение о прогрессе
        message = self.MESSAGES["title"].format(period=self.describe_period(days_passed))

        # Добавляем информацию о весе
        message += self.MESSAGES["weight"].format(
            start=first_record.weight,
            current=last_record.weight,
            change=weight_change,
            percent=weight_percent
        )

        # Добавляем информацию о проценте жира
        if fat_change is not None:
            message += self.MESSAGES["body_fat"].format(
                start=first_record.body_fat,
                current=last_record.body_fat,
                change=fat_change,
                percent=fat_percent
            )

        # Добавляем умный анализ
        message += self.smart_progress_message(
            weight_change=weight_change,
            fat_change=fat_change,
            goal=user.goal
        )

        # Создаем график прогресса
        graph = self.create_progress_graph(records)
        if graph:
            await self.send_photo(update, graph, caption=message, parse_mode="HTML")
        else:
            await self.send_message(update, message, parse_mode="HTML")

        return ConversationHandler.END

def get_progress_handler() -> ConversationHandler:
    """Get the progress conversation handler."""
    handler = ProgressHandler()
    return ConversationHandler(
        entry_points=[handler.show_progress],
        states={},
        fallbacks=[]
    )
