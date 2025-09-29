"""
Lightweight in-memory analytics collector for development/demo.
Stores recent events and provides simple aggregations.
"""
from collections import deque, Counter, defaultdict
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, Any, List

from models import AnalyticsEvent
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class InMemoryAnalytics:
    """Simple in-memory analytics store.

    Not suitable for production; use MongoDB/Timescale/Elastic for real analytics.
    """

    def __init__(self, max_events: int = 10000):
        self.events = deque(maxlen=max_events)
        self.lock = Lock()

    def record_event(self, event: AnalyticsEvent):
        with self.lock:
            self.events.append(event)

    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            now = datetime.utcnow()
            # Last 24 hours by default
            cutoff = now - timedelta(hours=24)
            recent = [e for e in self.events if e.timestamp >= cutoff]

            total_conversations = len({e.session_id for e in recent})
            total_messages = len([e for e in recent if e.event_type == 'message_processed'])
            intent_counter = Counter()
            sentiment_counter = Counter()
            platform_counter = Counter()
            response_times: List[float] = []

            for e in recent:
                data = e.data or {}
                intent = data.get('intent')
                if intent:
                    # intent may be a dict-like Pydantic object
                    try:
                        intent_name = intent.get('intent') if isinstance(intent, dict) else getattr(intent, 'intent', None)
                        intent_counter[intent_name] += 1
                    except Exception:
                        pass
                sentiment = data.get('sentiment')
                if sentiment:
                    try:
                        sentiment_name = sentiment.get('sentiment') if isinstance(sentiment, dict) else getattr(sentiment, 'sentiment', None)
                        sentiment_counter[sentiment_name] += 1
                    except Exception:
                        pass
                platform = getattr(e, 'platform', None)
                if platform:
                    platform_counter[getattr(platform, 'value', str(platform))] += 1

                rt = data.get('response_time_ms')
                if rt:
                    try:
                        response_times.append(float(rt))
                    except Exception:
                        pass

            average_response_time = sum(response_times) / len(response_times) if response_times else 0.0

            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'average_conversation_length': (total_messages / max(total_conversations, 1)) if total_conversations else 0.0,
                'intent_distribution': dict(intent_counter),
                'sentiment_distribution': dict(sentiment_counter),
                'platform_distribution': dict(platform_counter),
                'average_response_time_ms': average_response_time,
                'user_satisfaction_rating': 0.0
            }


# Singleton analytics instance for the application
analytics = InMemoryAnalytics(max_events=10000)
