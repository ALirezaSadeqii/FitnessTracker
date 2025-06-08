from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    height: float
    weight: float
    goal: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class FoodBase(BaseModel):
    name: str
    calories: int
    protein: float
    fat: float
    carbohydrates: float

class FoodResponse(FoodBase):
    food_id: int

    class Config:
        from_attributes = True

class FoodLogCreate(BaseModel):
    user_id: int
    food_id: int
    quantity: float
    date: date

class FoodLogResponse(BaseModel):
    foodlog_id: int
    user_id: int
    food_id: int
    date: date
    quantity: float
    calories: int
    protein: float
    fat: float
    carbohydrates: float

    class Config:
        from_attributes = True

class ProgressCreate(BaseModel):
    user_id: int
    weight: float
    bmi: float
    calorie_intake: int
    date: date

class ProgressResponse(ProgressCreate):
    progress_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str 