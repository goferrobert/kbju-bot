def calculate_kbju(data: dict) -> str:
    weight = data["weight"]
    height = data["height"]
    age = data["age"]
    activity = data["activity"]
    sex = data["sex"]
    target_weight = data["target_weight"]

    factors = [1.2, 1.375, 1.55, 1.725, 1.9]
    factor = factors[activity - 1]

    # Формулы Миффлина и Харриса
    if sex == "мужчина":
        bmr_m = 10 * weight + 6.25 * height - 5 * age + 5
        bmr_h = 66.5 + 13.75 * weight + 5.003 * height - 6.775 * age
    else:
        bmr_m = 10 * weight + 6.25 * height - 5 * age - 161
        bmr_h = 655.1 + 9.563 * weight + 1.85 * height - 4.676 * age

    bmr = round((bmr_m + bmr_h) / 2)
    tdee = round(bmr * factor)

    delta = (target_weight - weight) / weight * 100
    result = ""

    if delta < -3:
        mode = "📉 Похудение"
        kcal = tdee - 500
        delta_kg = abs(target_weight - weight)
        days = int(delta_kg * 7700 / 500)
        prot = round(weight * 2.2)
        fat = round(weight * 0.8)
        carbs = max(round((kcal - prot * 4 - fat * 9) / 4), 50)

        steps_bonus = 260
        days_with_steps = int((delta_kg * 7700) / (500 + steps_bonus))
        saved_days = days - days_with_steps

        result = f"""{mode}
🥚 Б: {prot} г | 🥑 Ж: {fat} г | 🍚 У: {carbs} г
Калорийность: {kcal} ккал

📅 При соблюдении режима ты достигнешь цели примерно за {days} дней.

🚶‍♀️ Добавив 6000 шагов в день, ты ускоришь результат на {saved_days} дней
📉 Вместо {days} дней — всего {days_with_steps}

📌 Чтобы похудеть и сохранить здоровье — мы увеличиваем белок.
Он помогает сохранить мышцы, чувствовать сытость и избегать срывов."""

    elif delta > 3:
        mode = "🔺 Набор массы"
        kcal = tdee + 500
        delta_kg = abs(target_weight - weight)
        days = int(delta_kg * 7700 / 500)
        months = days / 30
        muscle = round(months * 1.0, 1)
        prot = round(weight * 2.0)
        fat = round(weight * 1.0)
        carbs = max(round((kcal - prot * 4 - fat * 9) / 4), 80)

        result = f"""{mode}
🥚 Б: {prot} г | 🥑 Ж: {fat} г | 🍚 У: {carbs} г
Калорийность: {kcal} ккал

📅 При соблюдении режима ты достигнешь цели примерно за {days} дней.

💪 Если ты будешь тренироваться 2–3 раза в неделю, за это время ты сможешь набрать примерно {muscle} кг мышц.

📌 Набор массы — это не про «есть больше», а про расти сильнее.
Целевой вес — это форма и сила твоего тела."""

    else:
        mode = "⚖️ Поддержание"
        kcal = tdee
        prot = round(weight * 1.8)
        fat = round(weight * 1.0)
        carbs = max(round((kcal - prot * 4 - fat * 9) / 4), 100)

        cake_kcal = 250
        kcal_per_minute_walk = 4.5
        walk_minutes = int(cake_kcal / kcal_per_minute_walk)

        result = f"""{mode}
🥚 Б: {prot} г | 🥑 Ж: {fat} г | 🍚 У: {carbs} г
Калорийность: {kcal} ккал

📌 Ты можешь есть всё, что хочешь — если укладываешься в свой БЖУ. 🍫
А если вдруг захотелось сладенького — ничего страшного.

Один лишний кусочек торта — это всего ~{walk_minutes} минут прогулки.
Ты в балансе. И это главное."""

    return result
