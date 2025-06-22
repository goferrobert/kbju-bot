from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
import io

from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import UserRecord
from app.utils.validation import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

class StatsHandler(BaseHandler):
    """Handler for displaying user statistics."""

    # Константы для форматирования
    MESSAGES = {
        "start": (
            "📊 <b>Статистика</b>\n\n"
            "Выберите тип статистики:"
        ),
        "weight": (
            "⚖️ <b>Статистика веса</b>\n\n"
            "• Начальный вес: {start:.1f} кг\n"
            "• Текущий вес: {current:.1f} кг\n"
            "• Изменение: {change:+.1f} кг ({percent:+.1f}%)\n"
            "• Средний вес: {avg:.1f} кг\n"
            "• Минимальный вес: {min:.1f} кг\n"
            "• Максимальный вес: {max:.1f} кг"
        ),
        "steps": (
            "👣 <b>Статистика шагов</b>\n\n"
            "• Среднее количество шагов: {avg:.0f}\n"
            "• Минимальное количество: {min}\n"
            "• Максимальное количество: {max}\n"
            "• Всего шагов: {total:,}\n"
            "• Дней с данными: {days}"
        ),
        "sport": (
            "🏃 <b>Статистика спорта</b>\n\n"
            "• Всего тренировок: {total}\n"
            "• Средняя длительность: {avg_duration:.0f} мин\n"
            "• Общее время: {total_time:.0f} мин\n"
            "• Любимый вид: {favorite}\n"
            "• Средняя интенсивность: {avg_intensity:.1f}"
        ),
        "body_fat": (
            "📏 <b>Статистика жира</b>\n\n"
            "• Начальный процент: {start:.1f}%\n"
            "• Текущий процент: {current:.1f}%\n"
            "• Изменение: {change:+.1f}% ({percent:+.1f}%)\n"
            "• Средний процент: {avg:.1f}%\n"
            "• Минимальный процент: {min:.1f}%\n"
            "• Максимальный процент: {max:.1f}%"
        ),
        "no_data": "❌ Недостаточно данных для отображения статистики."
    }

    # Константы для клавиатуры
    KEYBOARD = {
        "main": [
            [
                InlineKeyboardButton("Вес", callback_data="weight"),
                InlineKeyboardButton("Шаги", callback_data="steps")
            ],
            [
                InlineKeyboardButton("Спорт", callback_data="sport"),
                InlineKeyboardButton("Жир", callback_data="body_fat")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ]
    }

    def calculate_weight_stats(self, records: List[UserRecord]) -> Dict:
        """
        Расчет статистики веса.
        
        Args:
            records: Список записей пользователя
            
        Returns:
            Dict: Словарь со статистикой
        """
        if not records:
            return {}

        weights = [r.weight for r in records]
        start_weight = weights[0]
        current_weight = weights[-1]
        weight_change = current_weight - start_weight
        weight_percent = (weight_change / start_weight) * 100

        return {
            "start": start_weight,
            "current": current_weight,
            "change": weight_change,
            "percent": weight_percent,
            "avg": sum(weights) / len(weights),
            "min": min(weights),
            "max": max(weights)
        }

    def calculate_steps_stats(self, records: List[UserRecord]) -> Dict:
        """
        Расчет статистики шагов.
        
        Args:
            records: Список записей пользователя
            
        Returns:
            Dict: Словарь со статистикой
        """
        if not records:
            return {}

        steps = [r.steps for r in records if r.steps is not None]
        if not steps:
            return {}

        return {
            "avg": sum(steps) / len(steps),
            "min": min(steps),
            "max": max(steps),
            "total": sum(steps),
            "days": len(steps)
        }

    def calculate_sport_stats(self, records: List[UserRecord]) -> Dict:
        """
        Расчет статистики спорта.
        
        Args:
            records: Список записей пользователя
            
        Returns:
            Dict: Словарь со статистикой
        """
        if not records:
            return {}

        sport_records = [r for r in records if r.sport_type and r.sport_duration]
        if not sport_records:
            return {}

        durations = [r.sport_duration for r in sport_records]
        intensities = [r.sport_intensity for r in sport_records if r.sport_intensity]

        # Определяем любимый вид спорта
        sport_types = [r.sport_type for r in sport_records]
        favorite = max(set(sport_types), key=sport_types.count)

        return {
            "total": len(sport_records),
            "avg_duration": sum(durations) / len(durations),
            "total_time": sum(durations),
            "favorite": favorite,
            "avg_intensity": sum(intensities) / len(intensities) if intensities else 0
        }

    def calculate_body_fat_stats(self, records: List[UserRecord]) -> Dict:
        """
        Расчет статистики жира.
        
        Args:
            records: Список записей пользователя
            
        Returns:
            Dict: Словарь со статистикой
        """
        if not records:
            return {}

        body_fat = [r.body_fat for r in records if r.body_fat is not None]
        if not body_fat:
            return {}

        start_fat = body_fat[0]
        current_fat = body_fat[-1]
        fat_change = current_fat - start_fat
        fat_percent = (fat_change / start_fat) * 100

        return {
            "start": start_fat,
            "current": current_fat,
            "change": fat_change,
            "percent": fat_percent,
            "avg": sum(body_fat) / len(body_fat),
            "min": min(body_fat),
            "max": max(body_fat)
        }

    def create_stats_graph(self, records: List[UserRecord], stat_type: str) -> Optional[io.BytesIO]:
        """
        Создание графика статистики.
        
        Args:
            records: Список записей пользователя
            stat_type: Тип статистики
            
        Returns:
            Optional[io.BytesIO]: Объект BytesIO с сохраненным графиком или None
        """
        if not records:
            return None

        plt.figure(figsize=(10, 6))
        dates = [r.created_at for r in records]

        if stat_type == "weight":
            values = [r.weight for r in records]
            plt.plot(dates, values, 'b-', label='Вес (кг)', linewidth=2)
            plt.scatter(dates, values, color='blue', s=50)
            plt.title('Динамика веса', fontsize=14)
            plt.ylabel('Вес (кг)', fontsize=12)

        elif stat_type == "steps":
            values = [r.steps for r in records if r.steps is not None]
            if not values:
                return None
            plt.plot(dates[:len(values)], values, 'g-', label='Шаги', linewidth=2)
            plt.scatter(dates[:len(values)], values, color='green', s=50)
            plt.title('Динамика шагов', fontsize=14)
            plt.ylabel('Количество шагов', fontsize=12)

        elif stat_type == "body_fat":
            values = [r.body_fat for r in records if r.body_fat is not None]
            if not values:
                return None
            plt.plot(dates[:len(values)], values, 'r-', label='Процент жира (%)', linewidth=2)
            plt.scatter(dates[:len(values)], values, color='red', s=50)
            plt.title('Динамика процента жира', fontsize=14)
            plt.ylabel('Процент жира (%)', fontsize=12)

        else:
            return None

        plt.xlabel('Дата', fontsize=12)
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

    @BaseHandler.handle_errors
    async def start_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начало процесса отображения статистики.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        await self.send_message(
            update,
            self.MESSAGES["start"],
            reply_markup=InlineKeyboardMarkup(self.KEYBOARD["main"])
        )
        return UserStates.WAITING_FOR_STATS_TYPE

    @BaseHandler.handle_errors
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Отображение выбранной статистики.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        if query.data == "back":
            return ConversationHandler.END

        stat_type = query.data
        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        records = await self.get_all_records(user.id)
        if not records:
            await self.send_message(update, self.MESSAGES["no_data"])
            return await self.start_stats(update, context)

        # Получаем статистику
        if stat_type == "weight":
            stats = self.calculate_weight_stats(records)
            if stats:
                message = self.MESSAGES["weight"].format(**stats)
            else:
                message = self.MESSAGES["no_data"]

        elif stat_type == "steps":
            stats = self.calculate_steps_stats(records)
            if stats:
                message = self.MESSAGES["steps"].format(**stats)
            else:
                message = self.MESSAGES["no_data"]

        elif stat_type == "sport":
            stats = self.calculate_sport_stats(records)
            if stats:
                message = self.MESSAGES["sport"].format(**stats)
            else:
                message = self.MESSAGES["no_data"]

        elif stat_type == "body_fat":
            stats = self.calculate_body_fat_stats(records)
            if stats:
                message = self.MESSAGES["body_fat"].format(**stats)
            else:
                message = self.MESSAGES["no_data"]

        else:
            return await self.start_stats(update, context)

        # Создаем график
        graph = self.create_stats_graph(records, stat_type)
        if graph:
            await self.send_photo(update, graph, caption=message, parse_mode="HTML")
        else:
            await self.send_message(update, message, parse_mode="HTML")

        return await self.start_stats(update, context)

def get_stats_handler() -> ConversationHandler:
    """Get the stats conversation handler."""
    handler = StatsHandler()
    return ConversationHandler(
        entry_points=[handler.start_stats],
        states={
            UserStates.WAITING_FOR_STATS_TYPE: [
                handler.show_stats
            ]
        },
        fallbacks=[]
    ) 