import React, { useState } from 'react';
import { Plus, MessageSquare, Trash2, Sun, Moon, Menu, X, Mail, Loader2 } from 'lucide-react';
import { useUser } from '@clerk/clerk-react';
import { useSession } from '../context/SessionContext';
import { useTheme } from '../context/ThemeContext';
import NewsletterSubscription from './NewsletterSubscription';
import './Sidebar.css';

const Sidebar = () => {
  const { user } = useUser();
  const { sessions, currentSessionId, setCurrentSessionId, createNewSession, deleteSession, isLoadingFromDB } = useSession();
  const { theme, toggleTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(true);
  const [showNewsletter, setShowNewsletter] = useState(false);

  const handleNewChat = () => {
    createNewSession();
  };

  const handleDeleteSession = (e, sessionId) => {
    e.stopPropagation();
    if (window.confirm('Delete this chat?')) {
      deleteSession(sessionId);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  return (
    <>
      <button className="sidebar-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>
      
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <button className="new-chat-button" onClick={handleNewChat}>
            <Plus size={18} />
            <span>New Chat</span>
          </button>
        </div>

        <div className="sessions-list">
          {isLoadingFromDB ? (
            <div className="empty-sessions">
              <Loader2 size={32} className="spinner" />
              <p>Loading your chats...</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="empty-sessions">
              <MessageSquare size={32} opacity={0.3} />
              <p>No chats yet</p>
            </div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`session-item ${currentSessionId === session.id ? 'active' : ''}`}
                onClick={() => setCurrentSessionId(session.id)}
              >
                <div className="session-content">
                  <MessageSquare size={16} />
                  <div className="session-info">
                    <div className="session-title">{session.title}</div>
                    <div className="session-date">{formatDate(session.createdAt)}</div>
                  </div>
                </div>
                <button
                  className="delete-session"
                  onClick={(e) => handleDeleteSession(e, session.id)}
                  aria-label="Delete chat"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>

        <div className="sidebar-footer">
          <button className="newsletter-button" onClick={() => setShowNewsletter(true)}>
            <Mail size={18} />
            <span>Subscribe to Newsletter</span>
          </button>
          
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>
          </button>
          {user && (
            <div className="user-info">
              <div className="user-avatar-small">
                {user.imageUrl ? (
                  <img src={user.imageUrl} alt={user.fullName} />
                ) : (
                  <div className="user-initials">
                    {user.firstName?.[0]}{user.lastName?.[0]}
                  </div>
                )}
              </div>
              <div className="user-details">
                <p className="user-name">{user.fullName || user.username}</p>
                <p className="user-email">{user.primaryEmailAddress?.emailAddress}</p>
              </div>
            </div>
          )}
          <div className="sidebar-info">
            <p className="info-text">Crypto & Currency Chatbot</p>
            <p className="info-subtext">v1.0.0</p>
          </div>
        </div>
      </div>
      
      {showNewsletter && (
        <NewsletterSubscription onClose={() => setShowNewsletter(false)} />
      )}
    </>
  );
};

export default Sidebar;
