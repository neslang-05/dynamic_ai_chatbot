"""
Self-learning system for continuous improvement and personalization.
"""
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import numpy as np


class LearningSystem:
    """
    Implements self-learning capabilities for the chatbot including:
    - User preference learning
    - Response effectiveness tracking
    - Topic and pattern recognition
    - Conversation quality improvement
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.db_path = getattr(config, 'DATABASE_URL', 'sqlite:///chatbot_memory.db').replace('sqlite:///', '')
        self._init_learning_tables()
        
        # Learning parameters
        self.min_confidence_threshold = getattr(config, 'CONFIDENCE_THRESHOLD', 0.7)
        self.learning_rate = getattr(config, 'LEARNING_RATE', 0.001)
        
        self.logger.info("Learning System initialized")
    
    def _init_learning_tables(self):
        """Initialize database tables for learning system."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # User preferences table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        preference_type TEXT NOT NULL,
                        preference_value TEXT NOT NULL,
                        confidence_score REAL DEFAULT 0.5,
                        learned_at DATETIME NOT NULL,
                        last_reinforced DATETIME,
                        reinforcement_count INTEGER DEFAULT 1
                    )
                ''')
                
                # Response effectiveness table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS response_effectiveness (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        response_pattern TEXT NOT NULL,
                        context_type TEXT,
                        user_reaction TEXT,
                        effectiveness_score REAL DEFAULT 0.5,
                        usage_count INTEGER DEFAULT 1,
                        last_used DATETIME NOT NULL
                    )
                ''')
                
                # Learning patterns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS learning_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT NOT NULL,
                        frequency INTEGER DEFAULT 1,
                        success_rate REAL DEFAULT 0.5,
                        created_at DATETIME NOT NULL,
                        last_seen DATETIME NOT NULL
                    )
                ''')
                
                # Topic trends table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS topic_trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        topic TEXT NOT NULL,
                        interest_score REAL DEFAULT 0.5,
                        frequency INTEGER DEFAULT 1,
                        last_mentioned DATETIME NOT NULL,
                        context_keywords TEXT
                    )
                ''')
                
                # Conversation quality metrics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_quality (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        quality_score REAL,
                        engagement_level TEXT,
                        response_appropriateness REAL,
                        context_understanding REAL,
                        user_satisfaction_indicators TEXT,
                        calculated_at DATETIME NOT NULL
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_effectiveness_pattern ON response_effectiveness(response_pattern)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_topic_trends_user_topic ON topic_trends(user_id, topic)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_learning_patterns_type ON learning_patterns(pattern_type)')
                
                conn.commit()
                self.logger.info("Learning system database tables initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing learning tables: {e}")
            raise
    
    def learn_from_interaction(self, user_id: str, user_message: str, 
                             bot_response: str, nlp_analysis: Dict):
        """
        Learn from a conversation interaction to improve future responses.
        """
        try:
            # Learn user preferences
            self._learn_user_preferences(user_id, user_message, nlp_analysis)
            
            # Analyze and store response patterns
            self._analyze_response_effectiveness(user_message, bot_response, nlp_analysis)
            
            # Update topic trends
            self._update_topic_trends(user_id, nlp_analysis)
            
            # Learn conversation patterns
            self._learn_conversation_patterns(user_message, bot_response, nlp_analysis)
            
            # Calculate conversation quality metrics
            self._calculate_conversation_quality(user_id, user_message, bot_response, nlp_analysis)
            
            self.logger.debug(f"Learning completed for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error in learning from interaction: {e}")
    
    def _learn_user_preferences(self, user_id: str, user_message: str, nlp_analysis: Dict):
        """Learn and update user preferences from conversation."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract preferences from NLP analysis
                preferences = []
                
                # Topic preferences
                topics = nlp_analysis.get('topics', [])
                for topic in topics:
                    preferences.append(('topic_interest', topic, 0.6))
                
                # Emotional preferences (how user typically expresses emotions)
                emotions = nlp_analysis.get('emotions', [])
                if emotions:
                    primary_emotion = emotions[0] if isinstance(emotions, list) else emotions
                    if isinstance(primary_emotion, dict):
                        emotion_label = primary_emotion.get('label', '')
                        emotion_score = primary_emotion.get('score', 0.5)
                        if emotion_score > 0.7:  # High confidence emotions
                            preferences.append(('emotional_expression', emotion_label, emotion_score))
                
                # Communication style preferences
                complexity = nlp_analysis.get('complexity', {})
                if complexity:
                    word_count = complexity.get('word_count', 0)
                    if word_count > 20:
                        preferences.append(('communication_style', 'detailed', 0.6))
                    elif word_count < 5:
                        preferences.append(('communication_style', 'brief', 0.6))
                
                # Intent preferences
                intent = nlp_analysis.get('intent', 'general')
                if intent != 'general':
                    preferences.append(('preferred_intent', intent, 0.5))
                
                # Store or update preferences
                for pref_type, pref_value, confidence in preferences:
                    # Check if preference already exists
                    cursor.execute('''
                        SELECT id, confidence_score, reinforcement_count
                        FROM user_preferences
                        WHERE user_id = ? AND preference_type = ? AND preference_value = ?
                    ''', (user_id, pref_type, pref_value))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing preference
                        pref_id, old_confidence, reinforcement_count = existing
                        new_confidence = min(1.0, old_confidence + (confidence * self.learning_rate))
                        
                        cursor.execute('''
                            UPDATE user_preferences
                            SET confidence_score = ?, last_reinforced = ?, 
                                reinforcement_count = reinforcement_count + 1
                            WHERE id = ?
                        ''', (new_confidence, datetime.now(), pref_id))
                    else:
                        # Create new preference
                        cursor.execute('''
                            INSERT INTO user_preferences
                            (user_id, preference_type, preference_value, confidence_score, 
                             learned_at, last_reinforced, reinforcement_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (user_id, pref_type, pref_value, confidence, 
                              datetime.now(), datetime.now(), 1))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error learning user preferences: {e}")
    
    def _analyze_response_effectiveness(self, user_message: str, bot_response: str, nlp_analysis: Dict):
        """Analyze and store response effectiveness patterns."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create response pattern (simplified)
                response_length = len(bot_response.split())
                response_pattern = f"length_{response_length}_intent_{nlp_analysis.get('intent', 'general')}"
                
                # Determine context type
                context_type = self._determine_context_type(nlp_analysis)
                
                # Estimate effectiveness based on various factors
                effectiveness_score = self._estimate_response_effectiveness(
                    user_message, bot_response, nlp_analysis
                )
                
                # Check if pattern exists
                cursor.execute('''
                    SELECT id, effectiveness_score, usage_count
                    FROM response_effectiveness
                    WHERE response_pattern = ? AND context_type = ?
                ''', (response_pattern, context_type))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing pattern
                    pattern_id, old_score, usage_count = existing
                    new_score = (old_score * usage_count + effectiveness_score) / (usage_count + 1)
                    
                    cursor.execute('''
                        UPDATE response_effectiveness
                        SET effectiveness_score = ?, usage_count = usage_count + 1, last_used = ?
                        WHERE id = ?
                    ''', (new_score, datetime.now(), pattern_id))
                else:
                    # Create new pattern
                    cursor.execute('''
                        INSERT INTO response_effectiveness
                        (response_pattern, context_type, effectiveness_score, usage_count, last_used)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (response_pattern, context_type, effectiveness_score, 1, datetime.now()))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error analyzing response effectiveness: {e}")
    
    def _update_topic_trends(self, user_id: str, nlp_analysis: Dict):
        """Update topic trends and interests for the user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                topics = nlp_analysis.get('topics', [])
                entities = nlp_analysis.get('entities', [])
                
                # Combine topics and entities
                all_topics = topics + [entity.lower() for entity in entities if entity.isalpha()]
                
                for topic in all_topics:
                    if len(topic) > 2:  # Skip very short topics
                        # Check if topic trend exists
                        cursor.execute('''
                            SELECT id, interest_score, frequency
                            FROM topic_trends
                            WHERE user_id = ? AND topic = ?
                        ''', (user_id, topic))
                        
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Update existing trend
                            trend_id, interest_score, frequency = existing
                            new_interest = min(1.0, interest_score + 0.1)
                            
                            cursor.execute('''
                                UPDATE topic_trends
                                SET interest_score = ?, frequency = frequency + 1, 
                                    last_mentioned = ?
                                WHERE id = ?
                            ''', (new_interest, datetime.now(), trend_id))
                        else:
                            # Create new trend
                            cursor.execute('''
                                INSERT INTO topic_trends
                                (user_id, topic, interest_score, frequency, last_mentioned, context_keywords)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (user_id, topic, 0.6, 1, datetime.now(), 
                                  json.dumps(nlp_analysis.get('entities', []))))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error updating topic trends: {e}")
    
    def _learn_conversation_patterns(self, user_message: str, bot_response: str, nlp_analysis: Dict):
        """Learn conversation patterns for future improvement."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create different types of patterns
                patterns = []
                
                # Question-Answer patterns
                if nlp_analysis.get('is_question', False):
                    question_type = self._classify_question_type(user_message)
                    patterns.append(('question_pattern', {
                        'question_type': question_type,
                        'response_style': self._classify_response_style(bot_response),
                        'entities': nlp_analysis.get('entities', [])
                    }))
                
                # Emotional response patterns
                emotions = nlp_analysis.get('emotions', [])
                if emotions:
                    primary_emotion = emotions[0] if isinstance(emotions, list) else emotions
                    if isinstance(primary_emotion, dict):
                        emotion_label = primary_emotion.get('label', '')
                        patterns.append(('emotional_pattern', {
                            'input_emotion': emotion_label,
                            'response_tone': self._analyze_response_tone(bot_response),
                            'sentiment': nlp_analysis.get('sentiment', {})
                        }))
                
                # Intent-Response patterns
                intent = nlp_analysis.get('intent', 'general')
                if intent != 'general':
                    patterns.append(('intent_pattern', {
                        'intent': intent,
                        'response_approach': self._classify_response_approach(bot_response),
                        'success_indicators': self._extract_success_indicators(nlp_analysis)
                    }))
                
                # Store patterns
                for pattern_type, pattern_data in patterns:
                    pattern_json = json.dumps(pattern_data)
                    
                    # Check if similar pattern exists
                    cursor.execute('''
                        SELECT id, frequency, success_rate
                        FROM learning_patterns
                        WHERE pattern_type = ? AND pattern_data = ?
                    ''', (pattern_type, pattern_json))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing pattern
                        pattern_id, frequency, success_rate = existing
                        estimated_success = self._estimate_pattern_success(nlp_analysis)
                        new_success_rate = (success_rate * frequency + estimated_success) / (frequency + 1)
                        
                        cursor.execute('''
                            UPDATE learning_patterns
                            SET frequency = frequency + 1, success_rate = ?, last_seen = ?
                            WHERE id = ?
                        ''', (new_success_rate, datetime.now(), pattern_id))
                    else:
                        # Create new pattern
                        estimated_success = self._estimate_pattern_success(nlp_analysis)
                        cursor.execute('''
                            INSERT INTO learning_patterns
                            (pattern_type, pattern_data, frequency, success_rate, created_at, last_seen)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (pattern_type, pattern_json, 1, estimated_success, 
                              datetime.now(), datetime.now()))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error learning conversation patterns: {e}")
    
    def _calculate_conversation_quality(self, user_id: str, user_message: str, 
                                      bot_response: str, nlp_analysis: Dict):
        """Calculate and store conversation quality metrics."""
        try:
            # Calculate various quality metrics
            context_understanding = self._assess_context_understanding(nlp_analysis)
            response_appropriateness = self._assess_response_appropriateness(
                user_message, bot_response, nlp_analysis
            )
            engagement_level = self._assess_engagement_level(user_message, nlp_analysis)
            
            # Overall quality score
            quality_score = (context_understanding + response_appropriateness + 
                           self._convert_engagement_to_score(engagement_level)) / 3
            
            # Store quality metrics (associated with session if available)
            session_id = getattr(self, 'current_session_id', 'unknown')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO conversation_quality
                    (session_id, user_id, quality_score, engagement_level, 
                     response_appropriateness, context_understanding, 
                     user_satisfaction_indicators, calculated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, user_id, quality_score, engagement_level,
                      response_appropriateness, context_understanding,
                      json.dumps(self._extract_satisfaction_indicators(nlp_analysis)),
                      datetime.now()))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error calculating conversation quality: {e}")
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get learned preferences for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT preference_type, preference_value, confidence_score, reinforcement_count
                    FROM user_preferences
                    WHERE user_id = ? AND confidence_score > ?
                    ORDER BY confidence_score DESC, reinforcement_count DESC
                ''', (user_id, self.min_confidence_threshold))
                
                preferences = defaultdict(list)
                for row in cursor.fetchall():
                    pref_type, pref_value, confidence, reinforcement = row
                    preferences[pref_type].append({
                        'value': pref_value,
                        'confidence': confidence,
                        'reinforcement_count': reinforcement
                    })
                
                return dict(preferences)
                
        except Exception as e:
            self.logger.error(f"Error getting user preferences: {e}")
            return {}
    
    def get_effective_response_patterns(self, context_type: str = None, limit: int = 10) -> List[Dict]:
        """Get most effective response patterns."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if context_type:
                    cursor.execute('''
                        SELECT response_pattern, context_type, effectiveness_score, usage_count
                        FROM response_effectiveness
                        WHERE context_type = ?
                        ORDER BY effectiveness_score DESC, usage_count DESC
                        LIMIT ?
                    ''', (context_type, limit))
                else:
                    cursor.execute('''
                        SELECT response_pattern, context_type, effectiveness_score, usage_count
                        FROM response_effectiveness
                        ORDER BY effectiveness_score DESC, usage_count DESC
                        LIMIT ?
                    ''', (limit,))
                
                patterns = []
                for row in cursor.fetchall():
                    patterns.append({
                        'pattern': row[0],
                        'context_type': row[1],
                        'effectiveness_score': row[2],
                        'usage_count': row[3]
                    })
                
                return patterns
                
        except Exception as e:
            self.logger.error(f"Error getting effective response patterns: {e}")
            return []
    
    def get_learning_insights(self, user_id: Optional[str] = None, days: int = 30) -> Dict:
        """Get insights from the learning system."""
        try:
            insights = {}
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Top topics for user or globally
                if user_id:
                    cursor.execute('''
                        SELECT topic, interest_score, frequency
                        FROM topic_trends
                        WHERE user_id = ? AND last_mentioned >= ?
                        ORDER BY interest_score DESC, frequency DESC
                        LIMIT 10
                    ''', (user_id, cutoff_date))
                else:
                    cursor.execute('''
                        SELECT topic, AVG(interest_score) as avg_interest, SUM(frequency) as total_frequency
                        FROM topic_trends
                        WHERE last_mentioned >= ?
                        GROUP BY topic
                        ORDER BY avg_interest DESC, total_frequency DESC
                        LIMIT 10
                    ''', (cutoff_date,))
                
                insights['top_topics'] = [
                    {'topic': row[0], 'score': row[1], 'frequency': row[2]}
                    for row in cursor.fetchall()
                ]
                
                # Most effective response patterns
                cursor.execute('''
                    SELECT response_pattern, AVG(effectiveness_score) as avg_effectiveness, SUM(usage_count) as total_usage
                    FROM response_effectiveness
                    WHERE last_used >= ?
                    GROUP BY response_pattern
                    ORDER BY avg_effectiveness DESC
                    LIMIT 5
                ''', (cutoff_date,))
                
                insights['effective_patterns'] = [
                    {'pattern': row[0], 'effectiveness': row[1], 'usage': row[2]}
                    for row in cursor.fetchall()
                ]
                
                # Quality trends
                quality_filter = "WHERE calculated_at >= ?"
                params = [cutoff_date]
                if user_id:
                    quality_filter += " AND user_id = ?"
                    params.append(user_id)
                
                cursor.execute(f'''
                    SELECT AVG(quality_score) as avg_quality,
                           AVG(response_appropriateness) as avg_appropriateness,
                           AVG(context_understanding) as avg_understanding
                    FROM conversation_quality
                    {quality_filter}
                ''', params)
                
                quality_row = cursor.fetchone()
                if quality_row and quality_row[0] is not None:
                    insights['quality_metrics'] = {
                        'average_quality': quality_row[0],
                        'average_appropriateness': quality_row[1],
                        'average_understanding': quality_row[2]
                    }
                
                return insights
                
        except Exception as e:
            self.logger.error(f"Error getting learning insights: {e}")
            return {}
    
    # Helper methods for analysis
    
    def _determine_context_type(self, nlp_analysis: Dict) -> str:
        """Determine context type from NLP analysis."""
        if nlp_analysis.get('is_question', False):
            return 'question'
        
        emotions = nlp_analysis.get('emotions', [])
        if emotions:
            return 'emotional'
        
        intent = nlp_analysis.get('intent', 'general')
        return intent
    
    def _estimate_response_effectiveness(self, user_message: str, bot_response: str, nlp_analysis: Dict) -> float:
        """Estimate response effectiveness based on various factors."""
        score = 0.5  # Base score
        
        # Response length appropriateness
        response_length = len(bot_response.split())
        message_length = len(user_message.split())
        
        if 5 <= response_length <= 50:  # Good response length
            score += 0.1
        
        # Question handling
        if nlp_analysis.get('is_question', False):
            if any(word in bot_response.lower() for word in ['because', 'due to', 'reason', 'answer']):
                score += 0.2
        
        # Emotional appropriateness
        emotions = nlp_analysis.get('emotions', [])
        if emotions:
            # Simple check: if user seems negative, response should be supportive
            primary_emotion = emotions[0] if isinstance(emotions, list) else emotions
            if isinstance(primary_emotion, dict):
                emotion_label = primary_emotion.get('label', '').lower()
                if any(word in emotion_label for word in ['sad', 'anger', 'fear']):
                    if any(word in bot_response.lower() for word in ['sorry', 'understand', 'help']):
                        score += 0.2
        
        return min(1.0, score)
    
    def _classify_question_type(self, message: str) -> str:
        """Classify the type of question."""
        message_lower = message.lower()
        if any(word in message_lower for word in ['what', 'which']):
            return 'what'
        elif any(word in message_lower for word in ['how']):
            return 'how'
        elif any(word in message_lower for word in ['why']):
            return 'why'
        elif any(word in message_lower for word in ['when']):
            return 'when'
        elif any(word in message_lower for word in ['where']):
            return 'where'
        elif any(word in message_lower for word in ['who']):
            return 'who'
        else:
            return 'general'
    
    def _classify_response_style(self, response: str) -> str:
        """Classify the style of the response."""
        word_count = len(response.split())
        if word_count < 10:
            return 'brief'
        elif word_count > 30:
            return 'detailed'
        else:
            return 'moderate'
    
    def _analyze_response_tone(self, response: str) -> str:
        """Analyze the tone of the response."""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['sorry', 'apologize', 'understand']):
            return 'empathetic'
        elif any(word in response_lower for word in ['great', 'wonderful', 'excellent']):
            return 'positive'
        elif any(word in response_lower for word in ['help', 'assist', 'support']):
            return 'helpful'
        else:
            return 'neutral'
    
    def _classify_response_approach(self, response: str) -> str:
        """Classify the approach used in the response."""
        response_lower = response.lower()
        
        if '?' in response:
            return 'questioning'
        elif any(word in response_lower for word in ['because', 'due to', 'reason']):
            return 'explanatory'
        elif any(word in response_lower for word in ['try', 'suggest', 'recommend']):
            return 'suggestive'
        else:
            return 'informative'
    
    def _extract_success_indicators(self, nlp_analysis: Dict) -> List[str]:
        """Extract indicators of successful interaction."""
        indicators = []
        
        confidence = nlp_analysis.get('confidence', 0.5)
        if confidence > 0.7:
            indicators.append('high_confidence')
        
        if nlp_analysis.get('entities'):
            indicators.append('entity_recognition')
        
        if nlp_analysis.get('topics'):
            indicators.append('topic_identification')
        
        return indicators
    
    def _estimate_pattern_success(self, nlp_analysis: Dict) -> float:
        """Estimate success rate of a pattern."""
        base_score = 0.5
        
        # High confidence indicates success
        confidence = nlp_analysis.get('confidence', 0.5)
        base_score += (confidence - 0.5) * 0.5
        
        # Entity recognition indicates understanding
        if nlp_analysis.get('entities'):
            base_score += 0.1
        
        # Topic identification indicates relevance
        if nlp_analysis.get('topics'):
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _assess_context_understanding(self, nlp_analysis: Dict) -> float:
        """Assess how well context was understood."""
        score = 0.3  # Base score
        
        # Entity recognition
        if nlp_analysis.get('entities'):
            score += 0.2
        
        # Topic identification
        if nlp_analysis.get('topics'):
            score += 0.2
        
        # Intent classification
        if nlp_analysis.get('intent', 'general') != 'general':
            score += 0.2
        
        # Confidence level
        confidence = nlp_analysis.get('confidence', 0.5)
        score += confidence * 0.1
        
        return min(1.0, score)
    
    def _assess_response_appropriateness(self, user_message: str, bot_response: str, nlp_analysis: Dict) -> float:
        """Assess appropriateness of the response."""
        score = 0.5  # Base score
        
        # Length appropriateness
        response_length = len(bot_response.split())
        if 5 <= response_length <= 50:
            score += 0.2
        
        # Question handling
        if nlp_analysis.get('is_question', False):
            if any(indicator in bot_response.lower() for indicator in ['answer', 'because', 'explain']):
                score += 0.2
        
        # Emotional appropriateness
        emotions = nlp_analysis.get('emotions', [])
        if emotions:
            score += 0.1  # Basic emotional acknowledgment
        
        return min(1.0, score)
    
    def _assess_engagement_level(self, user_message: str, nlp_analysis: Dict) -> str:
        """Assess user engagement level."""
        word_count = len(user_message.split())
        
        if word_count > 20:
            return 'high'
        elif word_count > 10:
            return 'medium'
        else:
            return 'low'
    
    def _convert_engagement_to_score(self, engagement_level: str) -> float:
        """Convert engagement level to numeric score."""
        engagement_scores = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
        return engagement_scores.get(engagement_level, 0.5)
    
    def _extract_satisfaction_indicators(self, nlp_analysis: Dict) -> List[str]:
        """Extract indicators of user satisfaction."""
        indicators = []
        
        sentiment = nlp_analysis.get('sentiment', {})
        if sentiment.get('compound', 0) > 0.3:
            indicators.append('positive_sentiment')
        elif sentiment.get('compound', 0) < -0.3:
            indicators.append('negative_sentiment')
        
        emotions = nlp_analysis.get('emotions', [])
        if emotions:
            primary_emotion = emotions[0] if isinstance(emotions, list) else emotions
            if isinstance(primary_emotion, dict):
                emotion_label = primary_emotion.get('label', '').lower()
                if 'joy' in emotion_label or 'happiness' in emotion_label:
                    indicators.append('positive_emotion')
                elif any(neg_emotion in emotion_label for neg_emotion in ['sad', 'anger', 'fear']):
                    indicators.append('negative_emotion')
        
        return indicators