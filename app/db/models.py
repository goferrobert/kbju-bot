from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    name = Column(String)
    date_of_birth = Column(Date)
    height = Column(Float)
    sex = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    records = relationship("UserRecord", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")

class UserRecord(Base):
    __tablename__ = "user_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    weight = Column(Float)
    body_fat = Column(Float)
    activity_level = Column(Float)

    calories = Column(Integer)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)

    goal_type = Column(String)

    step_level = Column(Integer)        # уровень шагов (1-5)
    sport_type = Column(String)         # тип тренировок (силовые, кардио, нет)
    sport_freq = Column(Integer)        # тренировки в неделю (0-7)

    user = relationship("User", back_populates="records")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preference_type = Column(String)  # "like" or "dislike"
    item = Column(String)

    user = relationship("User", back_populates="preferences")
