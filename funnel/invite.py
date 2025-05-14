from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def send_consultation_invite(update, context):
    with open("data/1.jpg", "rb") as photo:
        await update.message.reply_photo(photo)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Записаться на консультацию", url="https://t.me/dryuzefovna")]
    ])
    await update.message.reply_text(
        "Не обязательно воевать со своим телом, чтобы прийти к результату.\n"
        "Можно иначе — через понимание, поддержку и уважение к себе.\n\n"
        "Я — специалист по расстройствам пищевого поведения и пищевой зависимости.\n"
        "Работаю на стыке психотерапии, нейронауки и подходов, направленных на восстановление связи с телом.\n\n"
        "Помогаю возвращать мотивацию, восстанавливать силы и перестраивать отношения с едой.\n\n"
        "Когда ты начинаешь слышать себя — появляются энергия, лёгкость и уверенность.\n\n"
        "До новой жизни — один шаг. И ты его уже сделала.",
        reply_markup=keyboard
    )
