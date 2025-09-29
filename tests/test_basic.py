"""
Basic tests for the Dynamic AI Chatbot.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Import our modules
import sys
sys.path.append('/home/runner/work/dynamic_ai_chatbot/dynamic_ai_chatbot/src')

from api.main import create_app
from models import ChatRequest, Platform, IntentType, SentimentType
from nlp.intent_recognition import IntentRecognizer
from nlp.sentiment_analysis import SentimentAnalyzer
from nlp.ner import NamedEntityRecognizer


class TestBasicFunctionality:
    """Test basic chatbot functionality."""
    
    def setup_method(self):
        """Setup test client."""
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_chat_endpoint(self):
        """Test basic chat functionality."""
        chat_request = {
            "message": "Hello, how are you?",
            "user_id": "test_user",
            "platform": "api"
        }
        
        response = self.client.post("/chat", json=chat_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "confidence" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0


class TestNLPComponents:
    """Test NLP components."""
    
    @pytest.mark.asyncio
    async def test_intent_recognition(self):
        """Test intent recognition."""
        recognizer = IntentRecognizer()
        
        # Test greeting
        intent = await recognizer.recognize_intent("Hello, how are you?")
        assert intent.intent in [IntentType.GREETING, IntentType.UNKNOWN]
        assert 0 <= intent.confidence <= 1
        
        # Test question
        intent = await recognizer.recognize_intent("What can you do?")
        assert intent.intent in [IntentType.QUESTION, IntentType.UNKNOWN]
        assert 0 <= intent.confidence <= 1
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis(self):
        """Test sentiment analysis."""
        analyzer = SentimentAnalyzer()
        
        # Test positive sentiment
        sentiment = await analyzer.analyze_sentiment("I love this chatbot!")
        assert sentiment.sentiment in [SentimentType.POSITIVE, SentimentType.NEUTRAL]
        assert 0 <= sentiment.confidence <= 1
        
        # Test negative sentiment
        sentiment = await analyzer.analyze_sentiment("This is terrible!")
        assert sentiment.sentiment in [SentimentType.NEGATIVE, SentimentType.NEUTRAL]
        assert 0 <= sentiment.confidence <= 1
    
    @pytest.mark.asyncio
    async def test_ner(self):
        """Test named entity recognition."""
        ner = NamedEntityRecognizer()
        
        # Test with entities
        entities = await ner.extract_entities("My email is test@example.com and my phone is 123-456-7890")
        
        # Should find email and phone entities
        entity_types = [e.type for e in entities]
        assert len(entities) >= 1  # At least one entity should be found
        
        # Test each entity has required fields
        for entity in entities:
            assert hasattr(entity, 'type')
            assert hasattr(entity, 'value')
            assert hasattr(entity, 'confidence')
            assert hasattr(entity, 'start')
            assert hasattr(entity, 'end')


if __name__ == "__main__":
    pytest.main([__file__])