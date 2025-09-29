"""
User repository for database operations.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from auth.models import UserSignup, UserProfile
from auth.utils import password_manager
from config import settings


class UserRepository:
    """Handle user database operations."""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_db]
        self.users_collection = self.db.users
        
    async def create_indexes(self):
        """Create database indexes for users collection."""
        await self.users_collection.create_index("username", unique=True)
        await self.users_collection.create_index("email", unique=True)
    
    async def create_user(self, user_data: UserSignup) -> UserProfile:
        """Create a new user."""
        # Hash the password
        hashed_password = password_manager.hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "_id": str(uuid.uuid4()),
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": hashed_password,
            "full_name": user_data.full_name,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        try:
            await self.users_collection.insert_one(user_doc)
            return UserProfile(
                id=user_doc["_id"],
                username=user_doc["username"],
                email=user_doc["email"],
                full_name=user_doc["full_name"],
                created_at=user_doc["created_at"],
                is_active=user_doc["is_active"]
            )
        except DuplicateKeyError as e:
            if "username" in str(e):
                raise ValueError("Username already exists")
            elif "email" in str(e):
                raise ValueError("Email already exists")
            else:
                raise ValueError("User already exists")
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        return await self.users_collection.find_one({"username": username})
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        return await self.users_collection.find_one({"email": email})
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return await self.users_collection.find_one({"_id": user_id})
    
    async def verify_user_credentials(self, username: str, password: str) -> Optional[UserProfile]:
        """Verify user credentials and return user profile if valid."""
        user_doc = await self.get_user_by_username(username)
        if not user_doc:
            return None
        
        if not password_manager.verify_password(password, user_doc["password_hash"]):
            return None
        
        return UserProfile(
            id=user_doc["_id"],
            username=user_doc["username"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            created_at=user_doc["created_at"],
            is_active=user_doc["is_active"]
        )
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information."""
        result = await self.users_collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        result = await self.users_collection.delete_one({"_id": user_id})
        return result.deleted_count > 0


# Global instance
user_repository = UserRepository()