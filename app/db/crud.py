from datetime import date
from sqlalchemy.orm import Session
from app.db.models import User, UserPreference
from app.db.session import SessionLocal

def get_user_by_telegram_id(telegram_id: int) -> User:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        return user
    finally:
        db.close()

def create_user(
    telegram_id: int,
    username: str,
    first_name: str,
    last_name: str,
    name: str,
    sex: str,
    date_of_birth: date,
    height: float,
) -> User:
    db = SessionLocal()
    try:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            name=name,
            sex=sex,
            date_of_birth=date_of_birth,
            height=height,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

def update_user(
    telegram_id: int,
    username: str,
    first_name: str,
    last_name: str,
    name: str,
    sex: str,
    date_of_birth: date,
    height: float,
) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            return False

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.name = name
        user.sex = sex
        user.date_of_birth = date_of_birth
        user.height = height

        db.commit()
        return True
    finally:
        db.close()

def get_user_preferences(user_id: int, db: Session) -> dict:
    prefs = db.query(UserPreference).filter_by(user_id=user_id).all()
    return {p.item: p.preference_type for p in prefs}
