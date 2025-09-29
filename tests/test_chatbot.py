"""
Test suite for the dynamic AI chatbot.
"""
import unittest
import tempfile
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.core.engine import ChatbotEngine
from chatbot.nlp.processor import NLPProcessor
from chatbot.memory.conversation_memory import ConversationMemory
from chatbot.memory.learning_system import LearningSystem
from chatbot.utils.config import Config
from chatbot.utils.helpers import (
    clean_text, extract_keywords, calculate_text_similarity,
    validate_user_input, analyze_text_complexity
)


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test config initialization with defaults."""
        config = Config()
        
        self.assertEqual(config.CHATBOT_NAME, 'DynamicAI')
        self.assertIsInstance(config.MAX_HISTORY_LENGTH, int)
        self.assertIsInstance(config.CONFIDENCE_THRESHOLD, float)
        self.assertTrue(0 <= config.CONFIDENCE_THRESHOLD <= 1)
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        self.assertTrue(config.validate_config())
    
    def test_config_methods(self):
        """Test configuration helper methods."""
        config = Config()
        
        model_config = config.get_model_config()
        self.assertIn('model_name', model_config)
        
        db_config = config.get_database_config()
        self.assertIn('url', db_config)
        
        feature_flags = config.get_feature_flags()
        self.assertIn('sentiment_analysis', feature_flags)


class TestHelpers(unittest.TestCase):
    """Test utility helper functions."""
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        self.assertEqual(clean_text("  Hello   world!  "), "Hello world!")
        self.assertEqual(clean_text("Test@#$%text"), "Testtext")
        self.assertEqual(clean_text(""), "")
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "This is a test sentence about machine learning and AI"
        keywords = extract_keywords(text)
        
        self.assertIn('test', keywords)
        self.assertIn('machine', keywords)
        self.assertIn('learning', keywords)
        self.assertNotIn('is', keywords)  # Stop word
        self.assertNotIn('a', keywords)   # Stop word
    
    def test_calculate_text_similarity(self):
        """Test text similarity calculation."""
        text1 = "Hello world"
        text2 = "Hello there"
        text3 = "Goodbye world"
        
        sim1 = calculate_text_similarity(text1, text2)
        sim2 = calculate_text_similarity(text1, text3)
        
        self.assertGreater(sim1, 0)
        self.assertGreater(sim2, 0)
        self.assertGreater(sim1, sim2)  # text1 and text2 should be more similar
    
    def test_validate_user_input(self):
        """Test user input validation."""
        # Valid input
        result = validate_user_input("Hello, how are you?")
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        
        # Empty input
        result = validate_user_input("")
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
        
        # Too long input
        result = validate_user_input("a" * 2000, max_length=1000)
        self.assertFalse(result['valid'])
    
    def test_analyze_text_complexity(self):
        """Test text complexity analysis."""
        simple_text = "Hi there"
        complex_text = "The implementation of sophisticated natural language processing algorithms requires comprehensive understanding of computational linguistics."
        
        simple_analysis = analyze_text_complexity(simple_text)
        complex_analysis = analyze_text_complexity(complex_text)
        
        self.assertLess(simple_analysis['complexity_score'], complex_analysis['complexity_score'])
        self.assertGreater(complex_analysis['word_count'], simple_analysis['word_count'])


class TestNLPProcessor(unittest.TestCase):
    """Test NLP processing functionality."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = Config()
        self.processor = NLPProcessor(self.config)
    
    def test_text_cleaning(self):
        """Test text preprocessing."""
        dirty_text = "  Hello!!!   How are you???  "
        clean = self.processor._clean_text(dirty_text)
        
        self.assertEqual(clean, "Hello!!! How are you???")
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis."""
        positive_text = "I'm very happy today!"
        negative_text = "I'm feeling sad and depressed"
        neutral_text = "The weather is okay"
        
        pos_sentiment = self.processor._analyze_sentiment(positive_text)
        neg_sentiment = self.processor._analyze_sentiment(negative_text)
        neu_sentiment = self.processor._analyze_sentiment(neutral_text)
        
        self.assertEqual(pos_sentiment['overall'], 'positive')
        self.assertEqual(neg_sentiment['overall'], 'negative')
        self.assertEqual(neu_sentiment['overall'], 'neutral')
    
    def test_question_detection(self):
        """Test question detection."""
        question1 = "How are you today?"
        question2 = "What is machine learning"
        statement = "I am fine today"
        
        self.assertTrue(self.processor._is_question(question1))
        self.assertTrue(self.processor._is_question(question2))
        self.assertFalse(self.processor._is_question(statement))
    
    def test_intent_classification(self):
        """Test intent classification."""
        greeting = "Hello there!"
        question = "How does this work?"
        help_request = "I need help with something"
        
        self.assertEqual(self.processor._classify_intent(greeting), 'greeting')
        self.assertEqual(self.processor._classify_intent(question), 'question')
        self.assertEqual(self.processor._classify_intent(help_request), 'help_request')
    
    def test_message_analysis(self):
        """Test comprehensive message analysis."""
        message = "Hi! I'm feeling excited about learning AI. How does machine learning work?"
        
        analysis = self.processor.analyze_message(message)
        
        self.assertIn('sentiment', analysis)
        self.assertIn('emotions', analysis)
        self.assertIn('entities', analysis)
        self.assertIn('intent', analysis)
        self.assertIn('is_question', analysis)
        self.assertIn('complexity', analysis)
        self.assertIn('confidence', analysis)
        
        self.assertTrue(analysis['is_question'])
        self.assertEqual(analysis['intent'], 'question')


class TestConversationMemory(unittest.TestCase):
    """Test conversation memory functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create config with test database
        os.environ['DATABASE_URL'] = f'sqlite:///{self.temp_db.name}'
        self.config = Config()
        self.memory = ConversationMemory(self.config)
    
    def tearDown(self):
        """Clean up test database."""
        os.unlink(self.temp_db.name)
    
    def test_store_conversation(self):
        """Test conversation storage."""
        conversation_data = {
            'session_id': 'test_session_1',
            'user_id': 'test_user',
            'user_message': 'Hello there!',
            'bot_response': 'Hello! How can I help you?',
            'timestamp': datetime.now(),
            'nlp_analysis': {'sentiment': {'overall': 'positive'}},
            'context_keywords': ['hello', 'greeting']
        }
        
        # Should not raise an exception
        self.memory.store_conversation(conversation_data)
    
    def test_get_recent_conversations(self):
        """Test retrieving recent conversations."""
        # Store a test conversation first
        conversation_data = {
            'session_id': 'test_session_2',
            'user_id': 'test_user_2',
            'user_message': 'Test message',
            'bot_response': 'Test response',
            'timestamp': datetime.now(),
            'nlp_analysis': {},
            'context_keywords': []
        }
        
        self.memory.store_conversation(conversation_data)
        
        # Retrieve conversations
        conversations = self.memory.get_recent_conversations('test_user_2')
        self.assertGreaterEqual(len(conversations), 1)
        
        # Check the stored conversation
        stored_conv = conversations[0]
        self.assertEqual(stored_conv['user_message'], 'Test message')
        self.assertEqual(stored_conv['bot_response'], 'Test response')
    
    def test_find_similar_conversations(self):
        """Test finding similar conversations."""
        # Store some test conversations
        conversations = [
            {
                'session_id': 'sim_test_1',
                'user_id': 'sim_user',
                'user_message': 'How does machine learning work?',
                'bot_response': 'Machine learning is a subset of AI...',
                'timestamp': datetime.now(),
                'nlp_analysis': {},
                'context_keywords': []
            },
            {
                'session_id': 'sim_test_2',
                'user_id': 'sim_user',
                'user_message': 'What is artificial intelligence?',
                'bot_response': 'AI is the simulation of human intelligence...',
                'timestamp': datetime.now(),
                'nlp_analysis': {},
                'context_keywords': []
            }
        ]
        
        for conv in conversations:
            self.memory.store_conversation(conv)
        
        # Find similar conversations
        similar = self.memory.find_similar_conversations(
            'Tell me about machine learning', 
            user_id='sim_user'
        )
        
        self.assertGreaterEqual(len(similar), 1)
    
    def test_user_profile_creation(self):
        """Test user profile creation and updates."""
        # Store a conversation to trigger profile creation
        conversation_data = {
            'session_id': 'profile_test',
            'user_id': 'profile_user',
            'user_message': 'Hello!',
            'bot_response': 'Hi there!',
            'timestamp': datetime.now(),
            'nlp_analysis': {},
            'context_keywords': []
        }
        
        self.memory.store_conversation(conversation_data)
        
        # Check if profile was created
        profile = self.memory.get_user_profile('profile_user')
        self.assertIsNotNone(profile)
        self.assertEqual(profile['user_id'], 'profile_user')
        self.assertGreaterEqual(profile['total_messages'], 1)


