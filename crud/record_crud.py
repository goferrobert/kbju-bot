from sqlalchemy.orm import Session
from models.tables import UserRecord
from datetime import date
from typing import List, Optional
import logging

def create_or_update_record(
    db: Session,
    telegram_id: int,
    record_date: date,
    weight: float,
    waist: float,
    neck: float,
    hip: Optional[float] = None,
    chest: Optional[float] = None,
    bicep: Optional[float] = None,
    thigh: Optional[float] = None,
    wrist: Optional[float] = None,
    calf: Optional[float] = None,
    forearm: Optional[float] = None,
    abdomen: Optional[float] = None,
    sleep_hours: Optional[float] = None,
    stress_level: Optional[str] = None,
    steps: str = "8000-10000",
    sport_type: str = "none",
    sport_freq: str = "0",
    step_multiplier: float = 1.2,
    height: int = 170,
    goal: str = "maintain",
    bodyfat: Optional[float] = None,
    bmi: Optional[float] = None,
    lbm: Optional[float] = None,
    whr: Optional[float] = None,
    bmr: Optional[int] = None,
    tdee: Optional[int] = None,
    metabolic_age: Optional[int] = None,
    body_type: Optional[str] = None,
    bodyfat_category: Optional[str] = None
) -> Optional[UserRecord]:
    """
    Создать новую запись или обновить существующую
    """
    # Проверяем, есть ли уже запись на эту дату
    existing_record = db.query(UserRecord).filter(
        UserRecord.telegram_id == telegram_id,
        UserRecord.date == record_date
    ).first()
    
    if existing_record:
        # Обновляем существующую запись
        existing_record.weight = weight
        existing_record.waist = waist
        existing_record.neck = neck
        existing_record.hip = hip
        existing_record.chest = chest
        existing_record.bicep = bicep
        existing_record.thigh = thigh
        existing_record.wrist = wrist
        existing_record.calf = calf
        existing_record.forearm = forearm
        existing_record.abdomen = abdomen
        existing_record.sleep_hours = sleep_hours
        existing_record.stress_level = stress_level
        existing_record.steps = steps
        existing_record.sport_type = sport_type
        existing_record.sport_freq = sport_freq
        existing_record.step_multiplier = step_multiplier
        existing_record.height = height
        existing_record.goal = goal
        existing_record.bodyfat = bodyfat
        existing_record.bmi = bmi
        existing_record.lbm = lbm
        existing_record.whr = whr
        existing_record.bmr = bmr
        existing_record.tdee = tdee
        existing_record.metabolic_age = metabolic_age
        existing_record.body_type = body_type
        existing_record.bodyfat_category = bodyfat_category
        
        db.commit()
        return existing_record
    else:
        # Создаем новую запись
        new_record = UserRecord(
            telegram_id=telegram_id,
            date=record_date,
            weight=weight,
            waist=waist,
            neck=neck,
            hip=hip,
            chest=chest,
            bicep=bicep,
            thigh=thigh,
            wrist=wrist,
            calf=calf,
            forearm=forearm,
            abdomen=abdomen,
            sleep_hours=sleep_hours,
            stress_level=stress_level,
            steps=steps,
            sport_type=sport_type,
            sport_freq=sport_freq,
            step_multiplier=step_multiplier,
            height=height,
            goal=goal,
            bodyfat=bodyfat,
            bmi=bmi,
            lbm=lbm,
            whr=whr,
            bmr=bmr,
            tdee=tdee,
            metabolic_age=metabolic_age,
            body_type=body_type,
            bodyfat_category=bodyfat_category
        )
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record

def get_latest_record(db: Session, telegram_id: int) -> Optional[UserRecord]:
    """
    Получить последнюю запись пользователя
    """
    return db.query(UserRecord).filter(
        UserRecord.telegram_id == telegram_id
    ).order_by(UserRecord.date.desc()).first()

def get_user_records(db: Session, telegram_id: int) -> List[UserRecord]:
    """
    Получить все записи пользователя, отсортированные по дате
    """
    return db.query(UserRecord).filter(
        UserRecord.telegram_id == telegram_id
    ).order_by(UserRecord.date.desc()).all()

def get_records_by_date_range(
    db: Session, 
    telegram_id: int, 
    start_date: date, 
    end_date: date
) -> List[UserRecord]:
    """
    Получить записи пользователя за определенный период
    """
    return db.query(UserRecord).filter(
        UserRecord.telegram_id == telegram_id,
        UserRecord.date >= start_date,
        UserRecord.date <= end_date
    ).order_by(UserRecord.date.desc()).all()

def delete_record(db: Session, record_id: int) -> bool:
    """
    Удалить запись по ID
    """
    record = db.query(UserRecord).filter(UserRecord.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

def delete_user_records(db: Session, telegram_id: int) -> int:
    """
    Удалить все записи пользователя
    Возвращает количество удаленных записей
    """
    logging.info(f"delete_user_records: telegram_id={telegram_id}")
    try:
        records = db.query(UserRecord).filter(UserRecord.telegram_id == telegram_id).all()
        count = len(records)
        
        for record in records:
            db.delete(record)
        
        db.commit()
        logging.info(f"delete_user_records: deleted {count} records for user {telegram_id}")
        return count
    except Exception as e:
        logging.error(f"delete_user_records error: {e}")
        db.rollback()
        return 0 