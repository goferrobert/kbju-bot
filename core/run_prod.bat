@echo off
echo 🚀 Запуск PROD-бота
copy prod.env .env > nul
call .venv\Scripts\python.exe bot.py
del .env
pause
