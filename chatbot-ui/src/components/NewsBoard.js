import React, { useState, useEffect } from 'react';
import { X, Search, TrendingUp, ExternalLink, ThumbsUp, ThumbsDown, AlertCircle, Clock, ArrowLeft } from 'lucide-react';
import { getNewsUrl } from '../config/api';
import './NewsBoard.css';

const NewsBoard = ({ onClose }) => {
  const [newsData, setNewsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState(null);

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = async (query = '') => {
    setLoading(true);
    setError(null);
    setIsSearching(!!query);
    
    try {
      const url = getNewsUrl(query);
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        setNewsData(data.news || []);
      } else {
        setError(data.error || 'Failed to fetch news');
      }
    } catch (err) {
      setError('Failed to connect to server');
      console.error('News fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      fetchNews(searchQuery.trim());
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setIsSearching(false);
    fetchNews();
  };

  const formatDate = (timestamp) => {
    // CryptoCompare returns Unix timestamp in seconds
    const date = new Date(timestamp * 1000); // Convert to milliseconds
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const openArticle = (article) => {
    setSelectedArticle(article);
  };

  const closeArticle = () => {
    setSelectedArticle(null);
  };

  // Full article modal
  if (selectedArticle) {
    return (
      <div className="newsboard-overlay" onClick={closeArticle}>
        <div className="newsboard-container article-view" onClick={(e) => e.stopPropagation()}>
          <div className="newsboard-header">
            <button className="back-button" onClick={closeArticle}>
              <ArrowLeft size={20} />
              Back to News
            </button>
            <button className="close-button" onClick={onClose}>
              <X size={24} />
            </button>
          </div>
          
          <div className="article-content">
            {selectedArticle.imageurl && (
              <div className="article-image-wrapper">
                <img 
                  src={selectedArticle.imageurl} 
                  alt={selectedArticle.title}
                  className="article-image"
                  onError={(e) => e.target.style.display = 'none'}
                />
              </div>
            )}
            
            <div className="article-meta">
              <span className="article-source">{selectedArticle.source}</span>
              <span className="article-time">
                <Clock size={14} />
                {formatDate(selectedArticle.published_at)}
              </span>
            </div>
            
            <h1 className="article-title">{selectedArticle.title}</h1>
            
            {selectedArticle.categories && selectedArticle.categories.length > 0 && (
              <div className="article-currencies">
                {selectedArticle.categories.slice(0, 5).map((category, idx) => (
                  <span key={idx} className="currency-tag">{category}</span>
                ))}
              </div>
            )}
            
            {selectedArticle.description && (
              <div className="article-description">
                <p>{selectedArticle.description}</p>
              </div>
            )}
            
            <div className="article-votes">
              <div className="vote-item positive">
                <ThumbsUp size={16} />
                <span>{selectedArticle.votes.upvotes || 0} upvotes</span>
              </div>
              {selectedArticle.votes.downvotes > 0 && (
                <div className="vote-item negative">
                  <ThumbsDown size={16} />
                  <span>{selectedArticle.votes.downvotes} downvotes</span>
                </div>
              )}
            </div>
            
            {selectedArticle.url && (
              <div className="article-actions">
                <a 
                  href={selectedArticle.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="read-full-article"
                  onClick={(e) => e.stopPropagation()}
                >
                  <ExternalLink size={16} />
                  Read Full Article
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Main news list view
  return (
    <div className="newsboard-overlay" onClick={onClose}>
      <div className="newsboard-container" onClick={(e) => e.stopPropagation()}>
        <div className="newsboard-header">
          <div className="header-title">
            <TrendingUp size={24} style={{ color: '#ffd700' }} />
            <h2>Crypto News</h2>
          </div>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="newsboard-search">
          <form onSubmit={handleSearch}>
            <div className="search-input-wrapper">
              <Search size={20} className="search-icon" />
              <input
                type="text"
                className="search-input"
                placeholder="Search news for a specific coin (e.g., Bitcoin, ETH, BNB)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button
                  type="button"
                  className="clear-search"
                  onClick={clearSearch}
                >
                  <X size={18} />
                </button>
              )}
            </div>
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>
          {isSearching && (
            <div className="search-info">
              Showing news for: <strong>{searchQuery}</strong>
              <button className="clear-filter" onClick={clearSearch}>Clear</button>
            </div>
          )}
        </div>

        <div className="newsboard-content">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading latest crypto news...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <AlertCircle size={48} />
              <p>{error}</p>
              <button onClick={() => fetchNews()} className="retry-button">
                Try Again
              </button>
            </div>
          ) : newsData.length === 0 ? (
            <div className="no-results">
              <Search size={48} />
              <p>No news found</p>
              {isSearching && (
                <button onClick={clearSearch} className="back-button">
                  Back to all news
                </button>
              )}
            </div>
          ) : (
            <div className="news-grid">
              {newsData.map((article) => (
                <div key={article.id} className="news-card" onClick={() => openArticle(article)}>
                  <div className="news-card-header">
                    <div className="news-source">
                      <span className="source-name">{article.source}</span>
                      <span className="news-time">
                        <Clock size={12} />
                        {formatDate(article.published_at)}
                      </span>
                    </div>
                    {article.categories && article.categories.length > 0 && (
                      <div className="news-currencies">
                        {article.categories.slice(0, 3).map((category, idx) => (
                          <span key={idx} className="currency-badge">{category}</span>
                        ))}
                        {article.categories.length > 3 && (
                          <span className="currency-badge more">+{article.categories.length - 3}</span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <h3 className="news-title">{article.title}</h3>
                  
                  <div className="news-footer">
                    <div className="news-votes">
                      {article.votes.upvotes > 0 && (
                        <span className="vote-count positive">
                          <ThumbsUp size={14} />
                          {article.votes.upvotes}
                        </span>
                      )}
                    </div>
                    <span className="read-more">
                      Read more <ExternalLink size={14} />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NewsBoard;
