# Dynamic AI Chatbot

An intelligent, multi-platform AI chatbot with self-learning capabilities and robust NLP for dynamic, contextual conversations.

## Features

🤖 **Intelligent Conversation Engine**
- Context-aware responses with conversation memory
- Multi-turn conversation support with session management
- Intelligent response generation using transformer models

🧠 **Advanced NLP Processing**
- Sentiment analysis and emotion detection
- Named entity recognition and topic extraction
- Intent classification and question detection
- Text complexity analysis

📚 **Self-Learning System**
- User preference learning and personalization
- Response effectiveness tracking
- Conversation pattern recognition
- Continuous improvement through interaction

💾 **Robust Memory Management**
- Persistent conversation history
- User profile management
- Similar conversation matching
- Analytics and trend analysis

🌐 **Multi-Platform Support**
- Command-line interface (CLI)
- Web interface with real-time chat
- REST API for integration
- Configurable deployment options

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/neslang-05/dynamic_ai_chatbot.git
cd dynamic_ai_chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package:
```bash
pip install -e .
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your preferences:
```bash
CHATBOT_NAME=DynamicAI
MODEL_NAME=microsoft/DialoGPT-medium
MAX_HISTORY_LENGTH=10
CONFIDENCE_THRESHOLD=0.7
API_PORT=8000
WEB_PORT=5000
```

### Usage

#### Command Line Interface

Start an interactive chat session:
```bash
python -m chatbot.cli
```

Process a single message:
```bash
python -m chatbot.cli -m "Hello, how are you?"
```

#### Web Interface

Start the web server:
```bash
python -m chatbot.server
```

Then open http://localhost:8000 in your browser.

#### API Server

Start the API server:
```bash
uvicorn chatbot.server:app --host 0.0.0.0 --port 8000
```

API endpoints:
- `POST /api/chat` - Send a message
- `GET /api/conversation/history/{user_id}` - Get conversation history
- `GET /api/learning/insights` - Get learning analytics
- `GET /health` - Health check

## Architecture

### Core Components

1. **ChatbotEngine** - Main orchestration engine
2. **NLPProcessor** - Natural language processing
3. **ConversationMemory** - Persistent storage and retrieval
4. **LearningSystem** - Self-improvement and personalization

### Data Flow

```
User Input → NLP Analysis → Context Processing → Response Generation → Learning Update → Response Output
```

### Technology Stack

- **Python 3.8+** - Core language
- **Transformers** - NLP models (DialoGPT, BERT)
- **NLTK** - Text processing utilities
- **SQLite** - Conversation storage
- **FastAPI** - Web API framework
- **PyTorch** - ML model execution

## Configuration Options

### Model Settings
- `MODEL_NAME` - Transformer model to use
- `MAX_RESPONSE_LENGTH` - Maximum response length
- `TEMPERATURE` - Response generation creativity
- `USE_GPU` - Enable GPU acceleration

### Learning Settings
- `LEARNING_RATE` - How fast the bot learns
- `CONFIDENCE_THRESHOLD` - Minimum confidence for responses
- `ENABLE_LEARNING` - Enable/disable learning features

### Memory Settings
- `MAX_HISTORY_LENGTH` - Conversation context length
- `CLEANUP_DAYS` - Days to keep conversation history
- `DATABASE_URL` - Database connection string

## Development

### Running Tests

Run the complete test suite:
```bash
python -m pytest tests/ -v
```

Run specific test categories:
```bash
python tests/test_chatbot.py TestNLPProcessor
```

### Code Structure

```
chatbot/
├── core/           # Main engine and orchestration
├── nlp/            # Natural language processing
├── memory/         # Storage and learning systems
├── interfaces/     # CLI, web, and API interfaces
├── utils/          # Configuration and helpers
└── tests/          # Test suite
```

### Adding New Features

1. **New NLP Features**: Extend `NLPProcessor` class
2. **New Learning Patterns**: Extend `LearningSystem` class
3. **New Interfaces**: Create new modules in `interfaces/`
4. **New Storage**: Extend `ConversationMemory` class

## Deployment

### Docker Deployment

Build and run with Docker:
```bash
docker build -t dynamic-ai-chatbot .
docker run -p 8000:8000 dynamic-ai-chatbot
```

### Production Deployment

1. Set up environment variables
2. Configure database (PostgreSQL recommended for production)
3. Set up reverse proxy (nginx)
4. Enable logging and monitoring
5. Scale with multiple workers

### Environment Variables

```bash
# Production settings
CHATBOT_NAME=ProductionBot
DATABASE_URL=postgresql://user:pass@localhost/chatbot
API_KEY=your-secure-api-key
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO

# Feature flags
ENABLE_LEARNING=True
ENABLE_SENTIMENT_ANALYSIS=True
ENABLE_EMOTION_DETECTION=True
```

## API Documentation

### Chat Endpoint

```http
POST /api/chat
Content-Type: application/json

{
    "message": "Hello, how are you?",
    "user_id": "user123",
    "session_id": "optional_session_id"
}
```

Response:
```json
{
    "success": true,
    "data": {
        "response": "Hello! I'm doing well, thank you for asking.",
        "confidence": 0.85,
        "session_id": "user123_20231201_143022_abc123",
        "timestamp": "2023-12-01T14:30:22",
        "context_used": 5,
        "similar_found": 2
    }
}
```

### Analytics Endpoint

```http
GET /api/learning/insights?user_id=user123&days=30
```

Response:
```json
{
    "success": true,
    "data": {
        "top_topics": [
            {"topic": "ai", "score": 0.9, "frequency": 15},
            {"topic": "programming", "score": 0.8, "frequency": 12}
        ],
        "effective_patterns": [...],
        "quality_metrics": {...}
    }
}
```

## Performance and Scalability

### Performance Optimizations
- Model caching and batching
- Database query optimization
- Response caching for similar queries
- Asynchronous processing

### Scalability Options
- Horizontal scaling with multiple instances
- Database sharding by user_id
- Redis for session management
- Load balancing for API endpoints

## Monitoring and Analytics

### Built-in Analytics
- Conversation quality metrics
- User engagement tracking
- Response effectiveness analysis
- Learning progress monitoring

### Logging
- Structured logging with timestamps
- Performance metrics
- Error tracking and alerting
- User interaction patterns

## Security Considerations

- Input validation and sanitization
- Rate limiting and abuse prevention
- API key authentication
- Data privacy compliance
- Secure database connections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions
- Maintain test coverage above 80%

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review existing issues and discussions

## Roadmap

### Upcoming Features
- [ ] Voice input/output support
- [ ] Multi-language support
- [ ] Plugin system for extensions
- [ ] Advanced analytics dashboard
- [ ] Integration with external APIs
- [ ] Mobile app interface
- [ ] Webhook support for integrations
- [ ] Advanced learning algorithms

### Version History
- **v1.0.0** - Initial release with core features
- **v1.1.0** - Planned: Voice support and plugins
- **v1.2.0** - Planned: Multi-language support

---

Built with ❤️ by the Dynamic AI Team