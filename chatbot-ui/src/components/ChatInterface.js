import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, LayoutDashboard, Newspaper } from 'lucide-react';
import { useSession } from '../context/SessionContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Dashboard from './Dashboard';
import NewsBoard from './NewsBoard';
import ChartComponent from './Chart';
import { ENDPOINTS } from '../config/api';
import './ChatInterface.css';

const ChatInterface = () => {
  const { getCurrentSession, updateSessionMessages, currentSessionId, createNewSession, setSessions, sessions, isLoadingFromDB } = useSession();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [showNewsBoard, setShowNewsBoard] = useState(false);
  const messagesEndRef = useRef(null);

  const currentSession = getCurrentSession();
  const messages = currentSession?.messages || [];

  useEffect(() => {
    // Only create a new session if:
    // 1. Database loading is complete (not loading from DB)
    // 2. There's no current session selected
    // AND one of:
    //   a) There are no sessions at all, OR
    //   b) The last session has messages (need new empty session for queries)
    if (!isLoadingFromDB && !currentSessionId) {
      const lastSession = sessions.length > 0 ? sessions[0] : null;
      const lastSessionHasMessages = lastSession && (lastSession.messages?.length || 0) > 0;
      
      if (sessions.length === 0 || lastSessionHasMessages) {
        console.log('🆕 Creating new session - no sessions or last has messages');
        createNewSession();
      } else if (lastSession) {
        // Last session is empty, reuse it
        console.log('♻️ Reusing empty last session:', lastSession.id);
        // Note: createNewSession will also reuse empty session, but setting here is more direct
      }
    }
  }, [currentSessionId, createNewSession, sessions, isLoadingFromDB]);

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
    
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    // Create a placeholder bot message for streaming
    const botMessageId = (Date.now() + 1).toString();
    const botMessage = {
      id: botMessageId,
      text: '',
      sender: 'bot',
      timestamp: new Date().toISOString(),
      charts: null,
      isStreaming: true
    };

    // Add bot message placeholder to UI
    const messagesWithBot = [...messagesWithUser, botMessage];
    setSessions(prev => prev.map(session => 
      session.id === currentSessionId 
        ? { ...session, messages: messagesWithBot }
        : session
    ));

    try {
      // Get last 4 messages (2 conversation pairs) for context
      // Exclude the current user message we just added
      const historyMessages = messages.slice(-4).filter(msg => msg.text && msg.text.trim());
      
      // Use EventSource for Server-Sent Events streaming
      const streamUrl = new URL(ENDPOINTS.chatStream);
      
      // Fetch with streaming using fetch API
      const response = await fetch(ENDPOINTS.chatStream, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: currentInput,
          history: historyMessages
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let streamedText = '';
      let charts = null;

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        // Decode the chunk
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.type === 'token') {
                // Append token to streamed text
                streamedText += data.content;
                
                // Update the bot message in real-time
                setSessions(prev => prev.map(session => {
                  if (session.id === currentSessionId) {
                    return {
                      ...session,
                      messages: session.messages.map(msg => 
                        msg.id === botMessageId 
                          ? { ...msg, text: streamedText }
                          : msg
                      )
                    };
                  }
                  return session;
                }));
              } else if (data.type === 'charts') {
                // Store charts
                charts = data.charts;
              } else if (data.type === 'done') {
                // Streaming complete
                break;
              } else if (data.type === 'error') {
                throw new Error(data.error);
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError);
            }
          }
        }
      }

      // Final update with complete message and charts
      const finalBotMessage = {
        id: botMessageId,
        text: streamedText || 'Sorry, I could not process your request.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        charts: charts,
        isStreaming: false
      };

      // Save both user message and final bot message to DB
      const finalMessages = [...messagesWithUser, finalBotMessage];
      updateSessionMessages(currentSessionId, finalMessages);

    } catch (error) {
      console.error('Streaming error:', error);
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
    if (!text) return null;
    
    // Use ReactMarkdown for proper formatting
    return (
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={{
          // Customize how different markdown elements are rendered
          p: ({node, ...props}) => <p style={{margin: '0.5em 0'}} {...props} />,
          ul: ({node, ...props}) => <ul style={{marginLeft: '1.5em', marginTop: '0.5em'}} {...props} />,
          ol: ({node, ...props}) => <ol style={{marginLeft: '1.5em', marginTop: '0.5em'}} {...props} />,
          li: ({node, ...props}) => <li style={{marginBottom: '0.3em'}} {...props} />,
          strong: ({node, ...props}) => <strong style={{fontWeight: '700'}} {...props} />,
          em: ({node, ...props}) => <em style={{fontStyle: 'italic'}} {...props} />,
          code: ({node, inline, ...props}) => 
            inline 
              ? <code style={{backgroundColor: 'rgba(0, 0, 0, 0.08)', padding: '2px 6px', borderRadius: '3px', fontSize: '0.9em'}} {...props} />
              : <code style={{display: 'block', backgroundColor: 'rgba(0, 0, 0, 0.08)', padding: '1em', borderRadius: '6px', fontSize: '0.9em', overflowX: 'auto'}} {...props} />,
          h1: ({node, ...props}) => <h1 style={{fontSize: '1.5em', fontWeight: '700', marginTop: '0.5em', marginBottom: '0.5em'}} {...props} />,
          h2: ({node, ...props}) => <h2 style={{fontSize: '1.3em', fontWeight: '600', marginTop: '0.5em', marginBottom: '0.5em'}} {...props} />,
          h3: ({node, ...props}) => <h3 style={{fontSize: '1.1em', fontWeight: '600', marginTop: '0.5em', marginBottom: '0.5em'}} {...props} />,
        }}
      >
        {text}
      </ReactMarkdown>
    );
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
                <div className={`message-bubble ${message.isError ? 'error' : ''} ${message.isStreaming ? 'streaming' : ''}`}>
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
