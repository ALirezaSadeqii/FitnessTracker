from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import pymysql
import logging

from models import User, Food, FoodLog, Progress
from schemas import UserCreate, FoodLogCreate, ProgressCreate, UserUpdate

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-here"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database URL (placeholder - replace with your actual database URL)
DATABASE_URL = "mysql+pymysql://fitness_user:Fitness123!@localhost:3306/fitness_db"
print(f'Connecting to database with: {DATABASE_URL}')

def create_database_if_not_exists():
    print('Checking/creating database...')
    connection = pymysql.connect(
        host="localhost",
        user="fitness_user",
        password="Fitness123!",
        port=3306
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS fitness_db")
        connection.commit()
        print('Database checked/created successfully.')
    except Exception as e:
        print(f'Error creating database: {e}')
    finally:
        connection.close()

create_database_if_not_exists()

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Create all tables
Base.metadata.create_all(bind=engine)

# Database session dependency
def get_db():
    """
    Dependency function that yields database sessions.
    Usage in FastAPI:
    @app.get("/")
    def read_items(db: Session = Depends(get_db)):
        ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager for database sessions.
    Usage:
    with get_db_context() as db:
        db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

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

# Food operations
def get_foods(db: Session, skip: int = 0, limit: int = 100) -> List[Food]:
    return db.query(Food).offset(skip).limit(limit).all()

# FoodLog operations
def create_food_log(db: Session, food_log: FoodLogCreate) -> FoodLog:
    try:
        # Log the input data
        logger.info(f"Creating food log with data: user_id={food_log.user_id}, food_id={food_log.food_id}, date={food_log.date}, quantity={food_log.quantity}")
        
        # Check if user exists
        user = db.query(User).filter(User.user_id == food_log.user_id).first()
        if not user:
            logger.error(f"User with ID {food_log.user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {food_log.user_id} not found"
            )
        
        # Check if food exists
        food = db.query(Food).filter(Food.food_id == food_log.food_id).first()
        if not food:
            logger.error(f"Food with ID {food_log.food_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found"
            )
        
        # Calculate nutritional values based on quantity
        calories = int(food.calories * food_log.quantity)
        protein = food.protein * food_log.quantity
        fat = food.fat * food_log.quantity
        carbs = food.carbohydrates * food_log.quantity
        
        logger.info(f"Calculated nutrition: calories={calories}, protein={protein}, fat={fat}, carbs={carbs}")
        
        # Create food log entry
        db_food_log = FoodLog(
            user_id=food_log.user_id,
            food_id=food_log.food_id,
            date=food_log.date,
            quantity=food_log.quantity,
            calories=calories,
            protein=protein,
            fat=fat,
            carbohydrates=carbs
        )
        
        # Add to database
        db.add(db_food_log)
        db.commit()
        db.refresh(db_food_log)
        
        logger.info(f"Food log created successfully with ID: {db_food_log.foodlog_id}")
        return db_food_log
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating food log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating food log: {str(e)}"
        )

def get_user_foodlogs(db: Session, user_id: int) -> List[dict]:
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