"""
CryptoPanic API Integration
Provides news aggregation for cryptocurrency and blockchain topics
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CRYPTOPANIC_API_KEY = os.getenv('CRYPTOPANIC_API_KEY', '')
CRYPTOPANIC_BASE_URL = "https://cryptopanic.com/api/v1"


def get_cryptopanic_news(filter_type='rising', currencies=None, regions=None, kind='news', limit=20):
    """
    Get news from CryptoPanic API
    
    Args:
        filter_type: Type of filter ('rising', 'hot', 'bullish', 'bearish', 'important', 'saved', 'lol')
        currencies: Comma-separated currency codes (e.g., 'BTC,ETH')
        regions: Comma-separated region codes (e.g., 'en,de')
        kind: Type of posts ('news' or 'media' or 'all')
        limit: Number of results to return (max 100)
    
    Returns:
        dict: News data from CryptoPanic
    """
    url = f"{CRYPTOPANIC_BASE_URL}/posts/"
    
    params = {
        'auth_token': CRYPTOPANIC_API_KEY,
        'kind': kind,
        'filter': filter_type
    }
    
    if currencies:
        params['currencies'] = currencies
    
    if regions:
        params['regions'] = regions
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Debug: Print first article structure
        if 'results' in data and len(data['results']) > 0:
            print(f"DEBUG - First article from API: {data['results'][0]}")
        
        # Limit results
        if 'results' in data and len(data['results']) > limit:
            data['results'] = data['results'][:limit]
        
        return data
    except Exception as e:
        print(f"Error fetching CryptoPanic news: {e}")
        return {'results': [], 'count': 0}


def search_cryptopanic_news(query, currencies=None, limit=10):
    """
    Search CryptoPanic news by topic/query
    
    Args:
        query: Search query or topic
        currencies: Specific currencies to filter by (comma-separated)
        limit: Number of results
    
    Returns:
        list: List of news articles
    """
    # Get rising news filtered by currencies if specified
    news_data = get_cryptopanic_news(
        filter_type='rising',
        currencies=currencies,
        kind='news',
        limit=limit * 2  # Get more to filter
    )
    
    if not news_data.get('results'):
        return []
    
    # Filter results by query in title or description
    query_lower = query.lower()
    filtered_results = []
    
    for article in news_data['results']:
        title = article.get('title', '').lower()
        if query_lower in title:
            filtered_results.append(article)
            if len(filtered_results) >= limit:
                break
    
    # If not enough filtered results, return all up to limit
    if len(filtered_results) < limit:
        filtered_results = news_data['results'][:limit]
    
    return filtered_results


def get_news_for_topic(topic_id, limit=3):
    """
    Get news articles for a specific topic using CryptoPanic
    
    Args:
        topic_id: Topic identifier (e.g., 'bitcoin', 'ethereum', 'defi')
        limit: Number of articles to fetch
    
    Returns:
        list: List of formatted news articles
    """
    # Map topics to CryptoPanic currency codes or search terms
    topic_currency_map = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'altcoins': None,  # Will search broadly
        'defi': None,
        'trading': None,
        'mining': 'BTC',
        'regulation': None,
        'market-analysis': None,
        'nft-cryptopunks': None,
        'nft-bored-ape': None,
        'nft-art': None,
        'nft-gaming': None,
        'nft-marketplace': None,
        'nft-metaverse': None
    }
    
    # Get currency code if available
    currency_code = topic_currency_map.get(topic_id)
    
    # Determine search query
    search_queries = {
        'bitcoin': 'Bitcoin',
        'ethereum': 'Ethereum',
        'altcoins': 'altcoin',
        'defi': 'DeFi',
        'trading': 'trading',
        'mining': 'mining',
        'regulation': 'regulation',
        'market-analysis': 'market',
        'nft-cryptopunks': 'CryptoPunks',
        'nft-bored-ape': 'Bored Ape',
        'nft-art': 'NFT art',
        'nft-gaming': 'NFT gaming',
        'nft-marketplace': 'NFT marketplace',
        'nft-metaverse': 'metaverse'
    }
    
    query = search_queries.get(topic_id, topic_id)
    
    try:
        # Get news from CryptoPanic
        articles = search_cryptopanic_news(query, currency_code, limit)
        
        # Format articles to match the expected structure
        formatted_articles = []
        for article in articles:
            # CryptoPanic API returns 'url' for the post page, 
            # we need to construct or use alternative URL fields
            article_url = article.get('url', '')
            
            # If url is empty, try to use the cryptopanic post link
            if not article_url:
                post_id = article.get('id', '')
                if post_id:
                    article_url = f"https://cryptopanic.com/news/{post_id}"
            
            formatted_article = {
                'title': article.get('title', ''),
                'url': article_url,
                'published_at': article.get('published_at', ''),
                'source': {
                    'title': article.get('source', {}).get('title', 'CryptoPanic'),
                    'domain': article.get('source', {}).get('domain', '')
                },
                'currencies': article.get('currencies', []),
                'votes': article.get('votes', {}),
                'created_at': article.get('created_at', ''),
                'id': article.get('id', '')
            }
            formatted_articles.append(formatted_article)
        
        return formatted_articles
    
    except Exception as e:
        print(f"Error fetching news for topic {topic_id}: {e}")
        return []


def get_trending_news(limit=10):
    """
    Get trending/hot news from CryptoPanic
    
    Args:
        limit: Number of articles to return
    
    Returns:
        list: List of trending news articles
    """
    news_data = get_cryptopanic_news(filter_type='hot', kind='news', limit=limit)
    return news_data.get('results', [])


def get_important_news(limit=10):
    """
    Get important/breaking news from CryptoPanic
    
    Args:
        limit: Number of articles to return
    
    Returns:
        list: List of important news articles
    """
    news_data = get_cryptopanic_news(filter_type='important', kind='news', limit=limit)
    return news_data.get('results', [])


if __name__ == '__main__':
    # Test the API
    print("Testing CryptoPanic API...")
    print("\n1. Bitcoin News:")
    btc_news = get_news_for_topic('bitcoin', limit=2)
    for i, article in enumerate(btc_news, 1):
        print(f"   {i}. {article['title']}")
        print(f"      URL: {article.get('url', 'NO URL')}")
        print(f"      ID: {article.get('id', 'NO ID')}")
    
    print("\n✅ Test complete!")
