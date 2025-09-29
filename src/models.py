"""
Data models for the Dynamic AI Chatbot using Pydantic.
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class Platform(str, Enum):
    """Supported platforms for the chatbot."""
    WEB = "web"
    SLACK = "slack"
    TELEGRAM = "telegram"
    API = "api"


class Intent(str, Enum):
    """Recognized intents."""
    GREETING = "greeting"
    QUESTION = "question"
    REQUEST = "request"
    COMPLAINT = "complaint"
    GOODBYE = "goodbye"
    HELP = "help"
    COMPLIMENT = "compliment"
    UNKNOWN = "unknown"


# Alias for backward compatibility
IntentType = Intent


class Sentiment(str, Enum):
    """Sentiment classifications."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# Alias for backward compatibility
SentimentType = Sentiment


class EmotionType(str, Enum):
    """Emotion classifications."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"


class EntityType(str, Enum):
    """Named entity types."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    TIME = "time"
    MONEY = "money"
    PRODUCT = "product"


class Entity(BaseModel):
    """Named entity extracted from text."""
    text: str = Field(..., description="The entity text")
    label: EntityType = Field(..., description="The entity type")
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")
    confidence: float = Field(0.0, description="Confidence score")


class Message(BaseModel):
    """User message model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    text: str = Field(..., description="Message text")
    platform: Platform = Field(Platform.API, description="Source platform")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # NLP analysis fields
    intent: Intent = Field(Intent.UNKNOWN, description="Detected intent")
    sentiment: Sentiment = Field(Sentiment.NEUTRAL, description="Detected sentiment")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Response(BaseModel):
    """Bot response model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str = Field(..., description="Response text")
    intent: Intent = Field(Intent.UNKNOWN, description="Detected intent")
    sentiment: Sentiment = Field(Sentiment.NEUTRAL, description="Detected sentiment")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    confidence: float = Field(0.0, description="Response confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationTurn(BaseModel):
    """A single conversation turn with user message and bot response."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_message: Message
    bot_response: Response
    processing_time_ms: float = Field(0.0, description="Processing time in milliseconds")


class Session(BaseModel):
    """User session model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User identifier")
    platform: Platform = Field(Platform.API, description="Source platform")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    conversation_turns: List[ConversationTurn] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict, description="Session context")
    is_active: bool = Field(True, description="Whether session is active")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    platform: Platform = Field(Platform.API, description="Source platform")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str = Field(..., description="Bot response message")
    session_id: str = Field(..., description="Session identifier")
    intent: Intent = Field(Intent.UNKNOWN, description="Detected intent")
    sentiment: Sentiment = Field(Sentiment.NEUTRAL, description="Detected sentiment")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    confidence: float = Field(0.0, description="Response confidence")
    suggestions: List[str] = Field(default_factory=list, description="Suggested responses")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsEvent(BaseModel):
    """Analytics event model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = Field(..., description="Type of event")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    platform: Platform = Field(Platform.API, description="Source platform")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")


class UserFeedback(BaseModel):
    """User feedback model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    turn_id: str = Field(..., description="Conversation turn identifier")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_text: Optional[str] = Field(None, description="Optional feedback text")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IntentPrediction(BaseModel):
    """Intent prediction result."""
    intent: Intent = Field(..., description="Predicted intent")
    confidence: float = Field(..., description="Prediction confidence")
    alternatives: List[Dict[str, Union[Intent, float]]] = Field(
        default_factory=list, 
        description="Alternative predictions"
    )


class SentimentPrediction(BaseModel):
    """Sentiment prediction result."""
    sentiment: Sentiment = Field(..., description="Predicted sentiment")
    confidence: float = Field(..., description="Prediction confidence")
    scores: Dict[str, float] = Field(
        default_factory=dict, 
        description="Scores for all sentiment classes"
    )


class AnalyticsStats(BaseModel):
    """Analytics statistics model."""
    total_conversations: int = Field(0, description="Total number of conversations")
    total_messages: int = Field(0, description="Total number of messages")
    average_conversation_length: float = Field(0.0, description="Average messages per conversation")
    intent_distribution: Dict[str, int] = Field(default_factory=dict)
    sentiment_distribution: Dict[str, int] = Field(default_factory=dict)
    platform_distribution: Dict[str, int] = Field(default_factory=dict)
    average_response_time_ms: float = Field(0.0, description="Average response time")
    user_satisfaction_rating: float = Field(0.0, description="Average user rating")


# Import uuid for default factories
import uuid