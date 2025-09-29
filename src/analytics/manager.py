"""
Analytics and monitoring for the Dynamic AI Chatbot.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter

from models import AnalyticsEvent, Session, ConversationTurn, IntentType, SentimentType
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AnalyticsManager:
    """Analytics manager for collecting and analyzing chatbot data."""
    
    def __init__(self):
        # In-memory storage for demo - in production, use MongoDB
        self.events: List[AnalyticsEvent] = []
        self.sessions_data: Dict[str, Session] = {}
        logger.info("AnalyticsManager initialized")
    
    async def log_event(self, event: AnalyticsEvent):
        """Log an analytics event."""
        try:
            self.events.append(event)
            logger.debug(f"Logged analytics event: {event.event_type}")
        except Exception as e:
            logger.error(f"Error logging analytics event: {e}")
    
    async def log_session_data(self, session: Session):
        """Log session data for analytics."""
        try:
            self.sessions_data[session.id] = session
        except Exception as e:
            logger.error(f"Error logging session data: {e}")
    
    async def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        try:
            stats = {
                "total_sessions": len(self.sessions_data),
                "total_messages": 0,
                "total_events": len(self.events),
                "average_session_length": 0,
                "intent_distribution": Counter(),
                "sentiment_distribution": Counter(),
                "platform_distribution": Counter(),
                "hourly_activity": defaultdict(int),
                "daily_activity": defaultdict(int)
            }
            
            # Analyze sessions
            session_lengths = []
            for session in self.sessions_data.values():
                session_length = len(session.context)
                session_lengths.append(session_length)
                stats["total_messages"] += session_length
                
                stats["platform_distribution"][session.platform.value] += 1
                
                # Analyze conversation turns
                for turn in session.context:
                    if turn.message.intent:
                        stats["intent_distribution"][turn.message.intent.intent.value] += 1
                    
                    if turn.message.sentiment:
                        stats["sentiment_distribution"][turn.message.sentiment.sentiment.value] += 1
                    
                    # Time-based analysis
                    hour = turn.message.timestamp.hour
                    day = turn.message.timestamp.strftime("%Y-%m-%d")
                    stats["hourly_activity"][hour] += 1
                    stats["daily_activity"][day] += 1
            
            # Calculate averages
            if session_lengths:
                stats["average_session_length"] = sum(session_lengths) / len(session_lengths)
            
            # Convert Counters to regular dicts for JSON serialization
            stats["intent_distribution"] = dict(stats["intent_distribution"])
            stats["sentiment_distribution"] = dict(stats["sentiment_distribution"])
            stats["platform_distribution"] = dict(stats["platform_distribution"])
            stats["hourly_activity"] = dict(stats["hourly_activity"])
            stats["daily_activity"] = dict(stats["daily_activity"])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "total_events": 0,
                "average_session_length": 0,
                "intent_distribution": {},
                "sentiment_distribution": {},
                "platform_distribution": {},
                "hourly_activity": {},
                "daily_activity": {}
            }
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for a specific user."""
        try:
            user_sessions = [s for s in self.sessions_data.values() if s.user_id == user_id]
            user_events = [e for e in self.events if e.user_id == user_id]
            
            if not user_sessions:
                return {"error": "No data found for user"}
            
            stats = {
                "user_id": user_id,
                "total_sessions": len(user_sessions),
                "total_messages": sum(len(s.context) for s in user_sessions),
                "platforms_used": list(set(s.platform.value for s in user_sessions)),
                "first_interaction": min(s.created_at for s in user_sessions).isoformat(),
                "last_interaction": max(s.last_activity for s in user_sessions).isoformat(),
                "average_session_length": 0,
                "intent_preferences": Counter(),
                "sentiment_trend": []
            }
            
            # Calculate average session length
            session_lengths = [len(s.context) for s in user_sessions]
            if session_lengths:
                stats["average_session_length"] = sum(session_lengths) / len(session_lengths)
            
            # Analyze user's intent patterns
            for session in user_sessions:
                for turn in session.context:
                    if turn.message.intent:
                        stats["intent_preferences"][turn.message.intent.intent.value] += 1
            
            stats["intent_preferences"] = dict(stats["intent_preferences"])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user analytics for {user_id}: {e}")
            return {"error": "Failed to get user analytics"}
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for monitoring."""
        try:
            now = datetime.utcnow()
            last_hour = now - timedelta(hours=1)
            last_24h = now - timedelta(hours=24)
            
            # Active sessions (activity in last hour)
            active_sessions = sum(
                1 for s in self.sessions_data.values() 
                if s.last_activity >= last_hour
            )
            
            # Messages in last 24 hours
            messages_24h = 0
            for session in self.sessions_data.values():
                for turn in session.context:
                    if turn.message.timestamp >= last_24h:
                        messages_24h += 1
            
            # Events in last hour
            events_1h = sum(
                1 for e in self.events 
                if e.timestamp >= last_hour
            )
            
            return {
                "timestamp": now.isoformat(),
                "active_sessions": active_sessions,
                "messages_last_24h": messages_24h,
                "events_last_hour": events_1h,
                "total_sessions_ever": len(self.sessions_data),
                "system_health": "healthy"  # This would check various health metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting realtime metrics: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "active_sessions": 0,
                "messages_last_24h": 0,
                "events_last_hour": 0,
                "total_sessions_ever": 0,
                "system_health": "error"
            }


# Global analytics manager instance
analytics_manager = AnalyticsManager()