"""
Authentication dependencies for FastAPI.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from auth.utils import jwt_manager
from auth.repository import user_repository
from auth.models import UserProfile, TokenData


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserProfile:
    """Get the current authenticated user."""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        payload = jwt_manager.verify_token(credentials.credentials)
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if username is None or user_id is None:
            raise credentials_exception
            
        token_data = TokenData(username=username, user_id=user_id)
    except Exception:
        raise credentials_exception
    
    # Get user from database
    user_doc = await user_repository.get_user_by_id(token_data.user_id)
    if user_doc is None:
        raise credentials_exception
    
    return UserProfile(
        id=user_doc["_id"],
        username=user_doc["username"],
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        created_at=user_doc["created_at"],
        is_active=user_doc["is_active"]
    )


async def get_current_active_user(
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserProfile]:
    """Get current user if token is provided, otherwise return None."""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None