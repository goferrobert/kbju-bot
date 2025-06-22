from sqlalchemy.orm import Session

from .session import SessionLocal
from .models import User


def get_user_by_telegram_id(telegram_id: int) -> User | None:
    with SessionLocal() as session:
        return session.query(User).filter_by(telegram_id=telegram_id).first()


def create_user(**kwargs) -> User:
    with SessionLocal() as session:
        user = User(**kwargs)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def update_user(
    telegram_id: int,
    username: str,
    first_name: str,
    last_name: str | None,
    name: str,
    sex: str,
    date_of_birth,
    height: float,
) -> None:
    with SessionLocal() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.name = name
            user.gender = sex
            user.birth_date = date_of_birth
            user.height = height
            session.commit()
