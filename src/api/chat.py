"""
Main chat manager that orchestrates all chatbot components.
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from models import (
    ChatRequest, ChatResponse, Message, Response, Session, 
    ConversationTurn, Platform, AnalyticsEvent
)
# Import simplified modules 
from nlp.intent_recognition_simple import IntentRecognizer
from nlp.sentiment_analysis_simple import SentimentAnalyzer
from nlp.ner_simple import NamedEntityRecognizer
from ai.response_generator_simple import ResponseGenerator
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ChatManager:
    """Main chat manager that orchestrates all chatbot components."""
    
    def __init__(
        self,
        intent_recognizer: IntentRecognizer,
        sentiment_analyzer: SentimentAnalyzer,
        ner: NamedEntityRecognizer,
        response_generator: ResponseGenerator,
        session_manager: Optional[SessionManager] = None
    ):
        self.intent_recognizer = intent_recognizer
        self.sentiment_analyzer = sentiment_analyzer
        self.ner = ner
        self.response_generator = response_generator
        self.session_manager = session_manager or SessionManager()
        
        logger.info("ChatManager initialized successfully")
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a user message and generate a bot response."""
        try:
            # Get or create session
            session_id = request.session_id or str(uuid.uuid4())
            session = await self.session_manager.get_or_create_session(
                session_id=session_id,
                user_id=request.user_id,
                platform=request.platform
            )
            
            # Create message object
            message = Message(
                id=str(uuid.uuid4()),
                text=request.message,
                user_id=request.user_id,
                session_id=session_id,
                platform=request.platform
            )
            
            # Perform NLP analysis
            await self._analyze_message(message)
            
            # Generate response
            response = await self._generate_response(message, session)
            
            # Create conversation turn
            turn = ConversationTurn(message=message, response=response)
            
            # Update session with new turn
            await self.session_manager.add_conversation_turn(session_id, turn)
            
            # Log analytics event
            await self._log_analytics_event("message_processed", session, message)
            
            # Create API response
            chat_response = ChatResponse(
                response=response.text,
                session_id=session_id,
                intent=message.intent,
                sentiment=message.sentiment,
                entities=message.entities,
                confidence=response.confidence,
                timestamp=response.timestamp
            )
            
            logger.info(f"Processed message successfully for session {session_id}")
            return chat_response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Return fallback response
            return ChatResponse(
                response="I apologize, but I'm having trouble processing your message right now. Please try again.",
                session_id=session_id or str(uuid.uuid4()),
                confidence=0.1
            )
    
    async def _analyze_message(self, message: Message):
        """Perform NLP analysis on the message."""
        try:
            # Intent recognition
            message.intent = await self.intent_recognizer.recognize_intent(message.text)
            
            # Named entity recognition
            message.entities = await self.ner.extract_entities(message.text)
            
            # Sentiment analysis
            message.sentiment = await self.sentiment_analyzer.analyze_sentiment(message.text)
            
            logger.debug(f"NLP analysis completed for message: {message.id}")
            
        except Exception as e:
            logger.error(f"Error in NLP analysis: {e}")
            # Continue with default values
    
    async def _generate_response(self, message: Message, session: Session) -> Response:
        """Generate bot response using the hybrid approach."""
        try:
            response_text = await self.response_generator.generate_response(
                message=message,
                context=session.context
            )
            
            response = Response(
                id=str(uuid.uuid4()),
                text=response_text,
                session_id=session.id,
                confidence=0.8  # This would be calculated based on the generation method
            )
            
            logger.debug(f"Generated response: {response.id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            return Response(
                id=str(uuid.uuid4()),
                text="I'm sorry, I didn't understand that. Could you please rephrase your question?",
                session_id=session.id,
                confidence=0.1
            )
    
    async def _log_analytics_event(self, event_type: str, session: Session, message: Message):
        """Log analytics event."""
        try:
            event = AnalyticsEvent(
                event_type=event_type,
                session_id=session.id,
                user_id=session.user_id,
                platform=session.platform,
                data={
                    "message_length": len(message.text),
                    "intent": message.intent.dict() if message.intent else None,
                    "sentiment": message.sentiment.dict() if message.sentiment else None,
                    "entities_count": len(message.entities)
                }
            )
            
            # In a real implementation, this would be sent to the analytics service
            logger.debug(f"Analytics event logged: {event.event_type}")
            
        except Exception as e:
            logger.error(f"Error logging analytics event: {e}")
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        return await self.session_manager.get_session(session_id)
    
    async def delete_session(self, session_id: str):
        """Delete session by ID."""
        await self.session_manager.delete_session(session_id)
    
    async def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics statistics."""
        # In a real implementation, this would query the analytics database
        return {
            "total_sessions": 0,
            "total_messages": 0,
            "average_session_length": 0,
            "top_intents": [],
            "sentiment_distribution": {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }
        }