@echo off
chcp 65001 >nul

REM === Простой скрипт для очистки всех данных из БД kbju_bot.db через Python ===

REM Проверяем наличие файла БД
if not exist "kbju_bot.db" (
    echo ❌ База данных kbju_bot.db не найдена!
    pause
    exit /b 1
)

REM Очищаем все таблицы через Python
python -c "import sqlite3; db='kbju_bot.db'; con=sqlite3.connect(db); cur=con.cursor(); [cur.execute(f'DELETE FROM {t}') for t in ['users','user_records','user_food_preferences']]; con.commit(); con.close(); print('✅ Все данные в базе данных удалены!')"

pause знк