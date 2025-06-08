from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any

from models import User, Food, FoodLog, Progress
from schemas import UserCreate, FoodLogCreate, ProgressCreate, UserUpdate

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-here"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# User operations
def create_user(db: Session, user: UserCreate) -> User:
    try:
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=get_password_hash(user.password),
            height=user.height,
            weight=user.weight,
            goal=user.goal
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    # Get the user
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        return None
    
    # Check if email is being changed and if it's already taken
    if user_update.email != db_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user and existing_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user"
            )
    
    # Update user fields
    db_user.name = user_update.name
    db_user.email = user_update.email
    db_user.height = user_update.height
    db_user.weight = user_update.weight
    db_user.goal = user_update.goal
    
    # Update password if provided
    if user_update.password:
        db_user.password_hash = get_password_hash(user_update.password)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating user profile"
        )

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

# Food operations
def get_foods(db: Session, skip: int = 0, limit: int = 100) -> List[Food]:
    return db.query(Food).offset(skip).limit(limit).all()

# FoodLog operations
def create_food_log(db: Session, food_log: FoodLogCreate) -> FoodLog:
    food = db.query(Food).filter(Food.food_id == food_log.food_id).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )
    
    db_food_log = FoodLog(
        user_id=food_log.user_id,
        food_id=food_log.food_id,
        date=food_log.date,
        quantity=food_log.quantity,
        calories=int(food.calories * food_log.quantity),
        protein=food.protein * food_log.quantity,
        fat=food.fat * food_log.quantity,
        carbohydrates=food.carbohydrates * food_log.quantity
    )
    db.add(db_food_log)
    db.commit()
    db.refresh(db_food_log)
    return db_food_log

def get_user_foodlogs(db: Session, user_id: int) -> List[FoodLog]:
    # Join with Food table to get food names
    foodlogs = db.query(
        FoodLog, Food.name.label("food_name")
    ).join(
        Food, FoodLog.food_id == Food.food_id
    ).filter(
        FoodLog.user_id == user_id
    ).all()
    
    # Convert to list of dictionaries with food names included
    result = []
    for log, food_name in foodlogs:
        log_dict = {
            "foodlog_id": log.foodlog_id,
            "user_id": log.user_id,
            "food_id": log.food_id,
            "food_name": food_name,  # Include food name
            "date": log.date.strftime('%Y-%m-%d') if isinstance(log.date, date) else log.date,
            "quantity": log.quantity,
            "calories": log.calories,
            "protein": log.protein,
            "fat": log.fat,
            "carbohydrates": log.carbohydrates
        }
        result.append(log_dict)
    
    return result

# Progress operations
def create_progress(db: Session, progress: ProgressCreate) -> Progress:
    db_progress = Progress(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def get_user_progress(db: Session, user_id: int) -> List[Progress]:
    return db.query(Progress).filter(Progress.user_id == user_id).all()

def seed_foods(db: Session):
    foods = [
    {"name": "Egg", "calories": 78, "protein": 6.3, "fat": 5.3, "carbohydrates": 0.6},
    {"name": "Chicken Breast", "calories": 165, "protein": 31, "fat": 3.6, "carbohydrates": 0},
    {"name": "Apple", "calories": 95, "protein": 0.5, "fat": 0.3, "carbohydrates": 25},
    {"name": "Rice (Cooked)", "calories": 130, "protein": 2.7, "fat": 0.3, "carbohydrates": 28},
    {"name": "Broccoli", "calories": 55, "protein": 3.7, "fat": 0.6, "carbohydrates": 11.2},
    {"name": "Banana", "calories": 105, "protein": 1.3, "fat": 0.3, "carbohydrates": 27},
    {"name": "Salmon", "calories": 208, "protein": 20, "fat": 13, "carbohydrates": 0},
    {"name": "Almonds", "calories": 164, "protein": 6, "fat": 14, "carbohydrates": 6},
    {"name": "Milk (1 cup)", "calories": 103, "protein": 8, "fat": 2.4, "carbohydrates": 12},
    {"name": "Oats", "calories": 150, "protein": 5, "fat": 2.5, "carbohydrates": 27},
    {"name": "Beef (Ground, Lean)", "calories": 250, "protein": 26, "fat": 17, "carbohydrates": 0},
    {"name": "Sweet Potato", "calories": 86, "protein": 1.6, "fat": 0.1, "carbohydrates": 20},
    {"name": "Tofu", "calories": 76, "protein": 8, "fat": 4.8, "carbohydrates": 1.9},
    {"name": "Peanut Butter", "calories": 188, "protein": 8, "fat": 16, "carbohydrates": 6},
    {"name": "Greek Yogurt (Plain)", "calories": 100, "protein": 10, "fat": 0, "carbohydrates": 6},
    {"name": "Quinoa (Cooked)", "calories": 120, "protein": 4.1, "fat": 1.9, "carbohydrates": 21.3},
    {"name": "Avocado", "calories": 160, "protein": 2, "fat": 15, "carbohydrates": 9},
    {"name": "Carrot", "calories": 41, "protein": 0.9, "fat": 0.2, "carbohydrates": 10},
    {"name": "Orange", "calories": 62, "protein": 1.2, "fat": 0.2, "carbohydrates": 15.4},
    {"name": "Cottage Cheese", "calories": 98, "protein": 11, "fat": 4.3, "carbohydrates": 3.4},
    {"name": "Lentils (Cooked)", "calories": 116, "protein": 9, "fat": 0.4, "carbohydrates": 20},
    {"name": "Spinach", "calories": 23, "protein": 2.9, "fat": 0.4, "carbohydrates": 3.6},
    {"name": "Blueberries", "calories": 84, "protein": 1.1, "fat": 0.5, "carbohydrates": 21.5},
    {"name": "Whole Wheat Bread (1 slice)", "calories": 69, "protein": 3.6, "fat": 1.1, "carbohydrates": 12},
    {"name": "Cheddar Cheese", "calories": 113, "protein": 7, "fat": 9.3, "carbohydrates": 0.4},
    {"name": "Pumpkin Seeds", "calories": 151, "protein": 7, "fat": 13, "carbohydrates": 5},
    {"name": "Cucumber", "calories": 16, "protein": 0.7, "fat": 0.1, "carbohydrates": 3.6},
    {"name": "Shrimp", "calories": 99, "protein": 24, "fat": 0.3, "carbohydrates": 0.2},
    {"name": "Green Beans", "calories": 31, "protein": 1.8, "fat": 0.1, "carbohydrates": 7},
    {"name": "Pineapple", "calories": 82, "protein": 0.9, "fat": 0.2, "carbohydrates": 22}
]

    for food in foods:
        existing = db.query(Food).filter(Food.name == food["name"]).first()
        if not existing:
            db_food = Food(**food)
            db.add(db_food)
    db.commit() 