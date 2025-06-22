# scripts/init_dev_db.py
# Создаёт dev-базу данных с нуля
# ruff: noqa: E402

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.session import init_db

if __name__ == "__main__":
    init_db()
    print("🛠️ DEV-База данных успешно инициализирована ✅")
