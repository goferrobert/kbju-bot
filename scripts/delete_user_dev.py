# scripts/delete_user_dev.py
# Удаляет пользователя и связанные записи из dev-базы
# ruff: noqa: E402

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.session import SessionLocal
from app.db.models import User, UserRecord, UserPreference
from core.config import settings

if settings.MODE != "DEV":
    print("⛔ Удаление запрещено: не DEV-режим.")
    exit()

def delete_user_by_telegram_id(telegram_id: int):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            print("❌ Пользователь не найден.")
            return

        deleted_records = session.query(UserRecord).filter_by(user_id=user.id).delete()
        deleted_prefs = session.query(UserPreference).filter_by(user_id=user.id).delete()

        session.delete(user)
        session.commit()

        print(f"✅ Удалён пользователь {telegram_id}.\n📦 Записей: {deleted_records}, Предпочтений: {deleted_prefs}")

    except Exception as e:
        print(f"❌ Ошибка при удалении пользователя: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    telegram_id_to_delete = 285835433  # просто передаём число напрямую
    delete_user_by_telegram_id(telegram_id_to_delete)
