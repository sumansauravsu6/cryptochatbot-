import React, { useState, useEffect } from 'react';
import { X, TrendingUp, Flame, Search } from 'lucide-react';
import { ENDPOINTS } from '../config/api';
import './Dashboard.css';

const Dashboard = ({ onClose }) => {
  const [trendingData, setTrendingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTrendingData();
  }, []);

  const fetchTrendingData = async () => {
    try {
      setLoading(true);
      const response = await fetch(ENDPOINTS.trending);
      const result = await response.json();
      
      if (result.success) {
        setTrendingData(result.data);
        setError(null);
      } else {
        setError(result.error || 'Failed to fetch trending data');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatMarketCap = (marketCap) => {
    if (!marketCap) return 'N/A';
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
    return `$${marketCap.toLocaleString()}`;
  };

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    if (price < 0.01) return `$${price.toFixed(6)}`;
    if (price < 1) return `$${price.toFixed(4)}`;
    return `$${price.toFixed(2)}`;
  };

  return (
    <div className="dashboard-overlay">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div className="dashboard-title">
            <Flame className="dashboard-icon" />
            <h2>Trending Dashboard</h2>
          </div>
          <button className="dashboard-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        {loading && (
          <div className="dashboard-loading">
            <div className="spinner"></div>
            <p>Loading trending data...</p>
          </div>
        )}

        {error && (
          <div className="dashboard-error">
            <p>{error}</p>
            <button onClick={fetchTrendingData}>Retry</button>
          </div>
        )}

        {!loading && !error && trendingData && (
          <div className="dashboard-content">
            {/* Trending Coins */}
            <section className="dashboard-section">
              <div className="section-header">
                <TrendingUp className="section-icon" />
                <h3>Trending Coins</h3>
              </div>
              <div className="trending-grid">
                {trendingData.coins?.slice(0, 6).map((item, index) => (
                  <div key={item.item.id} className="trending-card">
                    <div className="card-rank">#{index + 1}</div>
                    <div className="card-header">
                      <img 
                        src={item.item.small} 
                        alt={item.item.name} 
                        className="coin-image"
                      />
                      <div className="coin-info">
                        <h4>{item.item.name}</h4>
                        <span className="coin-symbol">{item.item.symbol}</span>
                      </div>
                    </div>
                    <div className="card-details">
                      <div className="detail-row">
                        <span className="detail-label">Price (BTC):</span>
                        <span className="detail-value">{item.item.price_btc?.toFixed(8) || 'N/A'}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Market Cap Rank:</span>
                        <span className="detail-value">#{item.item.market_cap_rank || 'N/A'}</span>
                      </div>
                      {item.item.data?.price && (
                        <div className="detail-row">
                          <span className="detail-label">Price USD:</span>
                          <span className="detail-value">{formatPrice(parseFloat(item.item.data.price))}</span>
                        </div>
                      )}
                      {item.item.data?.market_cap && (
                        <div className="detail-row">
                          <span className="detail-label">Market Cap:</span>
                          <span className="detail-value">{formatMarketCap(parseFloat(item.item.data.market_cap))}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Trending NFTs */}
            {trendingData.nfts && trendingData.nfts.length > 0 && (
              <section className="dashboard-section">
                <div className="section-header">
                  <Flame className="section-icon" />
                  <h3>Trending NFTs</h3>
                </div>
                <div className="trending-grid">
                  {trendingData.nfts.slice(0, 6).map((nft, index) => (
                    <div key={nft.id} className="trending-card nft-card">
                      <div className="card-rank">#{index + 1}</div>
                      <div className="card-header">
                        <img 
                          src={nft.thumb} 
                          alt={nft.name} 
                          className="nft-image"
                        />
                        <div className="coin-info">
                          <h4>{nft.name}</h4>
                          <span className="nft-symbol">{nft.symbol}</span>
                        </div>
                      </div>
                      <div className="card-details">
                        <div className="detail-row">
                          <span className="detail-label">Floor Price:</span>
                          <span className="detail-value">{nft.floor_price_in_native_currency?.toFixed(4) || 'N/A'} {nft.native_currency_symbol}</span>
                        </div>
                        {nft.floor_price_24h_percentage_change && (
                          <div className="detail-row">
                            <span className="detail-label">24h Change:</span>
                            <span className={`detail-value ${nft.floor_price_24h_percentage_change > 0 ? 'positive' : 'negative'}`}>
                              {nft.floor_price_24h_percentage_change.toFixed(2)}%
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Trending Categories */}
            {trendingData.categories && trendingData.categories.length > 0 && (
              <section className="dashboard-section">
                <div className="section-header">
                  <Search className="section-icon" />
                  <h3>Trending Categories</h3>
                </div>
                <div className="categories-list">
                  {trendingData.categories.slice(0, 10).map((category, index) => (
                    <div key={category.id} className="category-card">
                      <div className="category-rank">#{index + 1}</div>
                      <div className="category-info">
                        <h4>{category.name}</h4>
                        <div className="category-details">
                          <span className="category-stat">
                            Market Cap: {formatMarketCap(category.market_cap)}
                          </span>
                          <span className={`category-change ${category.market_cap_change_24h > 0 ? 'positive' : 'negative'}`}>
                            24h: {category.market_cap_change_24h?.toFixed(2)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
