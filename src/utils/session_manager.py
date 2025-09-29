"""
Session management for maintaining conversation context.
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import uuid

from models import Session, ConversationTurn, Platform
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SessionManager:
    """Manages user sessions and conversation context."""
    
    def __init__(self):
        # In-memory storage for now - in production, this would use Redis
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = timedelta(seconds=settings.session_timeout)
        logger.info("SessionManager initialized")
    
    async def get_or_create_session(
        self, 
        session_id: str, 
        user_id: str, 
        platform: Platform
    ) -> Session:
        """Get existing session or create new one."""
        try:
            # Check if session exists and is not expired
            if session_id in self.sessions:
                session = self.sessions[session_id]
                if self._is_session_valid(session):
                    session.last_activity = datetime.utcnow()
                    return session
                else:
                    # Session expired, remove it
                    del self.sessions[session_id]
            
            # Create new session
            session = Session(
                id=session_id,
                user_id=user_id,
                platform=platform,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            self.sessions[session_id] = session
            logger.info(f"Created new session: {session_id}")
            
            return session
            
        except Exception as e:
            logger.error(f"Error managing session {session_id}: {e}")
            # Return a minimal session as fallback
            return Session(
                id=session_id,
                user_id=user_id,
                platform=platform
            )
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                if self._is_session_valid(session):
                    return session
                else:
                    del self.sessions[session_id]
            return None
            
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def add_conversation_turn(self, session_id: str, turn: ConversationTurn):
        """Add a conversation turn to the session."""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                # Append turn to the conversation_turns list (Session model uses conversation_turns)
                session.conversation_turns.append(turn)
                session.last_activity = datetime.utcnow()
                
                # Limit context length to prevent memory issues
                max_length = settings.max_context_length
                if len(session.conversation_turns) > max_length:
                    session.conversation_turns = session.conversation_turns[-max_length:]
                
                logger.debug(f"Added conversation turn to session {session_id}")
            
        except Exception as e:
            logger.error(f"Error adding conversation turn to session {session_id}: {e}")
    
    async def delete_session(self, session_id: str):
        """Delete a session."""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Deleted session: {session_id}")
                
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            expired_sessions = []
            current_time = datetime.utcnow()
            
            for session_id, session in self.sessions.items():
                if current_time - session.last_activity > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
                logger.info(f"Cleaned up expired session: {session_id}")
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
    
    def _is_session_valid(self, session: Session) -> bool:
        """Check if session is still valid (not expired)."""
        return datetime.utcnow() - session.last_activity < self.session_timeout
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        try:
            active_sessions = len(self.sessions)
            platforms = {}
            
            for session in self.sessions.values():
                platform = session.platform.value
                platforms[platform] = platforms.get(platform, 0) + 1
            
            return {
                "active_sessions": active_sessions,
                "platforms": platforms,
                "session_timeout": self.session_timeout.total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {"active_sessions": 0, "platforms": {}, "session_timeout": 0}


# Redis-based session manager for production use
class RedisSessionManager(SessionManager):
    """Redis-based session manager for production deployment."""
    
    def __init__(self):
        super().__init__()
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis session manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            logger.info("Falling back to in-memory session storage")
            self.redis_client = None
    
    async def get_or_create_session(
        self, 
        session_id: str, 
        user_id: str, 
        platform: Platform
    ) -> Session:
        """Get or create session using Redis."""
        if not self.redis_client:
            return await super().get_or_create_session(session_id, user_id, platform)
        
        try:
            # Try to get session from Redis
            session_data = self.redis_client.get(f"session:{session_id}")
            
            if session_data:
                session_dict = json.loads(session_data)
                session = Session(**session_dict)
                
                # Check if session is valid
                if self._is_session_valid(session):
                    session.last_activity = datetime.utcnow()
                    await self._save_session_to_redis(session)
                    return session
                else:
                    # Session expired, delete it
                    self.redis_client.delete(f"session:{session_id}")
            
            # Create new session
            session = Session(
                id=session_id,
                user_id=user_id,
                platform=platform
            )
            
            await self._save_session_to_redis(session)
            return session
            
        except Exception as e:
            logger.error(f"Error with Redis session management: {e}")
            return await super().get_or_create_session(session_id, user_id, platform)
    
    async def _save_session_to_redis(self, session: Session):
        """Save session to Redis."""
        try:
            session_data = session.json()
            self.redis_client.setex(
                f"session:{session.id}",
                int(self.session_timeout.total_seconds()),
                session_data
            )
        except Exception as e:
            logger.error(f"Error saving session to Redis: {e}")
    
    async def delete_session(self, session_id: str):
        """Delete session from Redis."""
        if not self.redis_client:
            return await super().delete_session(session_id)
        
        try:
            self.redis_client.delete(f"session:{session_id}")
            logger.info(f"Deleted session from Redis: {session_id}")
            
        except Exception as e:
            logger.error(f"Error deleting session from Redis: {e}")
            await super().delete_session(session_id)