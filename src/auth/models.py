"""
Authentication models for the Dynamic AI Chatbot.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserSignup(BaseModel):
    """User signup request model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    """User login request model."""
    username: str
    password: str


class UserProfile(BaseModel):
    """User profile model."""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool = True


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile


class TokenData(BaseModel):
    """Token data for validation."""
    username: Optional[str] = None
    user_id: Optional[str] = None