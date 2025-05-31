from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from app.db.crud import get_user_by_telegram_id
from app.db.session import get_db
from app.db.models import UserPreference

SELECT_TYPE, ENTER_ITEM, CONFIRM_DELETE = range(3)

def preferences_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("preferences", start_preferences)],
        states={
            SELECT_TYPE: [CallbackQueryHandler(select_type)],
            ENTER_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_item)],
            CONFIRM_DELETE: [CallbackQueryHandler(confirm_delete)],
        },
        fallbacks=[]
    )

async def start_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🍎 Любимое", callback_data="like"),
        InlineKeyboardButton("🥴 Нелюбимое", callback_data="dislike")
    ]]
    await update.message.reply_text(
        "🍽 <b>Предпочтения в еде</b>\n\nЧто хочешь указать?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return SELECT_TYPE

async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["pref_type"] = query.data

    db = next(get_db())
    user = get_user_by_telegram_id(query.from_user.id)
    context.user_data["user_id"] = user.id

    prefs = db.query(UserPreference).filter_by(user_id=user.id, preference_type=query.data).all()
    db.close()

    pref_text = "любимое" if query.data == "like" else "нелюбимое"

    if prefs:
        text = "\n".join(f"{i+1}. {p.item}" for i, p in enumerate(prefs))
        keyboard = [[InlineKeyboardButton(p.item, callback_data=f"del:{p.id}")] for p in prefs]
        await query.edit_message_text(
            f"📋 <b>Твой текущий список ({pref_text}):</b>\n\n{text}\n\n✍️ Напиши новый продукт или нажми на кнопку, чтобы удалить:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    else:
        await query.edit_message_text(
            f"📭 <b>Список {pref_text} пуст.</b>\n\n✍️ Напиши продукт, который хочешь добавить:",
            parse_mode="HTML"
        )
    return ENTER_ITEM

async def enter_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = update.message.text.strip().lower()
    if not item:
        await update.message.reply_text("❌ Некорректный ввод. Повтори.", parse_mode="HTML")
        return ENTER_ITEM

    db = next(get_db())
    new_pref = UserPreference(
        user_id=context.user_data["user_id"],
        preference_type=context.user_data["pref_type"],
        item=item
    )
    db.add(new_pref)
    db.commit()
    db.close()

    await update.message.reply_text(f"✅ Добавлено: <b>{item}</b>", parse_mode="HTML")
    return ConversationHandler.END

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pref_id = int(query.data.split(":")[1])

    db = next(get_db())
    pref = db.query(UserPreference).filter_by(id=pref_id).first()
    if pref:
        db.delete(pref)
        db.commit()
        await query.edit_message_text(f"🗑️ Удалено: <b>{pref.item}</b>", parse_mode="HTML")
    else:
        await query.edit_message_text("⚠️ Запись не найдена.", parse_mode="HTML")
    db.close()
    return ConversationHandler.END
