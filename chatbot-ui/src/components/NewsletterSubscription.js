import React, { useState, useEffect } from 'react';
import { Mail, Check, X, Edit } from 'lucide-react';
import { useUser } from '@clerk/clerk-react';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import './NewsletterSubscription.css';

const NewsletterSubscription = ({ onClose }) => {
  const { user } = useUser();
  const [email, setEmail] = useState(user?.primaryEmailAddress?.emailAddress || '');
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [existingTopics, setExistingTopics] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState(null); // 'success', 'error', or null
  const [isExistingSubscriber, setIsExistingSubscriber] = useState(false);
  const [isEditingTopics, setIsEditingTopics] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const cryptoTopics = [
    { id: 'bitcoin', name: 'Bitcoin', icon: '₿' },
    { id: 'ethereum', name: 'Ethereum', icon: 'Ξ' },
    { id: 'altcoins', name: 'Altcoins', icon: '🪙' },
    { id: 'defi', name: 'DeFi', icon: '🏦' },
    { id: 'trading', name: 'Trading', icon: '📈' },
    { id: 'mining', name: 'Mining', icon: '⛏️' },
    { id: 'regulation', name: 'Regulation', icon: '⚖️' },
    { id: 'market-analysis', name: 'Market Analysis', icon: '📊' }
  ];

  const nftTopics = [
    { id: 'nft-cryptopunks', name: 'CryptoPunks', icon: '🎭' },
    { id: 'nft-bored-ape', name: 'Bored Ape YC', icon: '🦍' },
    { id: 'nft-art', name: 'NFT Art', icon: '🎨' },
    { id: 'nft-gaming', name: 'NFT Gaming', icon: '🎮' },
    { id: 'nft-marketplace', name: 'Marketplaces', icon: '🏪' },
    { id: 'nft-metaverse', name: 'Metaverse', icon: '🌐' }
  ];

  // Check if user is already subscribed
  useEffect(() => {
    const checkExistingSubscription = async () => {
      if (email) {
        try {
          setIsLoading(true);
          const response = await axios.get(ENDPOINTS.newsletter.topics(email));
          
          console.log('Subscription check response:', response.data);
          
          if (response.data.success && response.data.topics && response.data.topics.length > 0) {
            setExistingTopics(response.data.topics);
            setSelectedTopics(response.data.topics); // Initialize with existing topics for editing
            setIsExistingSubscriber(true);
          } else {
            setIsExistingSubscriber(false);
            setExistingTopics([]);
          }
        } catch (error) {
          // User not found (404) or not subscribed yet - this is normal for new users
          console.log('Subscription check - user not found (this is normal for new subscribers)');
          setIsExistingSubscriber(false);
          setExistingTopics([]);
          setSelectedTopics([]);
        } finally {
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
      }
    };

    checkExistingSubscription();
  }, [email]);

  const toggleTopic = (topicId) => {
    setSelectedTopics(prev => 
      prev.includes(topicId) 
        ? prev.filter(id => id !== topicId)
        : [...prev, topicId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || selectedTopics.length === 0) {
      setStatus({ type: 'error', message: 'Please select at least one topic' });
      return;
    }

    setIsSubmitting(true);
    setStatus(null);

    try {
      let response;
      const isNewSubscription = !isExistingSubscriber;
      
      if (isExistingSubscriber && isEditingTopics) {
        // Update existing subscription - replace all topics
        response = await axios.post(ENDPOINTS.newsletter.updateTopics, {
          email,
          topics: selectedTopics,
          userName: user?.fullName || user?.username || 'User',
          mode: 'replace' // Replace all topics with the new selection
        });
      } else if (!isExistingSubscriber) {
        // New subscription
        response = await axios.post(ENDPOINTS.newsletter.subscribe, {
          email,
          topics: selectedTopics,
          userName: user?.fullName || user?.username || 'User'
        });
      }

      if (response && response.data.success) {
        console.log('Subscription successful:', response.data);
        
        setStatus({ 
          type: 'success', 
          message: isEditingTopics ? 'Topics updated successfully!' : 'Successfully subscribed to newsletter!' 
        });
        
        // Update existing topics with the new list
        if (response.data.topics) {
          setExistingTopics(response.data.topics);
          setSelectedTopics(response.data.topics);
          setIsExistingSubscriber(true);
          setIsEditingTopics(false);
        }
        
        // Don't auto-close - let users see their subscription status
        // Clear success message after 3 seconds
        setTimeout(() => {
          setStatus(null);
        }, 3000);
      }
    } catch (error) {
      console.error('Subscription error:', error.response?.data || error.message);
      setStatus({ 
        type: 'error', 
        message: error.response?.data?.error || 'Failed to update. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditTopics = () => {
    setIsEditingTopics(true);
  };

  const handleUnsubscribe = async () => {
    if (!window.confirm('Are you sure you want to unsubscribe from the newsletter?')) {
      return;
    }

    setIsSubmitting(true);
    setStatus(null);

    try {
      const response = await axios.post('http://localhost:5000/api/newsletter/unsubscribe', {
        email
      });

      if (response.data.success) {
        setStatus({ 
          type: 'success', 
          message: 'Successfully unsubscribed from newsletter!' 
        });
        
        // Reset state
        setExistingTopics([]);
        setSelectedTopics([]);
        setIsExistingSubscriber(false);
        setIsEditingTopics(false);
        
        setTimeout(() => {
          onClose();
        }, 2000);
      }
    } catch (error) {
      setStatus({ 
        type: 'error', 
        message: error.response?.data?.error || 'Failed to unsubscribe. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelEdit = () => {
    setIsEditingTopics(false);
    setSelectedTopics(existingTopics); // Reset to original topics
    setStatus(null);
  };

  const getTopicName = (topicId) => {
    const allTopics = [...cryptoTopics, ...nftTopics];
    const topic = allTopics.find(t => t.id === topicId);
    return topic ? `${topic.icon} ${topic.name}` : topicId;
  };

  if (isLoading) {
    return (
      <div className="newsletter-overlay" onClick={onClose}>
        <div className="newsletter-modal" onClick={(e) => e.stopPropagation()}>
          <div style={{ padding: '40px', textAlign: 'center' }}>
            <div className="loading-spinner">Loading...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="newsletter-overlay" onClick={onClose}>
      <div className="newsletter-modal" onClick={(e) => e.stopPropagation()}>
        <button className="newsletter-close" onClick={onClose}>
          <X size={20} />
        </button>

        <div className="newsletter-header">
          <Mail size={32} className="newsletter-icon" />
          <h2>{isExistingSubscriber && !isEditingTopics ? 'Your Newsletter Subscription' : isEditingTopics ? 'Edit Your Topics' : 'Subscribe to Newsletter'}</h2>
          <p>{isExistingSubscriber && !isEditingTopics ? 'Manage your topics' : isEditingTopics ? 'Add or remove topics from your subscription' : 'Get weekly updates on your favorite crypto and NFT topics'}</p>
        </div>

        {isExistingSubscriber && !isEditingTopics ? (
          // Show existing subscription (read-only view)
          <div className="newsletter-form">
            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                value={email}
                disabled
                style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
              />
            </div>

            <div className="topics-section">
              <h3>Your Subscribed Topics ({existingTopics.length})</h3>
              <div className="topics-grid">
                {existingTopics.map(topicId => (
                  <div
                    key={topicId}
                    className="topic-chip selected"
                    style={{ cursor: 'default' }}
                  >
                    <span className="topic-name">{getTopicName(topicId)}</span>
                    <Check size={16} className="check-icon" />
                  </div>
                ))}
              </div>
            </div>

            <button 
              type="button" 
              className="edit-topics-button"
              onClick={handleEditTopics}
            >
              <Edit size={20} />
              Edit Topics
            </button>

            <p className="newsletter-note">
              📧 You're receiving weekly digests every Monday with news about your selected topics.
            </p>
          </div>
        ) : (
          // Show topic selection (new subscriber or editing topics)
          <form onSubmit={handleSubmit} className="newsletter-form">
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                disabled={isExistingSubscriber}
                style={isExistingSubscriber ? { backgroundColor: '#f5f5f5', cursor: 'not-allowed' } : {}}
                required
              />
            </div>

            {isEditingTopics && (
              <div className="edit-instructions">
                <p>✨ Click to add or remove topics. You must have at least one topic selected.</p>
              </div>
            )}

            <div className="topics-section">
              <h3>Cryptocurrency Topics</h3>
              <div className="topics-grid">
                {cryptoTopics.map(topic => {
                  const isSelected = selectedTopics.includes(topic.id);
                  
                  return (
                    <button
                      key={topic.id}
                      type="button"
                      className={`topic-chip ${isSelected ? 'selected' : ''}`}
                      onClick={() => toggleTopic(topic.id)}
                    >
                      <span className="topic-icon">{topic.icon}</span>
                      <span className="topic-name">{topic.name}</span>
                      {isSelected && (
                        <Check size={16} className="check-icon" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="topics-section">
              <h3>NFT Topics</h3>
              <div className="topics-grid">
                {nftTopics.map(topic => {
                  const isSelected = selectedTopics.includes(topic.id);
                  
                  return (
                    <button
                      key={topic.id}
                      type="button"
                      className={`topic-chip ${isSelected ? 'selected' : ''}`}
                      onClick={() => toggleTopic(topic.id)}
                    >
                      <span className="topic-icon">{topic.icon}</span>
                      <span className="topic-name">{topic.name}</span>
                      {isSelected && (
                        <Check size={16} className="check-icon" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {status && (
              <div className={`status-message ${status.type}`}>
                {status.message}
              </div>
            )}

            <div className="button-group">
              {isEditingTopics && (
                <button 
                  type="button" 
                  className="cancel-button"
                  onClick={handleCancelEdit}
                >
                  Cancel
                </button>
              )}
              <button 
                type="submit" 
                className="submit-button"
                disabled={isSubmitting || selectedTopics.length === 0}
              >
                {isSubmitting ? 'Saving...' : isEditingTopics ? `Save ${selectedTopics.length} Topic${selectedTopics.length !== 1 ? 's' : ''}` : `Subscribe to ${selectedTopics.length} Topic${selectedTopics.length !== 1 ? 's' : ''}`}
              </button>
            </div>

            <p className="newsletter-note">
              📧 You'll receive a weekly digest every Monday with news about your selected topics.
            </p>
          </form>
        )}
      </div>
    </div>
  );
};

export default NewsletterSubscription;
