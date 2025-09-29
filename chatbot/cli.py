"""
Command-line interface for the dynamic AI chatbot.
"""
import argparse
import sys
import os
from datetime import datetime
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.core.engine import ChatbotEngine
from chatbot.utils.config import Config
from chatbot.utils.helpers import (
    validate_user_input, format_timestamp, create_success_response,
    create_error_response, PerformanceTimer
)


class ChatbotCLI:
    """Command-line interface for the chatbot."""
    
    def __init__(self, config_file: str = None):
        self.config = Config(config_file)
        if not self.config.validate_config():
            print("❌ Configuration validation failed. Please check your settings.")
            sys.exit(1)
        
        self.engine = ChatbotEngine(self.config)
        self.logger = logging.getLogger(__name__)
        
        print(f"🤖 {self.config.CHATBOT_NAME} initialized successfully!")
        print("Type 'help' for available commands or 'quit' to exit.\n")
    
    def start_interactive_session(self, user_id: str = "cli_user"):
        """Start an interactive chat session."""
        session_id = self.engine.start_conversation(user_id)
        
        print(f"🎯 Started new conversation session: {session_id}")
        print(f"👋 Hello! I'm {self.config.CHATBOT_NAME}, your intelligent AI assistant.")
        print("How can I help you today?\n")
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input("You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        self._handle_quit()
                        break
                    elif user_input.lower() == 'help':
                        self._show_help()
                        continue
                    elif user_input.lower() == 'stats':
                        self._show_stats()
                        continue
                    elif user_input.lower() == 'history':
                        self._show_history(user_id)
                        continue
                    elif user_input.lower() == 'clear':
                        self._clear_screen()
                        continue
                    
                    # Validate input
                    validation = validate_user_input(user_input)
                    if not validation['valid']:
                        print(f"❌ Input validation failed: {'; '.join(validation['errors'])})")
                        continue
                    
                    if validation['warnings']:
                        print(f"⚠️  Warning: {'; '.join(validation['warnings'])}")
                    
                    # Process message with performance timing
                    with PerformanceTimer("Message processing", self.logger):
                        response_data = self.engine.process_message(
                            validation['cleaned_text'], user_id
                        )
                    
                    # Display response
                    self._display_response(response_data)
                
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    self._handle_quit()
                    break
                except Exception as e:
                    self.logger.error(f"Error in interactive session: {e}")
                    print(f"❌ An error occurred: {e}")
                    print("Please try again or type 'quit' to exit.")
        
        finally:
            self.engine.end_conversation()
    
    def _display_response(self, response_data: dict):
        """Display chatbot response with formatting."""
        response = response_data.get('response', 'I apologize, but I couldn\'t generate a response.')
        confidence = response_data.get('confidence', 0.0)
        
        # Format confidence indicator
        if confidence >= 0.8:
            confidence_indicator = "🟢"
        elif confidence >= 0.6:
            confidence_indicator = "🟡"
        else:
            confidence_indicator = "🔴"
        
        print(f"\n{self.config.CHATBOT_NAME}: {response}")
        
        # Show additional info in verbose mode
        if hasattr(self, 'verbose') and self.verbose:
            print(f"\n📊 Confidence: {confidence:.3f} {confidence_indicator}")
            print(f"🔗 Context used: {response_data.get('context_used', 0)} keywords")
            print(f"📚 Similar conversations found: {response_data.get('similar_found', 0)}")
        
        print()  # Empty line for spacing
    
    def _show_help(self):
        """Display help information."""
        help_text = f"""
🤖 {self.config.CHATBOT_NAME} - Interactive Help

Available Commands:
  help     - Show this help message
  stats    - Display conversation statistics
  history  - Show recent conversation history
  clear    - Clear the screen
  quit     - Exit the chatbot

Features:
  ✨ Intelligent conversation with context awareness
  🧠 Self-learning from interactions
  🎯 Emotion and sentiment analysis
  📚 Conversation memory and history
  🔍 Entity recognition and topic tracking

Tips:
  • Ask questions naturally
  • Be specific for better responses
  • The bot learns from your conversations
  • Longer conversations build better context

Example conversations:
  "How are you today?"
  "Can you help me understand machine learning?"
  "What's the weather like?" (Note: I don't have real-time data)
  "Tell me a joke"
"""
        print(help_text)
    
    def _show_stats(self):
        """Display conversation statistics."""
        try:
            stats = self.engine.get_conversation_stats()
            
            if 'error' in stats:
                print(f"❌ {stats['error']}")
                return
            
            print("\n📊 Conversation Statistics:")
            print(f"   Session ID: {stats.get('session_id', 'N/A')}")
            print(f"   Messages: {stats.get('message_count', 0)}")
            print(f"   Context Keywords: {stats.get('context_keywords', 0)}")
            print(f"   Duration: {stats.get('duration_minutes', 0):.1f} minutes")
            print()
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
    
    def _show_history(self, user_id: str):
        """Display recent conversation history."""
        try:
            history = self.engine.conversation_memory.get_recent_conversations(user_id, limit=5)
            
            if not history:
                print("📚 No conversation history available.")
                return
            
            print("\n📚 Recent Conversation History:")
            print("=" * 50)
            
            for i, conv in enumerate(history, 1):
                timestamp = conv.get('timestamp', 'Unknown time')
                user_msg = conv.get('user_message', '')
                bot_msg = conv.get('bot_response', '')
                
                # Truncate long messages
                if len(user_msg) > 60:
                    user_msg = user_msg[:60] + "..."
                if len(bot_msg) > 60:
                    bot_msg = bot_msg[:60] + "..."
                
                print(f"{i}. [{timestamp}]")
                print(f"   You: {user_msg}")
                print(f"   Bot: {bot_msg}")
                print()
            
        except Exception as e:
            print(f"❌ Error getting history: {e}")
    
    def _clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"🤖 {self.config.CHATBOT_NAME} - Chat cleared")
        print("How can I help you today?\n")
    
    def _handle_quit(self):
        """Handle quit command."""
        print(f"\n👋 Thank you for chatting with {self.config.CHATBOT_NAME}!")
        
        # Show final stats
        try:
            stats = self.engine.get_conversation_stats()
            if 'error' not in stats:
                print(f"📊 Session Summary:")
                print(f"   Messages exchanged: {stats.get('message_count', 0)}")
                print(f"   Duration: {stats.get('duration_minutes', 0):.1f} minutes")
        except:
            pass
        
        print("Come back anytime! 🚀")
    
    def process_single_message(self, message: str, user_id: str = "cli_user") -> dict:
        """Process a single message and return response (for batch processing)."""
        try:
            # Start conversation if needed
            if not self.engine.current_session_id:
                self.engine.start_conversation(user_id)
            
            # Validate input
            validation = validate_user_input(message)
            if not validation['valid']:
                return create_error_response("validation_error", 
                                           '; '.join(validation['errors']))
            
            # Process message
            response_data = self.engine.process_message(validation['cleaned_text'], user_id)
            return create_success_response(response_data)
            
        except Exception as e:
            self.logger.error(f"Error processing single message: {e}")
            return create_error_response("processing_error", str(e))
        
        finally:
            self.engine.end_conversation()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Dynamic AI Chatbot - Intelligent conversational AI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--user-id', '-u',
        type=str,
        default='cli_user',
        help='User ID for the session (default: cli_user)'
    )
    
    parser.add_argument(
        '--message', '-m',
        type=str,
        help='Process a single message and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Dynamic AI Chatbot 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize CLI
        cli = ChatbotCLI(args.config)
        cli.verbose = args.verbose
        
        if args.message:
            # Process single message
            result = cli.process_single_message(args.message, args.user_id)
            
            if result.get('success'):
                response_data = result['data']
                print(f"Response: {response_data.get('response', 'No response')}")
                
                if args.verbose:
                    print(f"Confidence: {response_data.get('confidence', 0):.3f}")
                    print(f"Session ID: {response_data.get('session_id', 'N/A')}")
            else:
                print(f"Error: {result.get('message', 'Unknown error')}")
                sys.exit(1)
        else:
            # Start interactive session
            cli.start_interactive_session(args.user_id)
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()