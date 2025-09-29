"""
Simplified intent recognition for basic demo (no heavy ML dependencies).
"""
import re
from typing import Dict, List
from models import Intent, IntentType
from utils.logger import setup_logger

logger = setup_logger(__name__)


class IntentRecognizer:
    """Rule-based intent recognition system for demo."""
    
    def __init__(self):
        self.rules = self._load_intent_rules()
        logger.info("Simplified IntentRecognizer initialized")
    
    def _load_intent_rules(self) -> Dict[IntentType, List[str]]:
        """Load rule-based intent patterns."""
        return {
            IntentType.GREETING: [
                r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
                r'\b(greetings|salutations)\b'
            ],
            IntentType.GOODBYE: [
                r'\b(bye|goodbye|see you|farewell|take care)\b',
                r'\b(talk to you later|ttyl|catch you later)\b'
            ],
            IntentType.QUESTION: [
                r'\b(what|when|where|why|how|who|which|can you tell me)\b',
                r'\?',
                r'\b(do you know|could you explain|help me understand)\b'
            ],
            IntentType.REQUEST: [
                r'\b(please|could you|would you|can you)\b',
                r'\b(i need|i want|i would like)\b'
            ],
            IntentType.HELP: [
                r'\b(help|assist|support)\b',
                r'\b(i don\'t understand|confused|lost)\b'
            ],
            IntentType.COMPLAINT: [
                r'\b(problem|issue|wrong|error|broken|not working)\b',
                r'\b(frustrated|annoyed|angry)\b'
            ],
            IntentType.COMPLIMENT: [
                r'\b(thank|thanks|great|awesome|excellent|good job)\b',
                r'\b(appreciate|grateful|helpful)\b'
            ]
        }
    
    async def recognize_intent(self, text: str) -> Intent:
        """Recognize intent from text using rule-based approach."""
        try:
            return self._rule_based_intent(text)
        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            return IntentType.UNKNOWN
    
    def _rule_based_intent(self, text: str) -> Intent:
        """Rule-based intent recognition."""
        text_lower = text.lower()
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        
        for intent_type, patterns in self.rules.items():
            confidence = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matches += 1
                    confidence += 0.3
            
            # Normalize confidence based on number of patterns
            if matches > 0:
                confidence = min(confidence, 1.0)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent_type
        
        return best_intent