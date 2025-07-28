from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    telegram_id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    sex = Column(String)  # 'male' / 'female'
    date_of_birth = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    records = relationship("UserRecord", back_populates="user")
    food_preferences = relationship("UserFoodPreferences", back_populates="user")

class UserRecord(Base):
    __tablename__ = "user_records"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, ForeignKey("users.telegram_id"))
    date = Column(Date)
    weight = Column(Float)
    waist = Column(Float)
    neck = Column(Float)
    hip = Column(Float)  # только у женщин
    # Динамические и расчетные параметры:
    height = Column(Integer)
    goal = Column(String)
    steps = Column(String)
    sport_type = Column(String)
    sport_freq = Column(String)
    step_multiplier = Column(Float)
    bodyfat = Column(Float)
    # Relationship
    user = relationship("User", back_populates="records")

class UserFoodPreferences(Base):
    __tablename__ = "user_food_preferences"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, ForeignKey("users.telegram_id"))
    likes_raw = Column(Text)
    dislikes_raw = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationship
    user = relationship("User", back_populates="food_preferences") 