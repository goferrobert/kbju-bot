@echo off
echo Останавливаем предыдущие экземпляры бота...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Запускаем бота...
python main.py
pause 