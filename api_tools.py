"""
API Tools Module
Contains all API functions for cryptocurrency, exchange rates, and market data
"""

import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Load coin list
def load_coin_list():
    try:
        with open('coins.json', 'r') as f:
            return json.load(f)
    except:
        return []

COINS_LIST = load_coin_list()

# Load NFT list
def load_nft_list():
    try:
        with open('nft.json', 'r') as f:
            return json.load(f)
    except:
        return []

NFT_LIST = load_nft_list()

def is_cryptocurrency(name):
    """Check if a name matches a cryptocurrency in coins.json"""
    name_lower = name.lower().strip()
    
    # Check exact matches first
    for coin in COINS_LIST:
        if coin['id'] == name_lower:
            return True
        if coin['symbol'].lower() == name_lower:
            return True
        if coin['name'].lower() == name_lower:
            return True
    
    return False


def is_nft(name):
    """Check if a name matches an NFT in nft.json or known NFT keywords"""
    name_lower = name.lower().strip()
    
    # Known NFT keywords that should always be treated as NFTs
    # These take priority over crypto matches
    nft_keywords = [
        'cryptopunk', 'cryptopunks', 'bored ape', 'bayc', 'mutant ape', 'mayc',
        'azuki', 'clone x', 'clonex', 'doodle', 'doodles', 'moonbird', 'moonbirds',
        'pudgy penguin', 'pudgy penguins', 'art blocks', 'world of women', 'wow',
        'meebit', 'meebits'  # Include both singular and plural
    ]
    
    if name_lower in nft_keywords:
        return True
    
    # Check exact matches in NFT list
    for nft in NFT_LIST:
        if nft['id'] == name_lower:
            return True
        if nft['name'].lower() == name_lower:
            return True
    
    return False


def determine_category(name):
    """Determine if a name is a cryptocurrency or NFT
    Returns: 'crypto', 'nft', or 'unknown'
    """
    # Check NFT keywords first for known NFT collections
    # This takes priority over crypto matches for ambiguous names
    if is_nft(name):
        # But if it's ALSO a crypto with exact match, check which is more likely
        name_lower = name.lower().strip()
        for coin in COINS_LIST:
            # Exact ID or name match to crypto takes precedence
            if coin['id'] == name_lower or coin['name'].lower() == name_lower:
                # If the name contains NFT-specific words, it's likely an NFT
                nft_indicators = ['punk', 'ape', 'yacht', 'mutant', 'bored', 'doodle', 'moonbird']
                if any(indicator in name_lower for indicator in nft_indicators):
                    return 'nft'
                return 'crypto'
        return 'nft'
    
    # Check cryptocurrency
    if is_cryptocurrency(name):
        return 'crypto'
    
    return 'unknown'


def find_coin_id(coin_name):
    """Find the correct coin ID from coins.json"""
    coin_name_lower = coin_name.lower().strip()
    
    for coin in COINS_LIST:
        if coin['id'] == coin_name_lower:
            return coin['id']
    
    for coin in COINS_LIST:
        if coin['symbol'].lower() == coin_name_lower:
            return coin['id']
    
    for coin in COINS_LIST:
        if coin['name'].lower() == coin_name_lower:
            return coin['id']
    
    for coin in COINS_LIST:
        if coin_name_lower in coin['name'].lower() or coin_name_lower in coin['symbol'].lower():
            return coin['id']
    
    return coin_name_lower


def find_nft_id(nft_name):
    """Find the correct NFT ID from nft.json or pass through for API resolution"""
    nft_name_lower = nft_name.lower().strip()
    
    # IMPORTANT: If this matches a cryptocurrency, return None to avoid confusion
    if is_cryptocurrency(nft_name):
        return None
    
    # Common NFT name mappings (handle popular NFT variations)
    nft_mappings = {
        'cryptopunk': 'cryptopunks',
        'bored ape': 'bored-ape-yacht-club',
        'bayc': 'bored-ape-yacht-club',
        'mutant ape': 'mutant-ape-yacht-club',
        'mayc': 'mutant-ape-yacht-club',
        'clone x': 'clonex',
        'meebit': 'meebits',  # Only map "meebit" not "meebitstrategy"
        'doodle': 'doodles-official',
        'moonbird': 'proof-moonbirds',
        'pudgy penguin': 'pudgy-penguins',
    }
    
    # Check if there's a direct mapping (only for exact matches)
    if nft_name_lower in nft_mappings:
        nft_name_lower = nft_mappings[nft_name_lower]
    
    # Try exact ID match
    for nft in NFT_LIST:
        if nft['id'] == nft_name_lower:
            return nft['id']
    
    # Try exact name match
    for nft in NFT_LIST:
        if nft['name'].lower() == nft_name_lower:
            return nft['id']
    
    # Try symbol match
    for nft in NFT_LIST:
        if nft.get('symbol', '').lower() == nft_name_lower:
            return nft['id']
    
    # Try partial name match (but only if not too generic)
    for nft in NFT_LIST:
        if len(nft_name_lower) >= 5 and nft_name_lower in nft['name'].lower():
            return nft['id']
    
    # Try fuzzy matching for singular/plural (only for known NFT names)
    if len(nft_name_lower) >= 5:  # Avoid matching very short words
        variations = [
            nft_name_lower + 's',  # Add 's' for plural
            nft_name_lower[:-1] if nft_name_lower.endswith('s') else None,  # Remove 's'
        ]
        
        for variant in variations:
            if variant:
                for nft in NFT_LIST:
                    if nft['id'] == variant or nft['name'].lower() == variant:
                        return nft['id']
    
    # Return original name - CoinGecko API might resolve it directly
    return nft_name_lower


