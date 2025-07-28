from sqlalchemy.orm import Session
from models.tables import User
from datetime import datetime
import logging

def get_user(db: Session, telegram_id: int):
    logging.info(f"get_user: telegram_id={telegram_id}")
    try:
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    except Exception as e:
        logging.error(f"get_user error: {e}")
        db.rollback()
        return None

def create_user(db: Session, telegram_id: int, username: str = None, 
                first_name: str = None, last_name: str = None, **kwargs):
    logging.info(f"create_user: telegram_id={telegram_id}, username={username}, first_name={first_name}, last_name={last_name}")
    try:
        db_user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logging.info(f"create_user: created user id={db_user.telegram_id}")
        return db_user
    except Exception as e:
        logging.error(f"create_user error: {e}")
        db.rollback()
        return None

def update_user(db: Session, telegram_id: int, **kwargs):
    logging.info(f"update_user: telegram_id={telegram_id}, kwargs={kwargs}")
    try:
        db_user = get_user(db, telegram_id)
        if db_user:
            for key, value in kwargs.items():
                if hasattr(db_user, key):
                    setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
            logging.info(f"update_user: updated user id={db_user.telegram_id}")
        return db_user
    except Exception as e:
        logging.error(f"update_user error: {e}")
        db.rollback()
        return None

def user_exists(db: Session, telegram_id: int):
    logging.info(f"user_exists: telegram_id={telegram_id}")
    try:
        return db.query(User).filter(User.telegram_id == telegram_id).first() is not None
    except Exception as e:
        logging.error(f"user_exists error: {e}")
        db.rollback()
        return False 