# Dynamic AI Chatbot Dashboard

A professional, boxy UI dashboard for monitoring and analyzing your Dynamic AI Chatbot's performance, built with Flask backend and React frontend.

## 📊 Dashboard Features

### Key Performance Indicators (KPIs)
- **Total Users**: Track total number of unique users
- **Total Messages**: Monitor message volume
- **Average Conversation Length**: Understand user engagement
- **Response Time**: Monitor system performance
- **User Satisfaction**: Track user ratings
- **Sentiment Analysis**: Positive sentiment percentage

### Visual Analytics
- **Conversation Trends**: Line chart showing messages and conversations over time
- **Sentiment Distribution**: Donut chart of positive/negative/neutral sentiments
- **Intent Distribution**: Bar chart of most common user intents
- **Platform Usage**: Pie chart showing usage across different platforms

### Real-time Monitoring
- **System Health**: Live status indicators for services
- **Active Sessions**: Current active user sessions
- **Messages per Minute**: Real-time throughput
- **Uptime Tracking**: System availability metrics

## 🏗️ Architecture

```
dashboard/
├── backend/           # Flask API server
│   ├── app.py        # Main Flask application
│   └── requirements.txt
└── frontend/         # React application
    ├── src/
    │   ├── components/
    │   │   ├── MetricCard.js    # KPI display cards
    │   │   ├── ChartCard.js     # Chart components
    │   │   └── SystemHealth.js  # Health monitoring
    │   ├── App.js       # Main dashboard component
    │   ├── api.js       # API client
    │   └── index.css    # Tailwind CSS styles
    └── package.json
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Automated Setup
```bash
# Run the setup script
./setup_dashboard.sh
```

### 2. Manual Setup

#### Backend Setup
```bash
# Install Flask backend dependencies
cd dashboard/backend
pip install -r requirements.txt

# Start the dashboard backend
python app.py
```

#### Frontend Setup
```bash
# Install React frontend dependencies
cd dashboard/frontend
npm install

# Start the React development server
npm start
```

### 3. Start All Services

#### Terminal 1: Main Chatbot API
```bash
python runner.py
```

#### Terminal 2: Dashboard Backend
```bash
cd dashboard/backend
python app.py
```

#### Terminal 3: Dashboard Frontend
```bash
cd dashboard/frontend
npm start
```

## 🌐 Access Points

- **Main Chatbot API**: http://localhost:8000
- **Dashboard Backend**: http://localhost:5000
- **Dashboard Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

## 📡 API Endpoints

### Dashboard Backend Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/health` | GET | Dashboard health check |
| `/api/kpis` | GET | Key performance indicators |
| `/api/conversation-trends` | GET | Conversation trends data |
| `/api/sentiment-distribution` | GET | Sentiment analysis data |
| `/api/intent-distribution` | GET | Intent recognition data |
| `/api/platform-usage` | GET | Platform usage statistics |
| `/api/real-time-metrics` | GET | Real-time system metrics |
| `/api/chatbot-health` | GET | Main chatbot API health |

## 🎨 UI Design Features

### Boxy Card-Based Layout
- Clean, modern card-based design
- Consistent spacing and shadows
- Professional color scheme
- Responsive grid layout

### Visual Elements
- **Gradient Icons**: Color-coded metric cards
- **Interactive Charts**: Hover effects and animations
- **Status Indicators**: Real-time health monitoring
- **Loading States**: Smooth loading animations

### Color Scheme
- **Primary**: Blue tones for main actions
- **Success**: Green for positive metrics
- **Warning**: Yellow for attention items
- **Error**: Red for issues
- **Neutral**: Gray for secondary content

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the dashboard backend directory:

```bash
# Dashboard Backend Configuration
CHATBOT_API_URL=http://localhost:8000
DASHBOARD_PORT=5000

# Optional: Database connections
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017
```

### Frontend Configuration

Create a `.env` file in the dashboard frontend directory:

```bash
# Dashboard Frontend Configuration
REACT_APP_API_URL=http://localhost:5000
```

## 📊 Data Sources

The dashboard connects to your main chatbot API to fetch:
- Analytics statistics from `/analytics/stats`
- Session information
- Real-time metrics
- Health status

If the main API is unavailable, the dashboard falls back to mock data for demonstration.

## 🔄 Auto-Refresh

The dashboard automatically refreshes data every 30 seconds to provide real-time insights. You can also manually refresh using the "Refresh" button.

## 🎯 Customization

### Adding New Metrics
1. Add new endpoints to `dashboard/backend/app.py`
2. Create new components in `dashboard/frontend/src/components/`
3. Update the main `App.js` to include new metrics

### Styling Customization
- Modify `tailwind.config.js` for theme changes
- Update `index.css` for custom styles
- Adjust color schemes in component files

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure Flask-CORS is installed and configured
2. **API Connection Issues**: Check that all services are running on correct ports
3. **Missing Dependencies**: Run `npm install` and `pip install -r requirements.txt`

### Health Checks
- Visit `/api/health` to check dashboard backend
- Visit `/health` to check main chatbot API
- Check browser console for frontend errors

## 📈 Performance

The dashboard is optimized for:
- Fast loading with efficient API calls
- Responsive design for all screen sizes
- Minimal memory footprint
- Real-time updates without page refresh

## 🔒 Security Considerations

- API endpoints use CORS protection
- No sensitive data stored in frontend
- Environment variables for configuration
- Rate limiting can be added for production use

---

**Ready to monitor your AI chatbot like a pro!** 🚀