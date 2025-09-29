"""
Conversation memory system for storing and retrieving conversation history.
"""
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class ConversationMemory:
    """
    Manages conversation storage, retrieval, and similarity matching
    for contextual conversation continuity.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.db_path = getattr(config, 'DATABASE_URL', 'sqlite:///chatbot_memory.db').replace('sqlite:///', '')
        self._init_database()
        
        self.logger.info("Conversation Memory initialized")
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Conversations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        bot_response TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        nlp_analysis TEXT,
                        context_keywords TEXT,
                        embedding_vector TEXT
                    )
                ''')
                
                # Session summaries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS session_summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        user_id TEXT NOT NULL,
                        start_time DATETIME,
                        end_time DATETIME,
                        duration_seconds INTEGER,
                        message_count INTEGER,
                        final_keywords TEXT,
                        summary TEXT
                    )
                ''')
                
                # User profiles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT UNIQUE NOT NULL,
                        created_at DATETIME NOT NULL,
                        last_active DATETIME NOT NULL,
                        total_conversations INTEGER DEFAULT 0,
                        total_messages INTEGER DEFAULT 0,
                        preferences TEXT,
                        common_topics TEXT
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id)')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def store_conversation(self, conversation_data: Dict):
        """Store a conversation turn in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare data
                nlp_analysis_json = json.dumps(conversation_data.get('nlp_analysis', {}))
                context_keywords_json = json.dumps(conversation_data.get('context_keywords', []))
                
                # Store conversation
                cursor.execute('''
                    INSERT INTO conversations 
                    (session_id, user_id, user_message, bot_response, timestamp, 
                     nlp_analysis, context_keywords, embedding_vector)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    conversation_data['session_id'],
                    conversation_data['user_id'],
                    conversation_data['user_message'],
                    conversation_data['bot_response'],
                    conversation_data['timestamp'],
                    nlp_analysis_json,
                    context_keywords_json,
                    ''  # Embedding will be added later if needed
                ))
                
                conn.commit()
                
                # Update user profile
                self._update_user_profile(conversation_data['user_id'])
                
                self.logger.debug(f"Stored conversation for session {conversation_data['session_id']}")
                
        except Exception as e:
            self.logger.error(f"Error storing conversation: {e}")
    
    def store_session_summary(self, summary_data: Dict):
        """Store conversation session summary."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO session_summaries
                    (session_id, user_id, start_time, end_time, duration_seconds, 
                     message_count, final_keywords, summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    summary_data['session_id'],
                    summary_data['user_id'],
                    summary_data.get('start_time'),
                    datetime.now(),
                    summary_data.get('duration', 0),
                    summary_data.get('message_count', 0),
                    json.dumps(summary_data.get('final_keywords', [])),
                    summary_data.get('summary', '')
                ))
                
                conn.commit()
                self.logger.debug(f"Stored session summary for {summary_data['session_id']}")
                
        except Exception as e:
            self.logger.error(f"Error storing session summary: {e}")
    
    def get_recent_conversations(self, user_id: str, limit: int = 10, days: int = 7) -> List[Dict]:
        """Get recent conversations for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get conversations from the last N days
                cutoff_date = datetime.now() - timedelta(days=days)
                
                cursor.execute('''
                    SELECT session_id, user_message, bot_response, timestamp, 
                           nlp_analysis, context_keywords
                    FROM conversations
                    WHERE user_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, cutoff_date, limit))
                
                conversations = []
                for row in cursor.fetchall():
                    conv = {
                        'session_id': row[0],
                        'user_message': row[1],
                        'bot_response': row[2],
                        'timestamp': row[3],
                        'nlp_analysis': json.loads(row[4]) if row[4] else {},
                        'context_keywords': json.loads(row[5]) if row[5] else []
                    }
                    conversations.append(conv)
                
                return conversations
                
        except Exception as e:
            self.logger.error(f"Error retrieving recent conversations: {e}")
            return []
    
    def find_similar_conversations(self, message: str, user_id: Optional[str] = None, 
                                 limit: int = 5, similarity_threshold: float = 0.3) -> List[Dict]:
        """Find similar conversations based on message content."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query based on whether user_id is provided
                if user_id:
                    query = '''
                        SELECT user_message, bot_response, timestamp, nlp_analysis
                        FROM conversations
                        WHERE user_id = ?
                        ORDER BY timestamp DESC
                        LIMIT 100
                    '''
                    cursor.execute(query, (user_id,))
                else:
                    query = '''
                        SELECT user_message, bot_response, timestamp, nlp_analysis
                        FROM conversations
                        ORDER BY timestamp DESC
                        LIMIT 200
                    '''
                    cursor.execute(query)
                
                conversations = cursor.fetchall()
                
                # Simple similarity matching using keyword overlap
                similar_conversations = []
                message_words = set(message.lower().split())
                
                for conv in conversations:
                    conv_words = set(conv[0].lower().split())  # user_message words
                    
                    # Calculate simple word overlap similarity
                    intersection = message_words.intersection(conv_words)
                    union = message_words.union(conv_words)
                    
                    if len(union) > 0:
                        similarity = len(intersection) / len(union)
                        
                        if similarity >= similarity_threshold:
                            similar_conversations.append({
                                'user_message': conv[0],
                                'bot_response': conv[1],
                                'timestamp': conv[2],
                                'similarity_score': similarity,
                                'nlp_analysis': json.loads(conv[3]) if conv[3] else {}
                            })
                
                # Sort by similarity score and return top results
                similar_conversations.sort(key=lambda x: x['similarity_score'], reverse=True)
                return similar_conversations[:limit]
                
        except Exception as e:
            self.logger.error(f"Error finding similar conversations: {e}")
            return []
    
    def get_user_conversation_stats(self, user_id: str) -> Dict:
        """Get conversation statistics for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get basic stats
                cursor.execute('''
                    SELECT COUNT(*) as total_messages,
                           COUNT(DISTINCT session_id) as total_sessions,
                           MIN(timestamp) as first_conversation,
                           MAX(timestamp) as last_conversation
                    FROM conversations
                    WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    stats = {
                        'total_messages': row[0],
                        'total_sessions': row[1],
                        'first_conversation': row[2],
                        'last_conversation': row[3]
                    }
                    
                    # Get average session length
                    cursor.execute('''
                        SELECT AVG(duration_seconds) as avg_duration,
                               AVG(message_count) as avg_messages_per_session
                        FROM session_summaries
                        WHERE user_id = ?
                    ''', (user_id,))
                    
                    duration_row = cursor.fetchone()
                    if duration_row:
                        stats['avg_session_duration'] = duration_row[0] or 0
                        stats['avg_messages_per_session'] = duration_row[1] or 0
                    
                    return stats
                
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting user stats: {e}")
            return {}
    
    def _update_user_profile(self, user_id: str):
        """Update user profile with latest activity."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if user profile exists
                cursor.execute('SELECT id FROM user_profiles WHERE user_id = ?', (user_id,))
                
                if cursor.fetchone():
                    # Update existing profile
                    cursor.execute('''
                        UPDATE user_profiles
                        SET last_active = ?,
                            total_conversations = (
                                SELECT COUNT(DISTINCT session_id) 
                                FROM conversations 
                                WHERE user_id = ?
                            ),
                            total_messages = (
                                SELECT COUNT(*) 
                                FROM conversations 
                                WHERE user_id = ?
                            )
                        WHERE user_id = ?
                    ''', (datetime.now(), user_id, user_id, user_id))
                else:
                    # Create new profile
                    cursor.execute('''
                        INSERT INTO user_profiles
                        (user_id, created_at, last_active, total_conversations, total_messages)
                        VALUES (?, ?, ?, 1, 1)
                    ''', (user_id, datetime.now(), datetime.now()))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error updating user profile: {e}")
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, created_at, last_active, total_conversations, 
                           total_messages, preferences, common_topics
                    FROM user_profiles
                    WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row[0],
                        'created_at': row[1],
                        'last_active': row[2],
                        'total_conversations': row[3],
                        'total_messages': row[4],
                        'preferences': json.loads(row[5]) if row[5] else {},
                        'common_topics': json.loads(row[6]) if row[6] else []
                    }
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting user profile: {e}")
            return None
    
    def cleanup_old_conversations(self, days_to_keep: int = 30):
        """Clean up old conversations to manage database size."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Delete old conversations
                cursor.execute('''
                    DELETE FROM conversations
                    WHERE timestamp < ?
                ''', (cutoff_date,))
                
                deleted_conversations = cursor.rowcount
                
                # Delete old session summaries
                cursor.execute('''
                    DELETE FROM session_summaries
                    WHERE end_time < ?
                ''', (cutoff_date,))
                
                deleted_sessions = cursor.rowcount
                
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_conversations} conversations and {deleted_sessions} sessions")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old conversations: {e}")
    
    def get_conversation_trends(self, user_id: Optional[str] = None, days: int = 30) -> Dict:
        """Get conversation trends and analytics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Base query
                base_query = '''
                    FROM conversations
                    WHERE timestamp >= ?
                '''
                params = [cutoff_date]
                
                if user_id:
                    base_query += ' AND user_id = ?'
                    params.append(user_id)
                
                # Get message count trend by day
                cursor.execute(f'''
                    SELECT DATE(timestamp) as date, COUNT(*) as message_count
                    {base_query}
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                ''', params)
                
                daily_trends = [{'date': row[0], 'messages': row[1]} for row in cursor.fetchall()]
                
                # Get most active hours
                cursor.execute(f'''
                    SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, 
                           COUNT(*) as message_count
                    {base_query}
                    GROUP BY hour
                    ORDER BY message_count DESC
                ''', params)
                
                hourly_trends = [{'hour': row[0], 'messages': row[1]} for row in cursor.fetchall()]
                
                return {
                    'daily_trends': daily_trends,
                    'hourly_trends': hourly_trends,
                    'period_days': days
                }
                
        except Exception as e:
            self.logger.error(f"Error getting conversation trends: {e}")
            return {}
    
    def search_conversations(self, query: str, user_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search conversations by text content."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Simple text search
                search_pattern = f'%{query}%'
                
                if user_id:
                    cursor.execute('''
                        SELECT session_id, user_message, bot_response, timestamp
                        FROM conversations
                        WHERE user_id = ? AND (user_message LIKE ? OR bot_response LIKE ?)
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (user_id, search_pattern, search_pattern, limit))
                else:
                    cursor.execute('''
                        SELECT session_id, user_message, bot_response, timestamp
                        FROM conversations
                        WHERE user_message LIKE ? OR bot_response LIKE ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (search_pattern, search_pattern, limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'session_id': row[0],
                        'user_message': row[1],
                        'bot_response': row[2],
                        'timestamp': row[3]
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error searching conversations: {e}")
            return []