class TestLearningSystem(unittest.TestCase):
    """Test learning system functionality."""
    
    def setUp(self):
        """Set up test learning system."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        os.environ['DATABASE_URL'] = f'sqlite:///{self.temp_db.name}'
        self.config = Config()
        self.learning_system = LearningSystem(self.config)
    
    def tearDown(self):
        """Clean up test database."""
        os.unlink(self.temp_db.name)
    
    def test_learn_from_interaction(self):
        """Test learning from interactions."""
        nlp_analysis = {
            'sentiment': {'overall': 'positive', 'compound': 0.8},
            'emotions': [{'label': 'joy', 'score': 0.9}],
            'topics': ['technology', 'ai'],
            'entities': ['Python', 'machine learning'],
            'intent': 'question',
            'is_question': True,
            'confidence': 0.85
        }
        
        # Should not raise an exception
        self.learning_system.learn_from_interaction(
            'test_learner',
            'I love learning about AI and Python!',
            'That\'s great! AI and Python are fascinating topics.',
            nlp_analysis
        )
    
    def test_get_user_preferences(self):
        """Test retrieving user preferences."""
        # First, learn from an interaction
        nlp_analysis = {
            'topics': ['technology', 'programming'],
            'emotions': [{'label': 'joy', 'score': 0.8}],
            'intent': 'general',
            'confidence': 0.7
        }
        
        self.learning_system.learn_from_interaction(
            'pref_user',
            'I enjoy programming and technology',
            'That\'s wonderful!',
            nlp_analysis
        )
        
        # Get preferences
        preferences = self.learning_system.get_user_preferences('pref_user')
        self.assertIsInstance(preferences, dict)
    
    def test_learning_insights(self):
        """Test learning insights generation."""
        # Add some learning data
        nlp_analysis = {
            'topics': ['science'],
            'emotions': [{'label': 'curiosity', 'score': 0.7}],
            'intent': 'question',
            'confidence': 0.8
        }
        
        self.learning_system.learn_from_interaction(
            'insight_user',
            'Tell me about science',
            'Science is fascinating!',
            nlp_analysis
        )
        
        # Get insights
        insights = self.learning_system.get_learning_insights()
        self.assertIsInstance(insights, dict)


class TestChatbotEngine(unittest.TestCase):
    """Test the main chatbot engine."""
    
    def setUp(self):
        """Set up test chatbot engine."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        os.environ['DATABASE_URL'] = f'sqlite:///{self.temp_db.name}'
        self.config = Config()
        self.engine = ChatbotEngine(self.config)
    
    def tearDown(self):
        """Clean up test resources."""
        os.unlink(self.temp_db.name)
    
    def test_start_conversation(self):
        """Test conversation initialization."""
        session_id = self.engine.start_conversation('test_user')
        
        self.assertIsNotNone(session_id)
        self.assertEqual(self.engine.current_session_id, session_id)
        self.assertIn('test_user', session_id)
    
    def test_process_message(self):
        """Test message processing."""
        self.engine.start_conversation('test_processor')
        
        response_data = self.engine.process_message(
            'Hello! How are you today?',
            'test_processor'
        )
        
        self.assertIn('response', response_data)
        self.assertIn('confidence', response_data)
        self.assertIn('session_id', response_data)
        self.assertIn('timestamp', response_data)
        
        self.assertIsInstance(response_data['response'], str)
        self.assertGreater(len(response_data['response']), 0)
        self.assertIsInstance(response_data['confidence'], float)
        self.assertTrue(0 <= response_data['confidence'] <= 1)
    
    def test_conversation_stats(self):
        """Test conversation statistics."""
        # Start conversation and send a message
        self.engine.start_conversation('stats_user')
        self.engine.process_message('Test message', 'stats_user')
        
        stats = self.engine.get_conversation_stats()
        
        self.assertIn('session_id', stats)
        self.assertIn('message_count', stats)
        self.assertEqual(stats['message_count'], 1)
    
    def test_end_conversation(self):
        """Test conversation ending."""
        self.engine.start_conversation('end_user')
        session_id = self.engine.current_session_id
        
        self.engine.end_conversation()
        
        self.assertIsNone(self.engine.current_session_id)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        os.environ['DATABASE_URL'] = f'sqlite:///{self.temp_db.name}'
        self.config = Config()
        self.engine = ChatbotEngine(self.config)
    
    def tearDown(self):
        """Clean up integration test resources."""
        os.unlink(self.temp_db.name)
    
    def test_full_conversation_flow(self):
        """Test a complete conversation flow."""
        user_id = 'integration_user'
        
        # Start conversation
        session_id = self.engine.start_conversation(user_id)
        self.assertIsNotNone(session_id)
        
        # Send multiple messages
        messages = [
            'Hello! How are you?',
            'Can you help me with something?',
            'I\'m interested in machine learning',
            'Thank you for your help!'
        ]
        
        responses = []
        for message in messages:
            response_data = self.engine.process_message(message, user_id)
            responses.append(response_data)
            
            # Verify response structure
            self.assertIn('response', response_data)
            self.assertIn('confidence', response_data)
            self.assertEqual(response_data['session_id'], session_id)
        
        # Check conversation stats
        stats = self.engine.get_conversation_stats()
        self.assertEqual(stats['message_count'], len(messages))
        
        # End conversation
        self.engine.end_conversation()
        
        # Verify conversation was stored
        history = self.engine.conversation_memory.get_recent_conversations(user_id)
        self.assertEqual(len(history), len(messages))
    
    def test_learning_persistence(self):
        """Test that learning persists across conversations."""
        user_id = 'learning_user'
        
        # First conversation
        self.engine.start_conversation(user_id)
        self.engine.process_message('I love artificial intelligence!', user_id)
        self.engine.end_conversation()
        
        # Second conversation
        self.engine.start_conversation(user_id)
        response_data = self.engine.process_message('Tell me more about AI', user_id)
        self.engine.end_conversation()
        
        # Verify learning system has data
        preferences = self.engine.learning_system.get_user_preferences(user_id)
        self.assertIsInstance(preferences, dict)
        
        # Verify conversation history
        history = self.engine.conversation_memory.get_recent_conversations(user_id)
        self.assertEqual(len(history), 2)


def run_tests():
    """Run all tests."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run individual test classes or all tests
    if len(sys.argv) > 1:
        # Run specific test class
        unittest.main()
    else:
        # Run all tests
        success = run_tests()
        sys.exit(0 if success else 1)