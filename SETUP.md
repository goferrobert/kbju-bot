# 🚀 Подробная инструкция по установке KBJU Bot

Полное руководство по установке, настройке и запуску Telegram бота для расчета КБЖУ и процента жира.

## 📋 Предварительные требования

### **Системные требования:**
- **ОС:** Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python:** 3.8 или выше
- **RAM:** Минимум 512MB
- **Диск:** 100MB свободного места
- **Интернет:** Стабильное подключение

### **Необходимые инструменты:**
- **Git** - для клонирования репозитория
- **Python pip** - для установки зависимостей
- **Текстовый редактор** - VS Code, PyCharm, или любой другой

## 🔧 Пошаговая установка

### **Шаг 1: Подготовка системы**

#### Windows:
```bash
# Проверка версии Python
python --version

# Установка Git (если не установлен)
# Скачайте с https://git-scm.com/download/win

# Создание рабочей папки
mkdir C:\Projects
cd C:\Projects
```

#### macOS/Linux:
```bash
# Проверка версии Python
python3 --version

# Установка Git (если не установлен)
# macOS: brew install git
# Ubuntu: sudo apt install git

# Создание рабочей папки
mkdir ~/Projects
cd ~/Projects
```

### **Шаг 2: Клонирование репозитория**

```bash
# Клонирование проекта
git clone <repository-url> Telegram
cd Telegram

# Проверка структуры проекта
ls -la
```

### **Шаг 3: Создание виртуального окружения**

#### Windows:
```bash
# Создание виртуального окружения
python -m venv .venv

# Активация виртуального окружения
.venv\Scripts\activate

# Проверка активации (должен показать путь к .venv)
where python
```

#### macOS/Linux:
```bash
# Создание виртуального окружения
python3 -m venv .venv

# Активация виртуального окружения
source .venv/bin/activate

# Проверка активации (должен показать путь к .venv)
which python
```

### **Шаг 4: Установка зависимостей**

```bash
# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt

# Проверка установки
pip list
```

### **Шаг 5: Настройка конфигурации**

```bash
# Копирование примера конфигурации
cp env.example .env

# Редактирование конфигурации
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env
```

#### Содержимое файла .env:
```env
# Токен вашего Telegram бота
BOT_TOKEN=your_telegram_bot_token_here

# URL базы данных (SQLite по умолчанию)
DATABASE_URL=sqlite:///kbju_bot.db

# Уровень логирования (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Дополнительные настройки (опционально)
# ADMIN_USER_ID=your_telegram_id
# DEBUG_MODE=False
```

### **Шаг 6: Получение токена бота**

1. **Откройте Telegram** и найдите @BotFather
2. **Отправьте команду** `/newbot`
3. **Введите имя бота** (например: "My KBJU Bot")
4. **Введите username** (например: "my_kbju_bot")
5. **Скопируйте токен** и вставьте в файл .env

### **Шаг 7: Инициализация базы данных**

```bash
# Создание базы данных и таблиц
python scripts/init_database.py

# Проверка создания файла БД
ls -la *.db
```

### **Шаг 8: Тестирование установки**

```bash
# Проверка синтаксиса основного файла
python -m py_compile main.py

# Проверка импорта модулей
python -c "import handlers.measurements_handlers; print('OK')"
python -c "import utils.calculations; print('OK')"
python -c "import utils.validators; print('OK')"

# Создание тестовых данных (опционально)
python scripts/create_test_data.py
```

## 🚀 Запуск бота

### **Первый запуск:**

```bash
# Убедитесь, что виртуальное окружение активировано
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Запуск бота
python main.py
```

### **Проверка работы:**

1. **Откройте Telegram** и найдите вашего бота
2. **Отправьте команду** `/start`
3. **Следуйте инструкциям** для регистрации
4. **Проверьте все функции** бота

### **Остановка бота:**

```bash
# Нажмите Ctrl+C в терминале
# Или закройте терминал
```

## 🔧 Настройка для разработки

### **Структура проекта для разработчиков:**

```
Telegram/
├── handlers/                 # Обработчики Telegram сообщений
│   ├── measurements_handlers.py  # ✅ Оптимизировано (350 строк)
│   ├── user_info_handlers.py     # Обработчики пользовательской информации
│   ├── food_handlers.py          # Обработчики питания
│   ├── menu_handlers.py          # Обработчики меню
│   └── start_handlers.py         # Обработчики старта
├── utils/                   # Утилиты и вспомогательные функции
│   ├── calculations.py      # ✅ Математические расчеты (666 строк)
│   ├── texts.py            # ✅ Оптимизировано (400 строк)
│   ├── validators.py       # ✅ Оптимизировано (180 строк)
│   ├── buttons.py          # Клавиатуры и кнопки
│   └── progress.py         # Анализ прогресса
├── models/                 # Модели базы данных
│   ├── database.py         # Настройки подключения
│   └── tables.py           # Определения таблиц
├── crud/                   # Операции с базой данных
│   ├── user_crud.py        # CRUD для пользователей
│   ├── record_crud.py      # CRUD для записей измерений
│   └── food_crud.py        # CRUD для питания
├── states/                 # Состояния FSM
│   └── fsm_states.py       # Определения состояний
├── scripts/                # Скрипты для управления
│   ├── init_database.py    # Инициализация БД
│   ├── migrate_database.py # Миграции БД
│   ├── create_test_data.py # Создание тестовых данных
│   └── clear_test_data.py  # Очистка тестовых данных
├── main.py                 # Главный файл бота
├── config.py               # Конфигурация
└── requirements.txt        # Зависимости
```

