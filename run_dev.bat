@echo off
echo 🔧 Запуск DEV-бота
copy dev.env .env > nul
call .venv\Scripts\python.exe bot.py
del .env
pause
