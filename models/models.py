from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan")

class Food(Base):
    __tablename__ = "foods"

    food_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbohydrates = Column(Float, nullable=False)

    # Relationships
    food_logs = relationship("FoodLog", back_populates="food")

class FoodLog(Base):
    __tablename__ = "food_logs"

    foodlog_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.food_id", ondelete="SET NULL"), nullable=True)
    date = Column(Date, nullable=False, default=date.today)
    quantity = Column(Float, nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbohydrates = Column(Float, nullable=False)

    # Relationships
    user = relationship("User", back_populates="food_logs")
    food = relationship("Food", back_populates="food_logs")

class Progress(Base):
    __tablename__ = "progress"

    progress_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    weight = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    calorie_intake = Column(Integer, nullable=False)

    # Relationships
    user = relationship("User", back_populates="progress_records") 