### **Команды для разработки:**

```bash
# Создание тестовых данных
python scripts/create_test_data.py

# Очистка тестовых данных
python scripts/clear_test_data.py

# Проверка синтаксиса всех файлов
find . -name "*.py" -exec python -m py_compile {} \;

# Запуск с отладкой
python -u main.py

# Проверка импортов
python -c "import sys; sys.path.append('.'); import handlers, utils, models, crud; print('All modules imported successfully')"
```

## 🛠️ Устранение неполадок

### **Частые проблемы:**

#### **1. Ошибка "ModuleNotFoundError":**
```bash
# Решение: Активируйте виртуальное окружение
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
```

#### **2. Ошибка "No module named 'aiogram'":**
```bash
# Решение: Установите зависимости
pip install -r requirements.txt
```

#### **3. Ошибка "Invalid token":**
```bash
# Решение: Проверьте токен в файле .env
# Убедитесь, что токен скопирован полностью
```

#### **4. Ошибка "Database locked":**
```bash
# Решение: Закройте все процессы Python
# Windows: taskkill /f /im python.exe
# macOS/Linux: pkill python
```

#### **5. Ошибка "Permission denied":**
```bash
# Решение: Проверьте права доступа к папке
# Windows: Запустите от имени администратора
# macOS/Linux: chmod +x main.py
```

### **Проверка логов:**

```bash
# Просмотр логов в реальном времени
# Windows: Get-Content bot.log -Wait
# macOS/Linux: tail -f bot.log

# Поиск ошибок в логах
grep -i error bot.log
grep -i exception bot.log
```

## 🔒 Безопасность

### **Рекомендации по безопасности:**

1. **Никогда не публикуйте токен** в публичных репозиториях
2. **Используйте .env файл** для хранения секретов
3. **Регулярно обновляйте зависимости** для исправления уязвимостей
4. **Ограничьте доступ** к серверу с ботом
5. **Настройте бэкапы** базы данных

### **Настройка файрвола:**

```bash
# Ограничение доступа к портам (если используется веб-хук)
# Windows: netsh advfirewall firewall add rule name="Telegram Bot" dir=in action=allow protocol=TCP localport=8443
# macOS/Linux: ufw allow 8443
```

## 📊 Мониторинг и обслуживание

### **Автоматический запуск:**

#### Windows (Task Scheduler):
```batch
@echo off
cd /d C:\Projects\Telegram
call .venv\Scripts\activate
python main.py
```

#### macOS/Linux (systemd):
```ini
[Unit]
Description=KBJU Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/Projects/Telegram
Environment=PATH=/home/your_username/Projects/Telegram/.venv/bin
ExecStart=/home/your_username/Projects/Telegram/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **Бэкапы базы данных:**

```bash
# Создание бэкапа
cp kbju_bot.db kbju_bot_backup_$(date +%Y%m%d_%H%M%S).db

# Автоматический бэкап (cron)
# 0 2 * * * cp /path/to/kbju_bot.db /backup/kbju_bot_$(date +\%Y\%m\%d).db
```

### **Обновление бота:**

```bash
# Остановка бота
# Ctrl+C или systemctl stop kbju-bot

# Обновление кода
git pull origin main

# Обновление зависимостей
pip install -r requirements.txt

# Перезапуск бота
python main.py
```

## 🎯 Оптимизация производительности

### **Настройки для высоких нагрузок:**

```python
# config.py
import os

# Настройки для высоких нагрузок
MAX_CONNECTIONS = 100
POOL_SIZE = 20
MAX_OVERFLOW = 30

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

### **Мониторинг ресурсов:**

```bash
# Мониторинг использования памяти
# Windows: tasklist /fi "imagename eq python.exe"
# macOS/Linux: ps aux | grep python

# Мониторинг дискового пространства
df -h

# Мониторинг логов
tail -f bot.log | grep -E "(ERROR|WARNING)"
```

## 📚 Дополнительные ресурсы

### **Полезные ссылки:**
- [aiogram документация](https://docs.aiogram.dev/)
- [SQLAlchemy документация](https://docs.sqlalchemy.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### **Сообщество:**
- [GitHub Issues](https://github.com/your-repo/issues)
- [Telegram поддержка](https://t.me/dryuzefovna)
- [Discussions](https://github.com/your-repo/discussions)

---

**🎉 Поздравляем! Ваш KBJU Bot успешно установлен и готов к работе!**

**📞 Если у вас возникли вопросы, обратитесь к разделу "Устранение неполадок" или свяжитесь с поддержкой.** 