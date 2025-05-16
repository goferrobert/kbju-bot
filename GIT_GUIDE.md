## GitHub репозиторий для проекта КБЖУ Бот

- **Адрес:** [https://github.com/goferrobert/kbju-bot.git](https://github.com/goferrobert/kbju-bot.git)
- **Проект:** Telegram бот для расчёта КБЖУ и запуска воронки консультаций

---

### Состояние репозитория:
- `main` — основная (prod) ветка
- `dev` — ветка для разработки
- Настроено локальное Git-репо
- `.gitignore` добавлен
- Первый коммит сделан
- Репозиторий связан с GitHub

---

### Команды терминала (актуальные):

#### 🔹 Настройка GitHub репозитория
```bash
git remote add origin https://github.com/goferrobert/kbju-bot.git
git branch -M main
git push -u origin main
```

#### 🔹 Создание ветки dev и переключение
```bash
git checkout -b dev     # создать ветку и перейти в неё
git push -u origin dev  # отправить ветку на GitHub
```

#### 🔹 Переключение между ветками
```bash
git checkout main   # перейти на основную ветку
git checkout dev    # перейти на ветку для разработки
```

#### 🔹 Стандартная работа в dev
```bash
git add .
git commit -m "Комментарий"
git push
```

#### 🔹 Слияние dev → main (в прод)
```bash
git checkout main
git pull                  # обновить main перед слиянием (если нужно)
git merge dev             # влить изменения из dev
git push                  # отправить изменения на GitHub
```

#### 🔹 Если на GitHub уже были файлы (чтобы не было конфликта)
```bash
git pull --rebase origin main
```

#### 🔹 Временное сохранение несохранённого кода
```bash
git stash          # спрятать текущие изменения
# ...переключиться на другую ветку, сделать что нужно...
git stash apply    # вернуть изменения обратно
```