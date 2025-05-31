from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import UserRecord
from app.db.session import SessionLocal

def get_or_create_today_record(user_id: int, db: Session = None) -> UserRecord:
    created_inside = False
    if db is None:
        db = SessionLocal()
        created_inside = True

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    record = (
        db.query(UserRecord)
        .filter(UserRecord.user_id == user_id)
        .filter(UserRecord.created_at >= today_start)
        .first()
    )

    if record is None:
        record = UserRecord(user_id=user_id)
        db.add(record)
        db.commit()
        db.refresh(record)

    if created_inside:
        db.close()

    return record

def get_latest_record(user_id: int, db: Session = None) -> UserRecord:
    created_inside = False
    if db is None:
        db = SessionLocal()
        created_inside = True

    record = (
        db.query(UserRecord)
        .filter(UserRecord.user_id == user_id)
        .order_by(UserRecord.created_at.desc())
        .first()
    )

    if created_inside:
        db.close()

    return record
