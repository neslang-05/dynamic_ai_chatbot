import React, { useState, useEffect } from 'react';
import { 
  Users, 
  MessageSquare, 
  TrendingUp, 
  Activity,
  Star,
  Monitor,
  Shield,
  Zap,
  ExternalLink,
  RefreshCw
} from 'lucide-react';
import MetricCard from './components/MetricCard';
import ChartCard from './components/ChartCard';
import SystemHealth from './components/SystemHealth';
import apiClient from './api';

const App = () => {
  const [kpis, setKpis] = useState({});
  const [conversationTrends, setConversationTrends] = useState({});
  const [sentimentData, setSentimentData] = useState({});
  const [intentData, setIntentData] = useState({});
  const [platformData, setPlatformData] = useState({});
  const [realTimeMetrics, setRealTimeMetrics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Get the chatbot UI URL
  const getChatbotUrl = () => {
    const baseUrl = window.location.hostname === 'localhost' 
      ? 'http://localhost:8000'
      : `${window.location.protocol}//${window.location.hostname.replace('-3000', '-8000')}`;
    return `${baseUrl}/static/chatbot_secure.html`;
  };

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [
        kpiData,
        trendsData,
        sentimentDistribution,
        intentDistribution,
        platformUsage,
        realTimeData
      ] = await Promise.all([
        apiClient.get('/api/kpis'),
        apiClient.get('/api/conversation-trends'),
        apiClient.get('/api/sentiment-distribution'),
        apiClient.get('/api/intent-distribution'),
        apiClient.get('/api/platform-usage'),
        apiClient.get('/api/real-time-metrics')
      ]);

      setKpis(kpiData);
      setConversationTrends(trendsData);
      setSentimentData(sentimentDistribution);
      setIntentData(intentDistribution);
      setPlatformData(platformUsage);
      setRealTimeMetrics(realTimeData);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Chart data configurations
  const conversationTrendsChartData = {
    labels: conversationTrends.labels || [],
    datasets: [
      {
        label: 'Messages',
        data: conversationTrends.messages || [],
        borderColor: '#3B82F6',
        backgroundColor: '#3B82F6',
        tension: 0.4,
      },
      {
        label: 'Conversations',
        data: conversationTrends.conversations || [],
        borderColor: '#10B981',
        backgroundColor: '#10B981',
        tension: 0.4,
      },
    ],
  };

  const sentimentChartData = {
    labels: sentimentData.labels || [],
    datasets: [
      {
        data: sentimentData.data || [],
        backgroundColor: sentimentData.colors || ['#10B981', '#F59E0B', '#EF4444'],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  const intentChartData = {
    labels: intentData.labels || [],
    datasets: [
      {
        label: 'Intent Count',
        data: intentData.data || [],
        backgroundColor: '#3B82F6',
        borderRadius: 4,
      },
    ],
  };

  const platformChartData = {
    labels: platformData.labels || [],
    datasets: [
      {
        data: platformData.data || [],
        backgroundColor: platformData.colors || ['#8B5CF6', '#06B6D4', '#F97316', '#84CC16'],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  if (loading) {
    return (
      <div className="dashboard-container flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto"></div>
          <p className="mt-6 text-white text-lg font-medium">Loading Professional Dashboard...</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-green-600 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-2xl text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Dashboard</h2>
          <p className="text-gray-600">Fetching real-time analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-green-600 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl p-8 shadow-2xl text-center max-w-md">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center space-x-2 mx-auto"
          >
            <RefreshCw size={18} />
            <span>Retry Connection</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-green-600">
      <div className="p-6">
        {/* Header */}
        <header className="bg-white rounded-2xl shadow-xl border border-gray-200 mb-8 p-8">
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center space-y-4 lg:space-y-0">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mr-4">
                  <span className="text-white text-2xl">🤖</span>
                </div>
                AI Chatbot Analytics
              </h1>
              <p className="text-lg text-gray-600">
                Enterprise-Grade Real-time Monitoring & Intelligence
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
            </div>
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
              <a
                href={getChatbotUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg"
              >
                <ExternalLink size={18} />
                <span>Open Chatbot</span>
              </a>
              <button
                onClick={fetchDashboardData}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg"
              >
                <RefreshCw size={18} />
                <span>Refresh Data</span>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="space-y-8">
          {/* KPI Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Conversations"
              value={kpis.total_messages?.toLocaleString() || '0'}
              icon={MessageSquare}
              color="blue"
              trend="+12%"
            />
            <MetricCard
              title="Active Users"
              value={kpis.total_users?.toLocaleString() || '0'}
              icon={Users}
              color="green"
              trend="+8%"
            />
            <MetricCard
              title="Response Time"
              value={`${kpis.response_time_ms || 0}ms`}
              icon={Zap}
              color="purple"
              trend="-15ms"
            />
            <MetricCard
              title="Satisfaction"
              value={`${kpis.satisfaction_rating || 0}/5`}
              icon={Star}
              color="yellow"
              trend="+0.3"
            />
          </div>

          {/* Performance Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* System Health */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Activity className="mr-3 text-green-600" size={20} />
                  System Health
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Server Status</span>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      Online
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Uptime</span>
                    <span className="font-semibold text-green-600">99.9%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Response Accuracy</span>
                    <span className="font-semibold text-blue-600">94.2%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Real-time Metrics */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Monitor className="mr-3 text-blue-600" size={20} />
                  Live Metrics
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Active Sessions</span>
                    <span className="font-semibold text-blue-600">{realTimeMetrics.active_sessions || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Messages/Min</span>
                    <span className="font-semibold text-purple-600">{realTimeMetrics.messages_per_minute || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Queue Length</span>
                    <span className="font-semibold text-gray-600">0</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Today's Summary */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <TrendingUp className="mr-3 text-purple-600" size={20} />
                  Today's Activity
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Messages Today</span>
                    <span className="font-semibold text-blue-600">{realTimeMetrics.messages_today || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Positive Sentiment</span>
                    <span className="font-semibold text-green-600">{kpis.positive_sentiment_percentage || 0}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">New Users</span>
                    <span className="font-semibold text-purple-600">12</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Conversation Trends */}
            <ChartCard
              title="Conversation Trends (7 Days)"
              type="line"
              data={conversationTrendsChartData}
              height={300}
            />

            {/* Sentiment Distribution */}
            <ChartCard
              title="Sentiment Distribution"
              type="doughnut"
              data={sentimentChartData}
              height={300}
            />

            {/* Intent Distribution */}
            <ChartCard
              title="Intent Distribution"
              type="bar"
              data={intentChartData}
              height={300}
            />

            {/* Platform Usage */}
            <ChartCard
              title="Platform Usage"
              type="pie"
              data={platformChartData}
              height={300}
            />
          </div>

          {/* System Health Component */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <SystemHealth 
              data={{
                server_status: 'healthy',
                chatbot_status: realTimeMetrics.server_status || 'healthy',
                active_sessions: realTimeMetrics.active_sessions,
                uptime_hours: realTimeMetrics.uptime_hours
              }} 
            />
            
            {/* Additional Real-time Metrics */}
            <div className="lg:col-span-2 bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-50 to-blue-50 px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Performance Overview</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 rounded-xl p-4">
                    <div className="text-sm text-blue-600 mb-1">Messages/Min</div>
                    <div className="text-2xl font-bold text-blue-900">
                      {realTimeMetrics.messages_per_minute || 0}
                    </div>
                  </div>
                  <div className="bg-green-50 rounded-xl p-4">
                    <div className="text-sm text-green-600 mb-1">Avg Response Time</div>
                    <div className="text-2xl font-bold text-green-900">
                      {realTimeMetrics.average_response_time || 0}ms
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      
      </div>
    </div>
  );
};

export default App;