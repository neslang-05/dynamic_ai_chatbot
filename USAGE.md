# Dynamic AI Chatbot - Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/neslang-05/dynamic_ai_chatbot.git
cd dynamic_ai_chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi pydantic pydantic-settings uvicorn loguru vaderSentiment
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration (optional)
nano .env
```

### 3. Start the Server

```bash
# Start the chatbot server
python -m src.main

# The server will be available at:
# http://localhost:8000
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/health` | Health check |
| POST   | `/chat`   | Send message to chatbot |
| GET    | `/docs`   | Swagger API documentation |

### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/session/{session_id}` | Get session info |
| DELETE | `/session/{session_id}` | Delete session |

### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/webhook/slack` | Slack webhook integration |
| POST   | `/webhook/telegram` | Telegram webhook integration |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/analytics/stats` | Get conversation analytics |

## Usage Examples

### Basic Chat API

```bash
# Send a message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "user_id": "user123",
    "platform": "api"
  }'

# Response:
{
  "response": "Hello! How can I help you today?",
  "session_id": "abc123-def456-ghi789",
  "intent": {
    "intent": "greeting",
    "confidence": 0.9
  },
  "sentiment": {
    "sentiment": "positive",
    "confidence": 0.8,
    "emotion": "joy"
  },
  "entities": [],
  "confidence": 0.85,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### FAQ Queries

```bash
# Ask about capabilities
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What can you do?",
    "user_id": "user123"
  }'

# The bot will respond with its capabilities
```

### Entity Recognition

```bash
# Message with entities
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My email is john@example.com and phone is 123-456-7890",
    "user_id": "user123"
  }'

# Response includes extracted entities:
{
  "entities": [
    {
      "type": "email",
      "value": "john@example.com",
      "confidence": 0.9,
      "start": 12,
      "end": 28
    },
    {
      "type": "phone",
      "value": "123-456-7890",
      "confidence": 0.9,
      "start": 42,
      "end": 54
    }
  ]
}
```

## Web Demo

Open `demo.html` in your browser to try the interactive web interface.

## Platform Integrations

### Slack Integration

1. Create a Slack app at https://api.slack.com/apps
2. Configure webhook URL: `http://your-server:8000/webhook/slack`
3. Set environment variables:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_SIGNING_SECRET=your-secret
   ```

### Telegram Integration

1. Create a bot via @BotFather on Telegram
2. Configure webhook URL: `http://your-server:8000/webhook/telegram`
3. Set environment variable:
   ```
   TELEGRAM_BOT_TOKEN=your-bot-token
   ```

## Features

### NLP Capabilities
- ✅ Intent Recognition (greeting, question, request, complaint, etc.)
- ✅ Sentiment Analysis (positive, negative, neutral)
- ✅ Emotion Detection (joy, anger, sadness, fear, surprise, love)
- ✅ Named Entity Recognition (email, phone, URL, date, time, money)

### Response Generation
- ✅ Rule-based responses for common intents
- ✅ FAQ matching with keyword detection
- ✅ Sentiment-based response personalization
- ✅ Fallback mechanisms for unknown inputs

### Session Management
- ✅ Conversation context tracking
- ✅ Session timeout and cleanup
- ✅ Multi-platform session support
- ✅ In-memory and Redis storage options

### Analytics
- ✅ Real-time conversation metrics
- ✅ Intent and sentiment distribution
- ✅ Platform usage statistics
- ✅ User interaction tracking

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Services:
# - Chatbot API: http://localhost:8000
# - Redis: localhost:6379
# - MongoDB: localhost:27017
```

## Development

### Testing

```bash
# Run basic functionality tests
python test_basic.py

# Run pytest (if installed)
pytest tests/
```

### Code Quality

```bash
# Format code (if black installed)
black src/ tests/

# Lint code (if flake8 installed)
flake8 src/ tests/
```

## Production Considerations

### Performance
- Use Redis for session storage in production
- Consider load balancing for multiple instances
- Implement response caching for common queries

### Security
- Configure CORS appropriately for your domain
- Use HTTPS in production
- Validate and sanitize all input data
- Implement rate limiting

### Monitoring
- Set up proper logging levels
- Monitor API response times
- Track error rates and patterns
- Implement health checks

### Scaling
- Use container orchestration (Kubernetes)
- Implement horizontal pod autoscaling
- Consider microservices architecture for larger deployments

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if port 8000 is available
   - Verify all dependencies are installed
   - Check logs for specific errors

2. **API returns 500 errors**
   - Check server logs for stack traces
   - Verify configuration settings
   - Ensure all required services are running

3. **Poor NLP accuracy**
   - The simplified version uses rule-based approaches
   - For production, consider upgrading to transformer models
   - Train on domain-specific data for better results

4. **Webhook integrations not working**
   - Verify webhook URLs are accessible
   - Check platform-specific tokens and secrets
   - Review webhook payload formats

### Getting Help

- Check the logs in `logs/chatbot.log`
- Review the API documentation at `/docs`
- Examine the test files for usage examples
- Check GitHub issues for common problems

## Next Steps

For production deployment, consider:

1. **Advanced NLP Models**: Upgrade to transformer-based models
2. **Reinforcement Learning**: Implement feedback-based learning
3. **Multilingual Support**: Add translation capabilities
4. **Advanced Analytics**: Implement comprehensive dashboards
5. **Voice Integration**: Add speech-to-text/text-to-speech
6. **Custom Integrations**: Build connectors for other platforms