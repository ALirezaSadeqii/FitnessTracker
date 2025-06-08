from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from jose import JWTError, jwt
import logging

from models import Base, engine, get_db, User
from schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    FoodResponse, FoodLogCreate, FoodLogResponse,
    ProgressCreate, ProgressResponse, UserUpdate
)
import database as db
from db_operations import seed_foods

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fitness Tracker API")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    database: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Use the global constants from database module, not the db session
        payload = jwt.decode(token, db.SECRET_KEY, algorithms=[db.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise credentials_exception
    
    # Convert user_id to int
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise credentials_exception
    
    user = db.get_user(database, user_id_int)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, database: Session = Depends(get_db)):
    logger.info(f"Registering new user: {user.email}")
    return db.create_user(database, user)

@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    database: Session = Depends(get_db)
):
    logger.info(f"Login attempt: {form_data.username}")
    user = db.authenticate_user(database, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = db.create_access_token(data={"sub": str(user.user_id)})
    logger.info(f"Login successful for user: {form_data.username}, user_id: {user.user_id}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db)
):
    logger.info(f"Fetching user by ID: {user_id}")
    user = db.get_user(database, user_id)
    if user is None:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user"""
    logger.info(f"Fetching current user: {current_user.user_id}")
    return current_user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db)
):
    logger.info(f"Updating user: {user_id}")
    # Check if the current user is trying to update their own profile
    if current_user.user_id != user_id:
        logger.warning(f"Unauthorized update attempt: {current_user.user_id} tried to update {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update another user's profile"
        )
    
    # Update the user profile
    updated_user = db.update_user(database, user_id, user_update)
    if updated_user is None:
        logger.warning(f"User not found for update: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@app.get("/users", response_model=UserResponse)
def read_user_by_email(
    email: str,
    database: Session = Depends(get_db)
):
    logger.info(f"Fetching user by email: {email}")
    user = db.get_user_by_email(database, email)
    if user is None:
        logger.warning(f"User not found with email: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/foods", response_model=List[FoodResponse])
def read_foods(
    skip: int = 0,
    limit: int = 100,
    database: Session = Depends(get_db)
):
    logger.info(f"Fetching foods, skip: {skip}, limit: {limit}")
    foods = db.get_foods(database, skip=skip, limit=limit)
    return foods

@app.post("/foodlogs", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
def create_food_log(
    food_log: FoodLogCreate,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db)
):
    logger.info(f"Creating food log for user: {current_user.user_id}, food: {food_log.food_id}")
    
    # Debug info
    logger.info(f"Current user ID: {current_user.user_id}, Food log user ID: {food_log.user_id}")
    
    if int(food_log.user_id) != current_user.user_id:
        logger.warning(f"Unauthorized food log creation: {current_user.user_id} tried for {food_log.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create food log for another user"
        )
    
    try:
        result = db.create_food_log(database, food_log)
        logger.info(f"Food log created successfully: {result.foodlog_id}")
        return result
    except Exception as e:
        logger.error(f"Error creating food log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating food log: {str(e)}"
        )

@app.get("/users/{user_id}/foodlogs", response_model=List[FoodLogResponse])
def read_user_foodlogs(
    user_id: int,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db)
):
    logger.info(f"Fetching food logs for user: {user_id}")
    
    if user_id != current_user.user_id:
        logger.warning(f"Unauthorized food log access: {current_user.user_id} tried to access {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view another user's food logs"
        )
    
    foodlogs = db.get_user_foodlogs(database, user_id)
    return foodlogs

@app.get("/progress/{user_id}", response_model=List[ProgressResponse])
def read_user_progress(
    user_id: int,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db)
):
    logger.info(f"Fetching progress for user: {user_id}")
    
    if user_id != current_user.user_id:
        logger.warning(f"Unauthorized progress access: {current_user.user_id} tried to access {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view another user's progress"
        )
    
    progress = db.get_user_progress(database, user_id)
    return progress

@app.post("/progress", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
def create_progress(
    progress: ProgressCreate,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db)
):
    logger.info(f"Creating progress record for user: {current_user.user_id}")
    
    if progress.user_id != current_user.user_id:
        logger.warning(f"Unauthorized progress creation: {current_user.user_id} tried for {progress.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create progress for another user"
        )
    
    return db.create_progress(database, progress)

@app.post("/seed-foods")
def seed_foods_endpoint(database: Session = Depends(get_db)):
    logger.info("Seeding foods database")
    seed_foods(database)
    return {"message": "Foods seeded successfully"}

if __name__ == "__main__":
    from models import SessionLocal
    from db_operations import seed_foods
    db = SessionLocal()
    seed_foods(db)
    print("Food table seeded with default foods.")
    db.close() 