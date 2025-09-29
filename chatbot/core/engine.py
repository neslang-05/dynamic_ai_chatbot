"""
Core chatbot engine with intelligent response generation and context management.
"""
import logging
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from .nlp.processor import NLPProcessor
from .memory.conversation_memory import ConversationMemory
from .memory.learning_system import LearningSystem
from .utils.config import Config


class ChatbotEngine:
    """
    Main chatbot engine that orchestrates NLP processing, memory management,
    and response generation with self-learning capabilities.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.nlp_processor = NLPProcessor(self.config)
        self.conversation_memory = ConversationMemory(self.config)
        self.learning_system = LearningSystem(self.config)
        
        # Session management
        self.current_session_id = None
        self.conversation_context = {}
        
        self.logger.info("ChatbotEngine initialized successfully")
    
    def start_conversation(self, user_id: str = "default") -> str:
        """Start a new conversation session."""
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session_id = session_id
        self.conversation_context = {
            "session_id": session_id,
            "user_id": user_id,
            "start_time": datetime.now(),
            "message_count": 0,
            "context_keywords": [],
            "user_preferences": self.learning_system.get_user_preferences(user_id)
        }
        
        # Load conversation history for context
        recent_history = self.conversation_memory.get_recent_conversations(
            user_id, limit=self.config.MAX_HISTORY_LENGTH
        )
        self.conversation_context["recent_history"] = recent_history
        
        self.logger.info(f"Started conversation session: {session_id}")
        return session_id
    
    def process_message(self, message: str, user_id: str = "default") -> Dict:
        """
        Process user message and generate intelligent response.
        
        Returns:
            Dict containing response, confidence, context info, and learning insights
        """
        if not self.current_session_id:
            self.start_conversation(user_id)
        
        # Update conversation context
        self.conversation_context["message_count"] += 1
        
        # Analyze message with NLP
        nlp_analysis = self.nlp_processor.analyze_message(message)
        
        # Update context with new insights
        self._update_context(nlp_analysis)
        
        # Generate response based on analysis and context
        response_data = self._generate_response(message, nlp_analysis)
        
        # Store conversation for learning
        self._store_conversation_turn(message, response_data["response"], nlp_analysis)
        
        # Update learning system
        self.learning_system.learn_from_interaction(
            user_id, message, response_data["response"], nlp_analysis
        )
        
        return response_data
    
    def _update_context(self, nlp_analysis: Dict):
        """Update conversation context with new NLP insights."""
        # Add key entities and topics to context
        if "entities" in nlp_analysis:
            for entity in nlp_analysis["entities"]:
                if entity not in self.conversation_context["context_keywords"]:
                    self.conversation_context["context_keywords"].append(entity)
        
        # Keep only recent keywords (last 20)
        self.conversation_context["context_keywords"] = \
            self.conversation_context["context_keywords"][-20:]
    
    def _generate_response(self, message: str, nlp_analysis: Dict) -> Dict:
        """Generate intelligent response using NLP and context."""
        # Get similar conversations from memory
        similar_conversations = self.conversation_memory.find_similar_conversations(
            message, limit=5
        )
        
        # Generate response using NLP processor with context
        response = self.nlp_processor.generate_response(
            message=message,
            context=self.conversation_context,
            similar_conversations=similar_conversations,
            nlp_analysis=nlp_analysis
        )
        
        # Calculate confidence score
        confidence = self._calculate_confidence(nlp_analysis, similar_conversations)
        
        return {
            "response": response,
            "confidence": confidence,
            "session_id": self.current_session_id,
            "context_used": len(self.conversation_context["context_keywords"]),
            "similar_found": len(similar_conversations),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_confidence(self, nlp_analysis: Dict, similar_conversations: List) -> float:
        """Calculate confidence score for the response."""
        base_confidence = nlp_analysis.get("confidence", 0.5)
        
        # Boost confidence if we have similar conversations
        similarity_boost = min(0.3, len(similar_conversations) * 0.1)
        
        # Boost confidence if we have context
        context_boost = min(0.2, len(self.conversation_context["context_keywords"]) * 0.02)
        
        final_confidence = min(1.0, base_confidence + similarity_boost + context_boost)
        return round(final_confidence, 3)
    
    def _store_conversation_turn(self, user_message: str, bot_response: str, nlp_analysis: Dict):
        """Store conversation turn in memory."""
        conversation_turn = {
            "session_id": self.current_session_id,
            "user_id": self.conversation_context["user_id"],
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.now(),
            "nlp_analysis": nlp_analysis,
            "context_keywords": self.conversation_context["context_keywords"].copy()
        }
        
        self.conversation_memory.store_conversation(conversation_turn)
    
    def end_conversation(self):
        """End current conversation session."""
        if self.current_session_id:
            # Save final conversation summary
            summary = {
                "session_id": self.current_session_id,
                "user_id": self.conversation_context["user_id"],
                "duration": (datetime.now() - self.conversation_context["start_time"]).total_seconds(),
                "message_count": self.conversation_context["message_count"],
                "final_keywords": self.conversation_context["context_keywords"]
            }
            
            self.conversation_memory.store_session_summary(summary)
            self.logger.info(f"Ended conversation session: {self.current_session_id}")
            
            self.current_session_id = None
            self.conversation_context = {}
    
    def get_conversation_stats(self) -> Dict:
        """Get statistics about current conversation."""
        if not self.current_session_id:
            return {"error": "No active conversation"}
        
        return {
            "session_id": self.current_session_id,
            "message_count": self.conversation_context["message_count"],
            "context_keywords": len(self.conversation_context["context_keywords"]),
            "duration_minutes": (datetime.now() - self.conversation_context["start_time"]).total_seconds() / 60
        }