# Cryptocurrency API Functions
def get_crypto_global_market_data():
    """Get global cryptocurrency market data"""
    url = "https://api.coingecko.com/api/v3/global"
    headers = {"x-cg-demo-api-key": "CG-bm1iokxRmUk2d17v5EamRWso"}
    response = requests.get(url, headers=headers)
    return response.json()


def get_coin_price(vs_currency: str = "inr", coin_id: str = "bitcoin"):
    """Get current price of a cryptocurrency"""
    resolved_id = find_coin_id(coin_id)
    url = f"https://api.coingecko.com/api/v3/simple/price?vs_currencies={vs_currency}&ids={resolved_id}"
    headers = {"x-cg-demo-api-key": os.getenv('COINGECKO_API_KEY', 'CG-bm1iokxRmUk2d17v5EamRWso')}
    response = requests.get(url, headers=headers)
    return response.json()


def get_coin_info(coin_id: str = "bitcoin"):
    """Get detailed information about a specific cryptocurrency"""
    resolved_id = find_coin_id(coin_id)
    url = f"https://api.coingecko.com/api/v3/coins/{resolved_id}"
    headers = {"x-cg-demo-api-key": os.getenv('COINGECKO_API_KEY', 'CG-bm1iokxRmUk2d17v5EamRWso')}
    params = {
        "localization": "false",
        "tickers": "false",
        "community_data": "true",
        "developer_data": "false"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_coin_market_data(coin_id: str = "bitcoin"):
    """Get market data for a specific cryptocurrency"""
    resolved_id = find_coin_id(coin_id)
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    headers = {"x-cg-demo-api-key": os.getenv('COINGECKO_API_KEY', 'CG-bm1iokxRmUk2d17v5EamRWso')}
    params = {
        "vs_currency": "usd",
        "ids": resolved_id,
        "order": "market_cap_desc",
        "per_page": 1,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d,30d"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def search_crypto_news(query: str = "bitcoin"):
    """Search for cryptocurrency news"""
    url = "https://api.coingecko.com/api/v3/search"
    headers = {"x-cg-demo-api-key": os.getenv('COINGECKO_API_KEY', 'CG-bm1iokxRmUk2d17v5EamRWso')}
    params = {"query": query}
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_crypto_histrical_data(from_date: str, to_date: str, base_currency: str, target_currency: str):
    """Get historical cryptocurrency price data"""
    url = "https://api.coingecko.com/api/v3/coins/"
    resolved_id = find_coin_id(base_currency)
    url += f"{resolved_id}/market_chart/range"
    headers = {"x-cg-demo-api-key": os.getenv('COINGECKO_API_KEY', 'CG-bm1iokxRmUk2d17v5EamRWso')}
    params = {
        "vs_currency": target_currency,
        "from": int(datetime.strptime(from_date, "%Y-%m-%d").timestamp()),
        "to": int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


# Exchange Rate API Functions
def get_exchange_rate(from_currency: str = "USD", to_currency: str = "EUR"):
    """Get current exchange rate between two currencies"""
    url = "https://api.exchangerate.host/convert"
    params = {
        "from": from_currency,
        "to": to_currency,
        "amount": 1,
        "access_key": "686b242c0505e671eeac38e561b169a6"
    }
    response = requests.get(url, params=params)
    result = response.json()
    print(f"Exchange rate API response for {from_currency} to {to_currency}: {result}")
    return result


def get_exchange_rate_for_time_period(from_currency: str, to_currency: str, start_date: str, end_date: str):
    """Get historical exchange rates for a time period"""
    url = "https://api.exchangerate.host/timeframe"
    params = {
        "source": from_currency,
        "currencies": to_currency,
        "start_date": start_date,
        "end_date": end_date,
        "access_key": "686b242c0505e671eeac38e561b169a6"
    }
    response = requests.get(url, params=params)
    return response.json()


def convert_currency(from_currency: str, to_currency: str, amount: float):
    """Convert an amount from one currency to another"""
    url = "https://api.exchangerate.host/convert"
    params = {
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "access_key": "686b242c0505e671eeac38e561b169a6"
    }
    response = requests.get(url, params=params)
    return response.json()


# Utility function
def greet(name):
    """Simple greeting function"""
    return f"Hello, {name}!"


def get_nft_collection_data(id: str):
    """Get NFT collection data from OpenSea API"""
   
    url = f"https://api.opensea.io/api/v1/collection/{id}"
    headers = {
        "Accept": "application/json",
        "X-API-KEY": os.getenv('OPENSEA_API_KEY', '')
    }
    response = requests.get(url, headers=headers)
    return response.json()


def get_nft_info(nft_name: str):
    """Get detailed NFT information from CoinGecko"""
    nft_id = find_nft_id(nft_name)
    url = f"https://api.coingecko.com/api/v3/nfts/{nft_id}"
    headers = {"x-cg-demo-api-key": os.getenv('COINGECKO_API_KEY', '')}
    response = requests.get(url, headers=headers)
    return response.json()


def search_nft(query: str):
    """Search for NFTs by name"""
    query_lower = query.lower()
    results = []
    
    for nft in NFT_LIST:
        if query_lower in nft['name'].lower() or query_lower in nft['id'].lower():
            results.append(nft)
        if len(results) >= 10:  # Limit to 10 results
            break
    
    return results
