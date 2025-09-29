# Dynamic AI Chatbot

A modular, API-driven chatbot with advanced NLP capabilities, multi-platform integration, and self-learning features.

## Features

- **NLP-Based Conversational Understanding**: BERT-based intent recognition and named entity extraction
- **Contextual Memory**: Redis-backed session management with conversation history
- **Multi-Platform Integration**: API-first architecture with platform connectors for Slack, Telegram, web, and mobile
- **AI-Powered Response Generation**: Hybrid model combining rule-based and GPT-based responses
- **Sentiment Analysis & Emotion Detection**: Dynamic tone adjustment based on user sentiment
- **Self-Learning & Adaptive AI**: Reinforcement learning for continuous improvement
- **Smart Analytics Dashboard**: Real-time conversation analytics and insights

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Connectors    │    │   Core API      │    │   AI Models     │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Slack     │ │────┤ │   FastAPI   │ │────┤ │    BERT     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │  Telegram   │ │    │ │   Session   │ │    │ │     GPT     │ │
│ └─────────────┘ │    │ │  Manager    │ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ └─────────────┘ │    │ ┌─────────────┐ │
│ │   Web SDK   │ │    │                 │    │ │   VADER     │ │
│ └─────────────┘ │    │                 │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Data Layer    │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │    Redis    │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │   MongoDB   │ │
                    │ └─────────────┘ │
                    └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.9+
- Redis server
- MongoDB server

### Installation

1. Clone the repository:
```bash
git clone https://github.com/neslang-05/dynamic_ai_chatbot.git
cd dynamic_ai_chatbot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start the services:
```bash
# Start Redis (in another terminal)
redis-server

# Start MongoDB (in another terminal)
mongod

# Start the chatbot API
python -m src.main
```

## API Endpoints

- `POST /chat` - Send a message to the chatbot
- `GET /health` - Health check endpoint
- `POST /webhook/slack` - Slack webhook integration
- `POST /webhook/telegram` - Telegram webhook integration
- `GET /analytics/stats` - Get conversation analytics

## Configuration

The chatbot can be configured through environment variables or configuration files. See `.env.example` for all available options.

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/ tests/
flake8 src/ tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests and linting
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.