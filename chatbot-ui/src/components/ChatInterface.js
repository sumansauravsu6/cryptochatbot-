import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, LayoutDashboard, Newspaper } from 'lucide-react';
import { useSession } from '../context/SessionContext';
import axios from 'axios';
import Dashboard from './Dashboard';
import NewsBoard from './NewsBoard';
import ChartComponent from './Chart';
import { ENDPOINTS } from '../config/api';
import './ChatInterface.css';

const ChatInterface = () => {
  const { getCurrentSession, updateSessionMessages, currentSessionId, createNewSession, setSessions, sessions } = useSession();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [showNewsBoard, setShowNewsBoard] = useState(false);
  const messagesEndRef = useRef(null);

  const currentSession = getCurrentSession();
  const messages = currentSession?.messages || [];

  useEffect(() => {
    // Only create a new session if there are no sessions at all
    if (!currentSessionId && sessions.length === 0) {
      createNewSession();
    }
  }, [currentSessionId, createNewSession, sessions.length]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    // Show user message in UI immediately (optimistic update) without saving to DB yet
    const messagesWithUser = [...messages, userMessage];
    setSessions(prev => prev.map(session => 
      session.id === currentSessionId 
        ? { ...session, messages: messagesWithUser }
        : session
    ));
    
    setInput('');
    setIsLoading(true);

    try {
      // Call your Python backend using environment variable
      const response = await axios.post(ENDPOINTS.chat, {
        message: input
      });

      const botMessage = {
        id: (Date.now() + 1).toString(),
        text: response.data.response || 'Sorry, I could not process your request.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        charts: response.data.charts || null
      };

      // Now save both user message and bot message together
      updateSessionMessages(currentSessionId, [...messagesWithUser, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, there was an error connecting to the chatbot. Please make sure the Python server is running.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      // Save both user message and error message together
      updateSessionMessages(currentSessionId, [...messagesWithUser, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const formatMessageText = (text) => {
    if (!text) return text;
    
    // Split by lines and format each one
    const lines = text.split('\n').map((line, index) => {
      const trimmedLine = line.trim();
      
      // Check if line starts with bullet point
      if (trimmedLine.startsWith('•')) {
        return (
          <div key={index} className="bullet-point">
            <span className="bullet">•</span>
            <span className="bullet-text">{trimmedLine.substring(1).trim()}</span>
          </div>
        );
      }
      
      // Regular line (headings, etc.)
      if (trimmedLine) {
        return <div key={index} className="text-line">{trimmedLine}</div>;
      }
      
      return null;
    }).filter(Boolean);
    
    return <div className="formatted-content">{lines}</div>;
  };

  return (
    <div className="chat-interface">
      {showDashboard && <Dashboard onClose={() => setShowDashboard(false)} />}
      {showNewsBoard && <NewsBoard onClose={() => setShowNewsBoard(false)} />}
      
      <div className="chat-header">
        <div className="header-content">
          <div className="header-title">
            <h1>💰 Crypto & Currency Chatbot</h1>
            <p className="subtitle">Ask me about cryptocurrencies and exchange rates</p>
          </div>
          <div className="header-buttons">
            <button 
              className="dashboard-button"
              onClick={() => setShowNewsBoard(true)}
              title="View Crypto News"
            >
              <Newspaper size={20} />
              News
            </button>
            <button 
              className="dashboard-button"
              onClick={() => setShowDashboard(true)}
              title="View Trending Dashboard"
            >
              <LayoutDashboard size={20} />
              Dashboard
            </button>
          </div>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-icon">🤖</div>
            <h2>Welcome to Crypto Chatbot!</h2>
            <p>I can help you with:</p>
            <div className="feature-cards">
              <div className="feature-card">
                <span className="feature-icon">📊</span>
                <h3>Cryptocurrency Prices</h3>
                <p>Get real-time prices for Bitcoin, Ethereum, XRP, and more</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">💱</span>
                <h3>Exchange Rates</h3>
                <p>Check currency exchange rates and conversions</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">📈</span>
                <h3>Market Trends</h3>
                <p>View historical data and market comparisons</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">📉</span>
                <h3>Visual Charts</h3>
                <p>Get beautiful graphs for time series data</p>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message ${message.sender}`}>
              <div className="message-avatar">
                {message.sender === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className={`message-bubble ${message.isError ? 'error' : ''}`}>
                  {message.sender === 'bot' ? formatMessageText(message.text) : message.text}
                </div>
                {message.charts && message.charts.length > 0 && (
                  <div className={`charts-container ${message.charts.length > 1 ? 'charts-grid' : ''}`}>
                    {message.charts.map((chartData, index) => (
                      <ChartComponent key={index} chartData={chartData} />
                    ))}
                  </div>
                )}
                <span className="message-time">{formatTime(message.timestamp)}</span>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message bot">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="message-bubble loading">
                <Loader2 className="spinner" size={16} />
                <span>Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about crypto prices, exchange rates..."
            className="message-input"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={!input.trim() || isLoading}
          >
            <Send size={20} />
          </button>
        </form>
        <p className="input-hint">
          Try: "Compare Bitcoin and Ethereum" or "USD to EUR exchange rate for last 7 days"
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;
