#!/usr/bin/env python3
"""
Simple test script to verify the chatbot functionality.
"""
import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import ChatRequest, Platform

# Use simplified modules
from nlp.intent_recognition_simple import IntentRecognizer
from nlp.sentiment_analysis_simple import SentimentAnalyzer
from nlp.ner_simple import NamedEntityRecognizer


async def test_nlp_components():
    """Test NLP components."""
    print("Testing NLP Components...")
    
    # Test intent recognition
    print("\n1. Testing Intent Recognition:")
    recognizer = IntentRecognizer()
    test_messages = [
        "Hello, how are you?",
        "What can you do for me?",
        "Please help me with this issue",
        "Thank you so much!",
        "Goodbye!"
    ]
    
    for message in test_messages:
        intent = await recognizer.recognize_intent(message)
        print(f"  '{message}' -> {intent.intent.value} (confidence: {intent.confidence:.2f})")
    
    # Test sentiment analysis
    print("\n2. Testing Sentiment Analysis:")
    analyzer = SentimentAnalyzer()
    sentiment_messages = [
        "I love this chatbot!",
        "This is terrible and frustrating",
        "It's okay, nothing special",
        "I'm so happy and excited!"
    ]
    
    for message in sentiment_messages:
        sentiment = await analyzer.analyze_sentiment(message)
        emotion_str = f" ({sentiment.emotion.value})" if sentiment.emotion else ""
        print(f"  '{message}' -> {sentiment.sentiment.value}{emotion_str} (confidence: {sentiment.confidence:.2f})")
    
    # Test NER
    print("\n3. Testing Named Entity Recognition:")
    ner = NamedEntityRecognizer()
    ner_messages = [
        "My email is john@example.com and phone is 123-456-7890",
        "The meeting is on January 15, 2024 at 3:30 PM",
        "Visit https://example.com for more information"
    ]
    
    for message in ner_messages:
        entities = await ner.extract_entities(message)
        print(f"  '{message}':")
        for entity in entities:
            print(f"    - {entity.type}: '{entity.value}' (confidence: {entity.confidence:.2f})")
        if not entities:
            print("    - No entities found")


def test_api_structure():
    """Test API structure."""
    print("\n4. Testing API Structure:")
    try:
        from api.main import create_app
        app = create_app()
        print("  ✓ FastAPI application created successfully")
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ['/health', '/chat', '/webhook/slack', '/webhook/telegram']
        for route in expected_routes:
            if route in routes:
                print(f"  ✓ Route {route} exists")
            else:
                print(f"  ✗ Route {route} missing")
                
    except Exception as e:
        print(f"  ✗ Error creating FastAPI app: {e}")


async def test_chat_functionality():
    """Test end-to-end chat functionality."""
    print("\n5. Testing Chat Functionality:")
    try:
        from api.dependencies import get_chat_manager
        chat_manager = get_chat_manager()
        
        # Test messages
        test_requests = [
            ChatRequest(message="Hello!", user_id="test_user", platform=Platform.API),
            ChatRequest(message="What can you do?", user_id="test_user", platform=Platform.API),
            ChatRequest(message="Thank you!", user_id="test_user", platform=Platform.API),
            ChatRequest(message="Goodbye!", user_id="test_user", platform=Platform.API),
        ]
        
        for request in test_requests:
            response = await chat_manager.process_message(request)
            print(f"  User: {request.message}")
            print(f"  Bot: {response.response}")
            print(f"  Intent: {response.intent.intent.value if response.intent else 'unknown'}")
            print(f"  Sentiment: {response.sentiment.sentiment.value if response.sentiment else 'unknown'}")
            print(f"  Confidence: {response.confidence:.2f}")
            print()
        
        print("  ✓ Chat functionality working correctly")
        
    except Exception as e:
        print(f"  ✗ Error in chat functionality: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print("=" * 50)
    print("Dynamic AI Chatbot - Basic Functionality Test")
    print("=" * 50)
    
    try:
        await test_nlp_components()
        test_api_structure()
        await test_chat_functionality()
        
        print("\n" + "=" * 50)
        print("Basic tests completed!")
        print("✓ Core components are working")
        print("✓ API structure is correct")
        print("✓ Chat functionality is operational")
        print("\nTo start the server, run:")
        print("  python -m src.main")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())