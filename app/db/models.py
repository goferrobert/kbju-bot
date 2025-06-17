from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """User model for storing user information."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=False)
    gender = Column(String, nullable=False)  # 'male' or 'female'
    height = Column(Float, nullable=False)  # in cm
    work_type = Column(String, nullable=True)  # sedentary, standing, moderate, heavy
    chronic_diseases = Column(JSON, nullable=True)  # list of diseases
    allergies = Column(JSON, nullable=True)  # list of allergies
    food_preferences = Column(JSON, nullable=True)  # list of preferred foods
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    records = relationship("UserRecord", back_populates="user")
    goals = relationship("UserGoal", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    notifications = relationship("UserNotification", back_populates="user")

class UserRecord(Base):
    """Model for storing user measurements and activity data."""
    __tablename__ = 'user_records'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    weight = Column(Float, nullable=False)  # in kg
    waist = Column(Float, nullable=True)  # in cm
    neck = Column(Float, nullable=True)  # in cm
    body_fat = Column(Float, nullable=True)  # percentage
    steps = Column(Integer, nullable=True)
    bmr = Column(Float, nullable=True)  # basal metabolic rate
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="records")
    activities = relationship("UserActivity", back_populates="record")

class UserActivity(Base):
    """Model for storing user training activities."""
    __tablename__ = 'user_activities'

    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, ForeignKey('user_records.id'), nullable=False)
    activity_type = Column(String, nullable=False)  # weight, cardio, functional, etc.
    duration = Column(Integer, nullable=True)  # in minutes
    intensity = Column(String, nullable=True)  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    record = relationship("UserRecord", back_populates="activities")

class UserGoal(Base):
    """Model for storing user goals."""
    __tablename__ = 'user_goals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    body_type = Column(String, nullable=False)  # athletic, slim, healthy
    target_weight = Column(Float, nullable=True)  # in kg
    target_body_fat = Column(Float, nullable=True)  # percentage
    calories = Column(Integer, nullable=True)  # daily calories
    proteins = Column(Integer, nullable=True)  # daily proteins in grams
    fats = Column(Integer, nullable=True)  # daily fats in grams
    carbs = Column(Integer, nullable=True)  # daily carbs in grams
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="goals")

class UserSettings(Base):
    """Model for storing user settings."""
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    language = Column(String, default='ru')
    units = Column(String, default='metric')  # metric or imperial
    theme = Column(String, default='light')  # light or dark
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settings")

class UserNotification(Base):
    """Model for storing user notifications."""
    __tablename__ = 'user_notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String, nullable=False)  # weight, steps, sport, nutrition
    time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")
