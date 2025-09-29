"""
Authentication API endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from auth.models import UserSignup, UserLogin, Token, UserProfile
from auth.repository import user_repository
from auth.utils import jwt_manager, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.dependencies import get_current_active_user
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=Token)
async def signup(user_data: UserSignup):
    """Register a new user."""
    try:
        # Create user
        user_profile = await user_repository.create_user(user_data)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt_manager.create_access_token(
            data={"sub": user_profile.username, "user_id": user_profile.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"New user registered: {user_profile.username}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_profile
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return access token."""
    try:
        # Verify credentials
        user_profile = await user_repository.verify_user_credentials(
            user_credentials.username, 
            user_credentials.password
        )
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt_manager.create_access_token(
            data={"sub": user_profile.username, "user_id": user_profile.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user_profile.username}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: UserProfile = Depends(get_current_active_user)
):
    """Get current user profile."""
    return current_user


@router.post("/logout")
async def logout():
    """Logout user (client should delete the token)."""
    return {"message": "Successfully logged out"}


@router.get("/verify-token")
async def verify_token(
    current_user: UserProfile = Depends(get_current_active_user)
):
    """Verify if the current token is valid."""
    return {
        "valid": True, 
        "user": current_user.username,
        "user_id": current_user.id
    }
    