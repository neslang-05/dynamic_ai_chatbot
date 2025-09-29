"""
Hybrid response generation system combining rule-based and AI models.
"""
import random
from typing import List, Dict, Any, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

from models import Message, ConversationTurn, IntentType, SentimentType, EmotionType
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ResponseGenerator:
    """Hybrid response generation system."""
    
    def __init__(self):
        self.rule_based_responses = self._load_rule_based_responses()
        self.faq_responses = self._load_faq_responses()
        self.generative_model = None
        self._initialize_generative_model()
    
    def _initialize_generative_model(self):
        """Initialize the generative AI model."""
        try:
            logger.info("Loading generative model...")
            
            # Use a lightweight conversational model
            self.generative_model = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                tokenizer="microsoft/DialoGPT-medium",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("Generative model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load generative model: {e}")
            logger.info("Continuing with rule-based responses only")
    
    def _load_rule_based_responses(self) -> Dict[IntentType, List[str]]:
        """Load rule-based response templates."""
        return {
            IntentType.GREETING: [
                "Hello! How can I help you today?",
                "Hi there! What can I assist you with?",
                "Greetings! How may I be of service?",
                "Hello! I'm here to help. What do you need?"
            ],
            IntentType.GOODBYE: [
                "Goodbye! Have a great day!",
                "Take care! Feel free to come back anytime.",
                "Farewell! It was nice chatting with you.",
                "See you later! Have a wonderful day!"
            ],
            IntentType.HELP: [
                "I'm here to help! You can ask me questions, request information, or just have a conversation.",
                "I can assist you with various topics. What specific help do you need?",
                "I'm designed to be helpful. Please tell me what you'd like assistance with.",
                "I'm at your service! What can I help you with today?"
            ],
            IntentType.COMPLIMENT: [
                "Thank you so much! I appreciate your kind words.",
                "That's very nice of you to say! Thank you!",
                "I'm glad I could help! Your feedback means a lot.",
                "Thank you! I'm always trying to do my best to assist you."
            ],
            IntentType.COMPLAINT: [
                "I'm sorry you're experiencing difficulties. Let me try to help resolve this.",
                "I understand your frustration. How can I make this better for you?",
                "I apologize for any inconvenience. Let's work together to find a solution.",
                "I'm sorry this isn't working as expected. Let me see what I can do to help."
            ],
            IntentType.UNKNOWN: [
                "I'm not sure I understand. Could you please rephrase your question?",
                "Could you provide more details about what you're looking for?",
                "I didn't quite catch that. Can you tell me more about what you need?",
                "I'm having trouble understanding. Could you explain that differently?"
            ]
        }
    
    def _load_faq_responses(self) -> Dict[str, str]:
        """Load FAQ responses."""
        return {
            "what can you do": "I can help answer questions, have conversations, provide information, and assist with various tasks. I use advanced AI to understand your needs and provide helpful responses.",
            "how do you work": "I use natural language processing and machine learning to understand your messages and generate appropriate responses. I combine rule-based logic with AI models for the best results.",
            "what is your purpose": "I'm designed to be a helpful AI assistant that can engage in conversations, answer questions, and provide support across various topics.",
            "who created you": "I was created using advanced AI technologies to serve as a dynamic, intelligent chatbot assistant.",
            "what are your capabilities": "I can understand intent, analyze sentiment, recognize entities, generate contextual responses, and learn from conversations to improve over time."
        }
    
    async def generate_response(self, message: Message, context: List[ConversationTurn]) -> str:
        """Generate response using hybrid approach."""
        try:
            # First check for FAQ match
            faq_response = self._check_faq(message.text)
            if faq_response:
                return self._personalize_response(faq_response, message)
            
            # Then try rule-based response
            rule_response = self._generate_rule_based_response(message)
            
            # If intent is unknown or confidence is low, try generative model
            if (message.intent.intent == IntentType.UNKNOWN or 
                message.intent.confidence < 0.6 or 
                message.intent.intent == IntentType.QUESTION):
                
                if self.generative_model:
                    generative_response = await self._generate_with_ai(message, context)
                    if generative_response and len(generative_response.strip()) > 0:
                        return self._personalize_response(generative_response, message)
            
            # Fall back to rule-based response
            return self._personalize_response(rule_response, message)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def _check_faq(self, text: str) -> Optional[str]:
        """Check if the text matches any FAQ."""
        text_lower = text.lower()
        
        for question, answer in self.faq_responses.items():
            # Simple keyword matching for FAQ
            keywords = question.lower().split()
            if all(keyword in text_lower for keyword in keywords):
                return answer
        
        return None
    
    def _generate_rule_based_response(self, message: Message) -> str:
        """Generate rule-based response based on intent."""
        intent = message.intent.intent
        responses = self.rule_based_responses.get(intent, self.rule_based_responses[IntentType.UNKNOWN])
        return random.choice(responses)
    
    async def _generate_with_ai(self, message: Message, context: List[ConversationTurn]) -> Optional[str]:
        """Generate response using AI model."""
        try:
            # Build conversation context
            conversation_text = ""
            for turn in context[-3:]:  # Last 3 turns for context
                conversation_text += f"Human: {turn.message.text}\nBot: {turn.response.text}\n"
            
            conversation_text += f"Human: {message.text}\nBot:"
            
            # Generate response
            outputs = self.generative_model(
                conversation_text,
                max_length=len(conversation_text) + 100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.generative_model.tokenizer.eos_token_id
            )
            
            if outputs and len(outputs) > 0:
                generated_text = outputs[0]['generated_text']
                # Extract the bot response
                bot_response = generated_text[len(conversation_text):].strip()
                # Clean up the response
                bot_response = bot_response.split('\n')[0].strip()
                
                if len(bot_response) > 10:  # Ensure meaningful response
                    return bot_response
            
        except Exception as e:
            logger.error(f"Error in AI generation: {e}")
        
        return None
    
    def _personalize_response(self, response: str, message: Message) -> str:
        """Personalize response based on sentiment and emotion."""
        try:
            if not message.sentiment:
                return response
            
            sentiment = message.sentiment.sentiment
            emotion = message.sentiment.emotion
            
            # Adjust tone based on sentiment
            if sentiment == SentimentType.NEGATIVE:
                if emotion == EmotionType.ANGER:
                    response = f"I understand you're feeling frustrated. {response}"
                elif emotion == EmotionType.SADNESS:
                    response = f"I'm sorry you're feeling down. {response}"
                else:
                    response = f"I sense you might be having a difficult time. {response}"
            
            elif sentiment == SentimentType.POSITIVE:
                if emotion == EmotionType.JOY:
                    response = f"I'm glad you're in good spirits! {response}"
                elif emotion == EmotionType.LOVE:
                    response = f"It's wonderful to sense such positive energy! {response}"
                else:
                    response = f"I'm happy to help! {response}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error personalizing response: {e}")
            return response