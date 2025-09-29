"""
In-memory analytics service for collecting and aggregating chatbot events.
"""
from typing import Dict, List, Any
from collections import defaultdict

from models import AnalyticsEvent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class InMemoryAnalytics:
    """In-memory analytics collector for demo purposes."""
    
    def __init__(self):
        self.events: List[AnalyticsEvent] = []
        logger.info("InMemoryAnalytics initialized")
    
    def log_event(self, event: AnalyticsEvent):
        """Log an analytics event."""
        self.events.append(event)
        logger.debug(f"Logged analytics event: {event.event_type}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated analytics statistics."""
        try:
            if not self.events:
                return self._get_empty_stats()
            
            # Aggregate data
            total_conversations = len(set(e.session_id for e in self.events if e.event_type == "message_processed"))
            total_messages = len([e for e in self.events if e.event_type == "message_processed"])
            
            # Average conversation length (rough estimate)
            conversation_lengths = defaultdict(int)
            for e in self.events:
                if e.event_type == "message_processed":
                    conversation_lengths[e.session_id] += 1
            avg_conversation_length = sum(conversation_lengths.values()) / len(conversation_lengths) if conversation_lengths else 0
            
            # Intent distribution
            intent_dist = defaultdict(int)
            for e in self.events:
                if e.event_type == "message_processed" and e.data:
                    intent_data = e.data.get("intent")
                    if intent_data and isinstance(intent_data, dict):
                        intent = intent_data.get("intent")
                        if intent:
                            intent_dist[intent] += 1
            
            # Sentiment distribution
            sentiment_dist = defaultdict(int)
            for e in self.events:
                if e.event_type == "message_processed" and e.data:
                    sentiment_data = e.data.get("sentiment")
                    if sentiment_data and isinstance(sentiment_data, dict):
                        sentiment = sentiment_data.get("sentiment")
                        if sentiment:
                            sentiment_dist[sentiment] += 1
            
            # Platform distribution
            platform_dist = defaultdict(int)
            for e in self.events:
                platform_dist[e.platform.value] += 1
            
            # Average response time (placeholder, since not stored)
            avg_response_time = 350.0  # ms
            
            # User satisfaction (placeholder)
            user_satisfaction = 4.1
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "average_conversation_length": round(avg_conversation_length, 1),
                "intent_distribution": dict(intent_dist),
                "sentiment_distribution": dict(sentiment_dist),
                "platform_distribution": dict(platform_dist),
                "average_response_time_ms": avg_response_time,
                "user_satisfaction_rating": user_satisfaction
            }
            
        except Exception as e:
            logger.error(f"Error aggregating analytics: {e}")
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> Dict[str, Any]:
        """Return empty stats structure."""
        return {
            "total_conversations": 0,
            "total_messages": 0,
            "average_conversation_length": 0.0,
            "intent_distribution": {},
            "sentiment_distribution": {},
            "platform_distribution": {},
            "average_response_time_ms": 0.0,
            "user_satisfaction_rating": 0.0
        }
    
    def clear_events(self):
        """Clear all events (for testing)."""
        self.events.clear()
        logger.info("Cleared all analytics events")


# Global instance
analytics = InMemoryAnalytics()