// API Configuration - centralized environment variables
// All API URLs are defined here for easy production deployment

export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// API Endpoints
export const ENDPOINTS = {
  chat: `${API_URL}/chat`,
  chatStream: `${API_URL}/chat/stream`,
  trending: `${API_URL}/trending`,
  news: `${API_URL}/news`,
  newsletter: {
    subscribe: `${API_URL}/api/newsletter/subscribe`,
    unsubscribe: `${API_URL}/api/newsletter/unsubscribe`,
    topics: (email) => `${API_URL}/api/newsletter/topics/${encodeURIComponent(email)}`,
    updateTopics: `${API_URL}/api/newsletter/topics/update`,
  }
};

// Helper to build news URL with optional search query and pagination
export const getNewsUrl = (searchQuery, page = 1, perPage = 10) => {
  let url = `${ENDPOINTS.news}?page=${page}&per_page=${perPage}`;
  if (searchQuery) {
    url += `&search=${encodeURIComponent(searchQuery)}`;
  }
  return url;
};

export default API_URL;
