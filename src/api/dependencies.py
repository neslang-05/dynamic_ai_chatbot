"""
Dependency injection for FastAPI endpoints.
"""
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Global instances to avoid circular imports
_chat_manager = None


def get_chat_manager():
    """Get chat manager instance."""
    global _chat_manager
    
    if _chat_manager is None:
        # Import here to avoid circular imports
        from api.chat import ChatManager
        from nlp.intent_recognition_simple import IntentRecognizer
        from nlp.sentiment_analysis_simple import SentimentAnalyzer  
        from nlp.ner_simple import NamedEntityRecognizer
        from ai.response_generator_simple import ResponseGenerator
        
        logger.info("Creating ChatManager instance with simplified modules")
        
        intent_recognizer = IntentRecognizer()
        sentiment_analyzer = SentimentAnalyzer()
        ner = NamedEntityRecognizer()
        response_generator = ResponseGenerator()
        
        _chat_manager = ChatManager(
            intent_recognizer=intent_recognizer,
            sentiment_analyzer=sentiment_analyzer,
            ner=ner,
            response_generator=response_generator
        )
    
    return _chat_manager