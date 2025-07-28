from sqlalchemy.orm import Session
from models.tables import UserRecord
from datetime import date
from sqlalchemy import and_
import logging

def get_user_records(db: Session, telegram_id: int):
    logging.info(f"get_user_records: telegram_id={telegram_id}")
    try:
        return db.query(UserRecord).filter(UserRecord.telegram_id == telegram_id).all()
    except Exception as e:
        logging.error(f"get_user_records error: {e}")
        db.rollback()
        return []

def get_latest_record(db: Session, telegram_id: int):
    logging.info(f"get_latest_record: telegram_id={telegram_id}")
    try:
        return db.query(UserRecord).filter(UserRecord.telegram_id == telegram_id).order_by(UserRecord.date.desc()).first()
    except Exception as e:
        logging.error(f"get_latest_record error: {e}")
        db.rollback()
        return None

def create_or_update_record(db: Session, telegram_id: int, record_date: date, **kwargs):
    logging.info(f"create_or_update_record: telegram_id={telegram_id}, record_date={record_date}, kwargs={kwargs}")
    try:
        # Проверяем, есть ли запись на эту дату
        existing_record = db.query(UserRecord).filter(
            and_(UserRecord.telegram_id == telegram_id, UserRecord.date == record_date)
        ).first()
        
        if existing_record:
            # UPDATE если ввод в тот же день
            for key, value in kwargs.items():
                if hasattr(existing_record, key) and value is not None:
                    setattr(existing_record, key, value)
            db.commit()
            db.refresh(existing_record)
            logging.info(f"create_or_update_record: updated record id={existing_record.id}")
            return existing_record
        else:
            # INSERT если ввод в другой день
            # Фильтруем None значения
            filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            new_record = UserRecord(
                telegram_id=telegram_id,
                date=record_date,
                **filtered_kwargs
            )
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
            logging.info(f"create_or_update_record: created record id={new_record.id}")
            return new_record
    except Exception as e:
        logging.error(f"create_or_update_record error: {e}")
        db.rollback()
        return None 