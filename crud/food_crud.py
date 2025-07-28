from sqlalchemy.orm import Session
from models.tables import UserFoodPreferences
import logging

def get_food_preferences(db: Session, telegram_id: int):
    logging.info(f"get_food_preferences: telegram_id={telegram_id}")
    try:
        return db.query(UserFoodPreferences).filter(UserFoodPreferences.telegram_id == telegram_id).first()
    except Exception as e:
        logging.error(f"get_food_preferences error: {e}")
        db.rollback()
        return None

def create_or_update_food_preferences(db: Session, telegram_id: int, likes_raw: str = None, dislikes_raw: str = None):
    logging.info(f"create_or_update_food_preferences: telegram_id={telegram_id}, likes_raw={likes_raw}, dislikes_raw={dislikes_raw}")
    try:
        existing_prefs = get_food_preferences(db, telegram_id)
        
        if existing_prefs:
            # UPDATE
            if likes_raw is not None:
                existing_prefs.likes_raw = likes_raw.strip() if likes_raw else ""
            if dislikes_raw is not None:
                existing_prefs.dislikes_raw = dislikes_raw.strip() if dislikes_raw else ""
            db.commit()
            db.refresh(existing_prefs)
            logging.info(f"create_or_update_food_preferences: updated id={existing_prefs.id}")
            return existing_prefs
        else:
            # CREATE
            new_prefs = UserFoodPreferences(
                telegram_id=telegram_id,
                likes_raw=likes_raw.strip() if likes_raw else "",
                dislikes_raw=dislikes_raw.strip() if dislikes_raw else ""
            )
            db.add(new_prefs)
            db.commit()
            db.refresh(new_prefs)
            logging.info(f"create_or_update_food_preferences: created id={new_prefs.id}")
            return new_prefs
    except Exception as e:
        logging.error(f"create_or_update_food_preferences error: {e}")
        db.rollback()
        return None 