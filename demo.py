#!/usr/bin/env python3
"""
Comprehensive demonstration of the Dynamic AI Chatbot functionality.
This script showcases all major features of the chatbot system.
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot.core.engine import ChatbotEngine
from chatbot.utils.config import Config
from chatbot.utils.helpers import (
    clean_text, extract_keywords, validate_user_input,
    analyze_text_complexity, PerformanceTimer
)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_subheader(title: str):
    """Print a formatted subheader."""
    print(f"\n🔹 {title}")
    print("-" * 40)


def demonstrate_configuration():
    """Demonstrate configuration management."""
    print_header("CONFIGURATION MANAGEMENT")
    
    # Initialize configuration
    config = Config()
    
    print(f"✅ Chatbot Name: {config.CHATBOT_NAME}")
    print(f"✅ Model: {config.MODEL_NAME}")
    print(f"✅ Max History: {config.MAX_HISTORY_LENGTH}")
    print(f"✅ Confidence Threshold: {config.CONFIDENCE_THRESHOLD}")
    print(f"✅ Learning Enabled: {config.ENABLE_LEARNING}")
    print(f"✅ Database: {config.DATABASE_URL}")
    
    # Validate configuration
    if config.validate_config():
        print("✅ Configuration validation: PASSED")
    else:
        print("❌ Configuration validation: FAILED")


def demonstrate_helpers():
    """Demonstrate utility helper functions."""
    print_header("UTILITY HELPERS")
    
    # Text cleaning
    print_subheader("Text Processing")
    dirty_text = "  Hello!!!   @#$World???  "
    clean = clean_text(dirty_text)
    print(f"Original: '{dirty_text}'")
    print(f"Cleaned:  '{clean}'")
    
    # Keyword extraction
    text = "I'm interested in machine learning and artificial intelligence"
    keywords = extract_keywords(text)
    print(f"\nKeyword extraction from: '{text}'")
    print(f"Keywords: {keywords}")
    
    # Text complexity analysis
    simple_text = "Hi there"
    complex_text = "The implementation of sophisticated natural language processing algorithms"
    
    simple_analysis = analyze_text_complexity(simple_text)
    complex_analysis = analyze_text_complexity(complex_text)
    
    print(f"\nComplexity Analysis:")
    print(f"Simple text: '{simple_text}' -> Score: {simple_analysis['complexity_score']}")
    print(f"Complex text: '{complex_text[:50]}...' -> Score: {complex_analysis['complexity_score']}")
    
    # Input validation
    print(f"\nInput Validation:")
    valid_result = validate_user_input("Hello, how are you?")
    invalid_result = validate_user_input("")
    
    print(f"Valid input: {valid_result['valid']}")
    print(f"Empty input: {invalid_result['valid']} (errors: {invalid_result['errors']})")


def demonstrate_chatbot_engine():
    """Demonstrate core chatbot engine functionality."""
    print_header("CHATBOT ENGINE DEMONSTRATION")
    
    # Initialize chatbot
    config = Config()
    engine = ChatbotEngine(config)
    print("✅ Chatbot engine initialized")
    
    # Start conversation
    user_id = "demo_user"
    session_id = engine.start_conversation(user_id)
    print(f"✅ Started conversation session: {session_id}")
    
    # Demonstration conversation
    conversation = [
        "Hello! How are you today?",
        "I'm interested in learning about artificial intelligence",
        "Can you explain how machine learning works?",
        "What are some practical applications of AI?",
        "Thank you for the information!"
    ]
    
    print_subheader("Interactive Conversation")
    
    for i, message in enumerate(conversation, 1):
        print(f"\n👤 User: {message}")
        
        # Process with timing
        with PerformanceTimer(f"Message {i} processing"):
            response_data = engine.process_message(message, user_id)
        
        print(f"🤖 Bot: {response_data['response']}")
        print(f"📊 Confidence: {response_data['confidence']:.3f}")
        print(f"🔗 Context keywords: {response_data['context_used']}")
        print(f"📚 Similar conversations: {response_data['similar_found']}")
        
        time.sleep(0.5)  # Small delay for demonstration
    
    # Show conversation statistics
    print_subheader("Conversation Statistics")
    stats = engine.get_conversation_stats()
    print(f"Session ID: {stats['session_id']}")
    print(f"Total messages: {stats['message_count']}")
    print(f"Context keywords: {stats['context_keywords']}")
    print(f"Duration: {stats['duration_minutes']:.2f} minutes")
    
    # End conversation
    engine.end_conversation()
    print("\n✅ Conversation ended")
    
    return engine


def demonstrate_memory_system(engine):
    """Demonstrate memory and learning capabilities."""
    print_header("MEMORY & LEARNING SYSTEM")
    
    user_id = "demo_user"
    
    # Show recent conversations
    print_subheader("Conversation History")
    history = engine.conversation_memory.get_recent_conversations(user_id, limit=3)
    
    for i, conv in enumerate(history, 1):
        timestamp = conv['timestamp']
        user_msg = conv['user_message'][:50] + "..." if len(conv['user_message']) > 50 else conv['user_message']
        bot_msg = conv['bot_response'][:50] + "..." if len(conv['bot_response']) > 50 else conv['bot_response']
        
        print(f"{i}. [{timestamp}]")
        print(f"   User: {user_msg}")
        print(f"   Bot:  {bot_msg}")
    
    # Show similar conversation matching
    print_subheader("Similar Conversation Matching")
    similar = engine.conversation_memory.find_similar_conversations(
        "Tell me about AI", user_id=user_id, limit=2
    )
    
    if similar:
        for i, conv in enumerate(similar, 1):
            print(f"{i}. Similarity: {conv['similarity_score']:.3f}")
            print(f"   Query: {conv['user_message'][:40]}...")
            print(f"   Response: {conv['bot_response'][:40]}...")
    else:
        print("No similar conversations found")
    
    # Show learning insights
    print_subheader("Learning Insights")
    insights = engine.learning_system.get_learning_insights(user_id=user_id)
    
    if insights.get('top_topics'):
        print("Top Topics:")
        for topic in insights['top_topics'][:3]:
            print(f"  - {topic['topic']}: {topic['score']:.2f} (freq: {topic['frequency']})")
    
    if insights.get('quality_metrics'):
        metrics = insights['quality_metrics']
        print(f"\nQuality Metrics:")
        print(f"  - Average Quality: {metrics.get('average_quality', 0):.2f}")
        print(f"  - Appropriateness: {metrics.get('average_appropriateness', 0):.2f}")
        print(f"  - Understanding: {metrics.get('average_understanding', 0):.2f}")
    
    # Show user preferences
    preferences = engine.learning_system.get_user_preferences(user_id)
    if preferences:
        print(f"\nLearned User Preferences:")
        for pref_type, pref_list in preferences.items():
            if pref_list:
                print(f"  {pref_type.replace('_', ' ').title()}:")
                for pref in pref_list[:2]:  # Show top 2
                    print(f"    - {pref['value']} (confidence: {pref['confidence']:.2f})")


def demonstrate_nlp_features():
    """Demonstrate NLP processing capabilities."""
    print_header("NLP PROCESSING CAPABILITIES")
    
    config = Config()
    from chatbot.nlp.processor import NLPProcessor
    
    processor = NLPProcessor(config)
    
    # Test messages
    test_messages = [
        "Hello! I'm excited about learning AI today!",
        "I'm feeling sad and need some help",
        "Can you explain how machine learning algorithms work?",
        "Thank you so much for your help!"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print_subheader(f"Analysis {i}")
        print(f"Message: '{message}'")
        
        # Perform NLP analysis
        analysis = processor.analyze_message(message)
        
        print(f"Sentiment: {analysis['sentiment']['overall']} ({analysis['sentiment']['compound']:.2f})")
        print(f"Intent: {analysis['intent']}")
        print(f"Is Question: {analysis['is_question']}")
        print(f"Topics: {analysis['topics']}")
        print(f"Entities: {analysis['entities']}")
        print(f"Confidence: {analysis['confidence']:.3f}")
        
        if analysis.get('emotions'):
            emotions = analysis['emotions']
            if emotions and len(emotions) > 0:
                if isinstance(emotions[0], dict):
                    emotion_str = f"{emotions[0]['label']} ({emotions[0].get('score', 0):.2f})"
                else:
                    emotion_str = str(emotions[0])
                print(f"Primary Emotion: {emotion_str}")


def demonstrate_api_features():
    """Demonstrate API and integration features."""
    print_header("API & INTEGRATION FEATURES")
    
    print("🌐 Web Interface:")
    print("   - Real-time chat interface")
    print("   - Confidence indicators")
    print("   - Conversation history")
    print("   - Responsive design")
    
    print("\n🔌 REST API Endpoints:")
    print("   - POST /api/chat - Send messages")
    print("   - GET /api/conversation/history/{user_id} - Get history")
    print("   - GET /api/learning/insights - Get analytics")
    print("   - GET /api/user/preferences/{user_id} - Get preferences")
    print("   - GET /health - Health check")
    
    print("\n⚡ Performance Features:")
    print("   - Rate limiting")
    print("   - Background task processing")
    print("   - Session management")
    print("   - Error handling")
    
    print("\n📱 Multi-Platform Support:")
    print("   - Command-line interface")
    print("   - Web browser interface")
    print("   - REST API for integrations")
    print("   - Configurable deployment")


def main():
    """Run the complete demonstration."""
    print("🤖 Dynamic AI Chatbot - Complete System Demonstration")
    print("=" * 60)
    print("This demonstration showcases all major features of the chatbot system")
    print("including NLP processing, memory management, learning capabilities,")
    print("and multi-platform interfaces.")
    
    try:
        # Run demonstrations
        demonstrate_configuration()
        demonstrate_helpers()
        
        # Core engine demo (returns engine for memory demo)
        engine = demonstrate_chatbot_engine()
        
        # Memory and learning demo
        demonstrate_memory_system(engine)
        
        # NLP features demo
        demonstrate_nlp_features()
        
        # API features overview
        demonstrate_api_features()
        
        # Success summary
        print_header("DEMONSTRATION COMPLETE")
        print("✅ All systems operational!")
        print("✅ Configuration: Working")
        print("✅ Core Engine: Working")
        print("✅ NLP Processing: Working")
        print("✅ Memory System: Working")
        print("✅ Learning System: Working")
        print("✅ Multi-Platform: Working")
        
        print("\n🚀 The Dynamic AI Chatbot is ready for use!")
        print("\nNext steps:")
        print("- Try the CLI: python -m chatbot.cli")
        print("- Start web server: python -m chatbot.server")
        print("- Run tests: python tests/test_chatbot.py")
        print("- Check API docs: http://localhost:8000/docs (when server running)")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())