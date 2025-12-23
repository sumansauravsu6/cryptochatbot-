from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
import json
import re

# Load environment variables
load_dotenv()

# Import modularized components
from api_tools import (
    greet,
    get_crypto_global_market_data,
    get_coin_price,
    get_coin_info,
    get_coin_market_data,
    search_crypto_news,
    get_exchange_rate,
    get_exchange_rate_for_time_period,
    convert_currency,
    get_crypto_histrical_data,
    load_coin_list,
    COINS_LIST,
    get_nft_info,
    search_nft,
    find_nft_id,
    NFT_LIST,
    determine_category,
    is_cryptocurrency,
    is_nft
)
from chart_generator import create_chart_data
from newsletter_api import (
    subscribe_to_newsletter, 
    unsubscribe_from_newsletter,
    get_subscriber_info,
    update_subscriber_topics
)

app = Flask(__name__)

# Configure CORS for production - allow all origins for now
CORS(app, resources={r"/*": {"origins": "*"}})

# Tools dictionary for function calling
tools = {
    "greet": greet,
    "get_crypto_global_market_data": get_crypto_global_market_data,
    "get_coin_price": get_coin_price,
    "get_coin_info": get_coin_info,
    "get_coin_market_data": get_coin_market_data,
    "search_crypto_news": search_crypto_news,
    "get_exchange_rate": get_exchange_rate,
    "convert_currency": convert_currency,
    "get_exchange_rate_for_time_period": get_exchange_rate_for_time_period,
    "get_crypto_histrical_data": get_crypto_histrical_data,
    "get_nft_info": get_nft_info,
    "search_nft": search_nft,
    "determine_category": determine_category
}

# API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_URL = os.getenv('GROQ_URL', 'https://api.groq.com/openai/v1/chat/completions')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
TIMEOUT = 60


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        # Get today's date for context
        today = datetime.now().strftime("%Y-%m-%d")
        days_15_ago = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
        
        # Build prompt
        prompt = f"""You are a friendly crypto buddy who helps with cryptocurrency and currency exchange info. Talk like you're chatting with a friend!

IMPORTANT: Today's date is {today}.

Currency Code Reference:
- Pound, British Pound, Sterling = GBP
- Euro = EUR
- Dollar, US Dollar = USD
- Yen, Japanese Yen = JPY
- Rupee, Indian Rupee = INR
- Australian Dollar = AUD
- Canadian Dollar = CAD
- Swiss Franc = CHF
- Yuan, Chinese Yuan = CNY
- Afghan Afghani = AFN

Cryptocurrency Note:
- For get_coin_price function, you can use common names (Bitcoin, XRP, Zcash, Ethereum, Cardano, Dogecoin, Litecoin, etc.)
- The system will automatically find the correct coin ID
- Use the name, symbol, or ticker as you know it

You have access to the following functions:
0. determine_category(name: str) - **USE THIS FIRST** to determine if a name is 'crypto', 'nft', or 'unknown'. Returns the category type.
1. get_crypto_global_market_data() - Returns global cryptocurrency market data.
2. get_coin_price(vs_currency: str="inr", coin_id: str = "bitcoin") - Returns the price of a specific cryptocurrency in a given currency.
3. get_coin_info(coin_id: str = "bitcoin") - Get detailed information about a coin (description, market cap rank, categories, website, social links, etc.)
4. get_coin_market_data(coin_id: str = "bitcoin") - Get comprehensive market data for a coin (current price, 24h/7d/30d changes, market cap, volume, ATH, ATL, etc.)
5. search_crypto_news(query: str = "bitcoin") - Search for news and information about cryptocurrencies
6. get_exchange_rate(from_currency: str = "USD", to_currency: str = "EUR") - Get latest exchange rate between two currencies.
7. convert_currency(from_currency: str, to_currency: str, amount: float) - Convert an amount from one currency to another.
8. greet(name) - Returns a greeting message for the given name.
9. get_exchange_rate_for_time_period(from_currency: str, to_currency: str, start_date: str, end_date: str) - Get exchange rates for a date range. Dates must be in YYYY-MM-DD format.
10. get_crypto_histrical_data(from_date: str, to_date: str, base_currency: str, target_currency: str) - Get historical market data for a cryptocurrency between two dates.
11. get_nft_info(nft_name: str) - Get detailed information about a specific NFT collection from CoinGecko. The system will automatically resolve NFT names to IDs (e.g., "CryptoPunks", "Bored Ape", "Azuki").
12. search_nft(query: str) - Search for NFT collections by name or keyword. Returns up to 10 matching NFT collections.

User question: "{user_message}"

CRITICAL - CATEGORY DETECTION FIRST:
When user asks about price or info of something ambiguous (e.g., "Meebit", "Punk"), ALWAYS call determine_category(name) FIRST to check if it's a crypto or NFT.
Example workflow:
1. User asks: "what is the price of meebitstrategy"
2. Call: determine_category("meebitstrategy") -> returns "crypto"
3. Then call: get_coin_price("usd", "meebitstrategy")

IMPORTANT FUNCTION SELECTION:
- **ALWAYS use determine_category() first for ambiguous names**
- If determine_category returns "crypto" -> use get_coin_price() or get_coin_info()
- If determine_category returns "nft" -> use get_nft_info()
- For "tell me about [coin]" or "what is [coin]" or "info about [coin]" -> use get_coin_info(coin_id)
- For "news about [coin]" or "[coin] news" -> use search_crypto_news(query)
- For market data, price changes, volume -> use get_coin_market_data(coin_id)
- For finding NFTs like "search for [NFT]" or "find [NFT]" -> use search_nft(query)

NFT KEYWORDS (always NFT): CryptoPunks, Bored Ape, BAYC, Azuki, Meebits (not MeebitStrategy!), Doodles, Moonbirds, CloneX, Pudgy Penguins, Mutant Ape, Art Blocks, World of Women

When the user's question requires a function call, respond with ONLY the function call in this exact format:
FUNCTION_CALL: function_name(arg1, arg2)

IMPORTANT: If the user asks to compare or get multiple things, you can call multiple functions by putting each on a new line:
FUNCTION_CALL: function1(args)
FUNCTION_CALL: function2(args)

If no function is needed, just answer the question normally.

Examples:
- "What is the current global cryptocurrency market status?" -> FUNCTION_CALL: get_crypto_global_market_data()
- "Compare Bitcoin and Ethereum prices in USD" -> 
FUNCTION_CALL: get_coin_price("usd", "bitcoin")
FUNCTION_CALL: get_coin_price("usd", "ethereum")
- "What is the price of Ethereum in USD?" -> FUNCTION_CALL: get_coin_price("usd", "ethereum")
- "Tell me about Bitcoin" -> FUNCTION_CALL: get_coin_info("bitcoin")
- "What is Ethereum?" -> FUNCTION_CALL: get_coin_info("ethereum")
- "Bitcoin news" -> FUNCTION_CALL: search_crypto_news("bitcoin")
- "News about Cardano" -> FUNCTION_CALL: search_crypto_news("cardano")
- "Show me Bitcoin market data" -> FUNCTION_CALL: get_coin_market_data("bitcoin")
- "What's happening with Solana?" -> FUNCTION_CALL: get_coin_market_data("solana")
- "What is the exchange rate from USD to EUR?" -> FUNCTION_CALL: get_exchange_rate("USD", "EUR")
- "What is the exchange rate from pound to INR?" -> FUNCTION_CALL: get_exchange_rate("GBP", "INR")
- "What is the exchange rate from USD to INR?" -> FUNCTION_CALL: get_exchange_rate("USD", "INR")
- "Compare USD to INR and USD to JPY" -> 
FUNCTION_CALL: get_exchange_rate("USD", "INR")
FUNCTION_CALL: get_exchange_rate("USD", "JPY")
- "Compare Australian Dollar vs US Dollar and Afghan Afghani" ->
FUNCTION_CALL: get_exchange_rate("AUD", "USD")
FUNCTION_CALL: get_exchange_rate("AFN", "USD")
- "Convert 100 USD to EUR" -> FUNCTION_CALL: convert_currency("USD", "EUR", 100)
- "Bitcoin price for last 20 days" -> FUNCTION_CALL: get_crypto_histrical_data("{(datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')}", "{today}", "bitcoin", "usd")
- "Show me ETH price from Nov 1 to Nov 30" -> FUNCTION_CALL: get_crypto_histrical_data("2025-11-01", "2025-11-30", "ethereum", "usd")

When calculating dates for time period queries:
- "last 15 days" means from {days_15_ago} to {today}
- "last 7 days" means calculate 7 days before today
- "last month" means calculate 30 days before today
- "last 20 days" means calculate 20 days before today
- Always use YYYY-MM-DD format
- Example: "INR to USD for last 15 days" -> FUNCTION_CALL: get_exchange_rate_for_time_period("INR", "USD", "{days_15_ago}", "{today}")
- Example: "Bitcoin price for last 20 days" -> FUNCTION_CALL: get_crypto_histrical_data("{(datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')}", "{today}", "bitcoin", "usd")

NFT Query Examples:
- "Tell me about CryptoPunks" -> FUNCTION_CALL: get_nft_info("cryptopunks")
- "What is Bored Ape Yacht Club?" -> FUNCTION_CALL: get_nft_info("bored-ape-yacht-club")
- "Search for NFTs related to apes" -> FUNCTION_CALL: search_nft("apes")
- "Find Azuki NFT" -> FUNCTION_CALL: search_nft("azuki")
- "Info about Pudgy Penguins" -> FUNCTION_CALL: get_nft_info("pudgy-penguins")

IMPORTANT: 
- Use get_exchange_rate() for CURRENT exchange rates between fiat currencies
- Use get_exchange_rate_for_time_period() for HISTORICAL exchange rates over a date range
- Use get_coin_price() for CURRENT cryptocurrency prices
- Use get_crypto_histrical_data() for HISTORICAL cryptocurrency prices over a date range
- Use get_nft_info() for detailed information about a specific NFT collection
- Use search_nft() to find NFTs by name or keyword
- Only use time period functions when user explicitly asks for historical data or mentions "last X days/weeks"
"""
        
        # Call Groq API
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        response_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        # Check if response contains function calls
        if "FUNCTION_CALL:" in response_text:
            function_calls = []
            for line in response_text.split('\n'):
                if "FUNCTION_CALL:" in line:
                    func_call = line.split("FUNCTION_CALL:")[-1].strip()
                    if func_call:
                        function_calls.append(func_call)
            
            all_results = []
            graphs_generated = []  # Changed to list to support multiple charts
            
            for function_call in function_calls:
                try:
                    result = eval(function_call, {"__builtins__": {}}, tools)
                    
                    # Add metadata from function call parameters
                    import re
                    
                    # If this is a time period query, add the date parameters to the result for graphing
                    if "get_exchange_rate_for_time_period" in function_call and isinstance(result, dict):
                        match = re.search(r'get_exchange_rate_for_time_period\([^,]+,\s*[^,]+,\s*"([^"]+)",\s*"([^"]+)"\)', function_call)
                        if match:
                            result['start_date'] = match.group(1)
                            result['end_date'] = match.group(2)
                    
                    # If this is a currency conversion, extract from and to currencies from function call
                    elif "get_exchange_rate" in function_call and isinstance(result, dict):
                        match = re.search(r'get_exchange_rate\("([^"]+)",\s*"([^"]+)"\)', function_call)
                        if match:
                            result['_from_currency'] = match.group(1)
                            result['_to_currency'] = match.group(2)
                            print(f"Added metadata to exchange rate result: {match.group(1)} -> {match.group(2)}")
                    
                    all_results.append(result)
                except Exception as e:
                    all_results.append({"error": str(e)})
            
            # Summarize large data before sending to LLM
            def summarize_data(data):
                """Summarize large datasets to avoid payload size issues"""
                if isinstance(data, dict):
                    # Check for NFT data (has floor_price, market_cap structure)
                    if "floor_price" in data and isinstance(data.get("floor_price"), dict):
                        return {
                            "type": "nft_data",
                            "name": data.get("name", "Unknown NFT"),
                            "description": data.get("description", "")[:200],  # Truncate description
                            "floor_price_usd": data["floor_price"].get("usd", 0),
                            "floor_price_eth": data["floor_price"].get("native_currency", 0),
                            "market_cap_usd": data.get("market_cap", {}).get("usd", 0) if isinstance(data.get("market_cap"), dict) else 0,
                            "volume_24h_usd": data.get("volume_24h", {}).get("usd", 0) if isinstance(data.get("volume_24h"), dict) else 0,
                            "total_supply": data.get("total_supply", 0),
                            "floor_price_24h_change": data.get("floor_price_24h_percentage_change", {}).get("usd", 0) if isinstance(data.get("floor_price_24h_percentage_change"), dict) else 0,
                            "website": data.get("links", {}).get("homepage", ""),
                            "twitter": data.get("links", {}).get("twitter", ""),
                            "native_currency": data.get("native_currency", "ETH")
                        }
                    # Check for historical crypto data (CoinGecko format)
                    elif "prices" in data and isinstance(data.get("prices"), list):
                        prices = data["prices"]
                        if len(prices) > 5:
                            return {
                                "type": "crypto_historical_data",
                                "data_points": len(prices),
                                "first_price": prices[0][1],
                                "last_price": prices[-1][1],
                                "highest": max(p[1] for p in prices),
                                "lowest": min(p[1] for p in prices),
                                "summary": f"Historical price data with {len(prices)} data points"
                            }
                    # Check for exchange rate time series
                    elif "quotes" in data and isinstance(data.get("quotes"), dict):
                        return {
                            "type": "exchange_rate_time_series",
                            "currency_pair": f"{data.get('source', 'N/A')} to {list(data['quotes'].values())[0].keys() if data['quotes'] else 'N/A'}",
                            "data_points": len(data["quotes"])
                        }
                return data
            
            # Summarize results to avoid payload issues
            summarized_results = [summarize_data(r) for r in all_results]
            
            # Combine results for LLM decision
            if len(summarized_results) == 1:
                combined_result_str = json.dumps(summarized_results[0], indent=2) if isinstance(summarized_results[0], dict) else str(summarized_results[0])
            else:
                combined_result_str = json.dumps(summarized_results, indent=2)
            
            # Ask LLM if we should create a graph
            visualization_prompt = f"""Based on the following data, should we create a graph/visualization?

Data: {combined_result_str}

Respond with ONLY one of these options:
GRAPH: YES - TIME_SERIES (if the data has multiple dates/time points)
GRAPH: YES - MARKET_SHARE (if the data shows market dominance/percentages)
GRAPH: YES - COMPARISON (if comparing multiple items with numbers)
GRAPH: NO (if graph won't add value)"""

            viz_payload = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": visualization_prompt}],
                "temperature": 0.3,
                "max_tokens": 50
            }
            
            try:
                viz_response = requests.post(GROQ_URL, json=viz_payload, headers=headers, timeout=TIMEOUT)
                viz_response.raise_for_status()
                viz_decision = viz_response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                print(f"LLM Decision: {viz_decision}")
                
                # Create chart based on LLM's decision
                if "GRAPH: YES" in viz_decision or "COMPARISON" in viz_decision or "TIME_SERIES" in viz_decision or "MARKET_SHARE" in viz_decision:
                    # Check if all results are the same type
                    all_time_series = all(
                        isinstance(r, dict) and ("prices" in r or "quotes" in r)
                        for r in all_results
                    )
                    
                    # Check for crypto prices (format: {"bitcoin": {"usd": 92265}})
                    all_crypto_prices = all(
                        isinstance(r, dict) and 
                        not ("query" in r or "quotes" in r or "prices" in r) and
                        len(r) == 1 and isinstance(list(r.values())[0], dict)
                        for r in all_results
                    )
                    
                    print(f"DEBUG: all_crypto_prices = {all_crypto_prices}, len(all_results) = {len(all_results)}")
                    
                    all_single_values = all(
                        isinstance(r, dict) and ("query" in r or "result" in r) and "quotes" not in r and "prices" not in r
                        for r in all_results
                    )
                    
                    # Check if all are exchange rates (have 'query' field with 'from' and 'to')
                    all_exchange_rates = all(
                        isinstance(r, dict) and "query" in r and isinstance(r.get("query"), dict) and 
                        "from" in r.get("query", {}) and "to" in r.get("query", {})
                        for r in all_results
                    )
                    
                    # For exchange rates, ALWAYS create separate charts (one per currency pair)
                    if all_exchange_rates and len(all_results) > 1:
                        print(f"Multiple exchange rates detected - creating {len(all_results)} separate charts (one per pair)")
                        for i, result in enumerate(all_results):
                            chart_result = create_chart_data(result)
                            if chart_result:
                                graphs_generated.append(chart_result)
                                print(f"Exchange rate chart {i+1} added to graphs list")
                    # For crypto price comparisons, combine into ONE chart
                    elif ("COMPARISON" in viz_decision or all_crypto_prices) and len(all_results) > 1 and (all_single_values or all_crypto_prices) and not all_exchange_rates:
                        print(f"Creating single comparison chart with {len(all_results)} results (crypto prices)")
                        chart_result = create_chart_data(all_results)
                        if chart_result:
                            graphs_generated.append(chart_result)
                            print(f"Comparison chart added to graphs list")
                    # For multiple time series, create SEPARATE charts for each
                    elif all_time_series and len(all_results) > 1:
                        print(f"Multiple time series detected - creating {len(all_results)} separate charts")
                        for i, result in enumerate(all_results):
                            chart_result = create_chart_data(result)
                            if chart_result:
                                graphs_generated.append(chart_result)
                                print(f"Chart {i+1} added to graphs list")
                    else:
                        # For single results or mixed types, create charts for each valid one
                        for result in all_results:
                            chart_result = create_chart_data(result)
                            if chart_result:
                                graphs_generated.append(chart_result)
                                print(f"Chart data added to graphs list")
            except Exception as e:
                print(f"Visualization check failed: {e}")
            
            # Generate natural language response using SUMMARIZED data
            # But keep full data for graphing
            if len(summarized_results) == 1:
                response_data_str = json.dumps(summarized_results[0], indent=2) if isinstance(summarized_results[0], dict) else str(summarized_results[0])
            else:
                response_data_str = json.dumps(summarized_results, indent=2)
            
            # Generate natural language response
            prompt2 = f"""You are a helpful crypto assistant. Based on the data below, give a natural, conversational response.

User asked: "{user_message}"

Data:
{response_data_str}

STYLE GUIDELINES:
- Be natural and friendly, but don't overuse phrases or patterns
- DON'T repeat the user's question back to them
- DON'T use the same phrases every time (avoid "pretty cool", "right now", etc.)
- Vary your language naturally
- For SINGLE items: Give a simple, direct answer (NO bullet points)
- For MULTIPLE items (2+): Use bullet points with • on separate lines with \\n

FORMATTING:
- Large numbers: Add commas (8,149,502)
- Currency symbols: ₹ (INR), $ (USD), € (EUR), £ (GBP), ¥ (JPY)
- Keep responses concise and to the point
- **CRITICAL FOR NFT DATA**: When you see "floor_price_usd" field, that is the USD price. Use it directly. The "floor_price_eth" is in ETH, NOT dollars.

EXAMPLES:

Single price: "Bitcoin is at $90,052"
Single rate: "That's ₹83.50 per dollar"
Market data: "The total crypto market cap is $3.17 trillion, with Bitcoin holding 56.8% market share"
NFT data (when you see type: "nft_data"): "Meebits has a floor price of $1,393 (the floor_price_usd field shows 1393.87, so say $1,393). The market cap is $27.8 million."

Comparison (use bullets):
"Here's what I found:\\n• Bitcoin: $90,052\\n• Ethereum: $3,245\\n• Litecoin: $81.19"

Be direct, clear, and natural. Vary your responses."""
            
            payload2 = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt2}],
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            response2 = requests.post(GROQ_URL, json=payload2, headers=headers, timeout=TIMEOUT)
            response2.raise_for_status()
            final_answer = response2.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            # Return only charts array to avoid duplication
            return jsonify({
                'response': final_answer,
                'charts': graphs_generated if len(graphs_generated) > 0 else None
            })
        else:
            return jsonify({
                'response': response_text,
                'charts': None
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trending', methods=['GET'])
def get_trending():
    """Get trending coins, NFTs, and categories from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        headers = {"x-cg-demo-api-key": os.getenv('COINGECKO_API_KEY', 'CG-bm1iokxRmUk2d17v5EamRWso')}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'data': data
            })
        else:
            return jsonify({
                'success': False,
                'error': f'CoinGecko API error: {response.status_code}'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def fetch_rss_crypto_news():
    """Fetch news from free RSS feeds - always works, no API key needed"""
    import xml.etree.ElementTree as ET
    from datetime import datetime
    
    # Multiple RSS feeds for crypto news (all free, no rate limits)
    rss_feeds = [
        ('https://cointelegraph.com/rss', 'Cointelegraph'),
        ('https://bitcoinmagazine.com/.rss/full/', 'Bitcoin Magazine'),
        ('https://decrypt.co/feed', 'Decrypt'),
    ]
    
    all_news = []
    
    for feed_url, source_name in rss_feeds:
        try:
            response = requests.get(feed_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                # Handle both RSS and Atom feeds
                items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                
                for item in items[:5]:  # Get 5 from each feed
                    # RSS format
                    title = item.findtext('title', '')
                    link = item.findtext('link', '')
                    description = item.findtext('description', '')[:200] if item.findtext('description') else ''
                    pub_date = item.findtext('pubDate', '')
                    
                    # Atom format fallback
                    if not title:
                        title = item.findtext('{http://www.w3.org/2005/Atom}title', '')
                    if not link:
                        link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                        link = link_elem.get('href', '') if link_elem is not None else ''
                    
                    if title and link:
                        all_news.append({
                            'id': hash(link),
                            'title': title.strip(),
                            'description': description.strip()[:200],
                            'source': source_name,
                            'url': link,
                            'imageurl': '',
                            'published_at': pub_date,
                            'tags': '',
                            'categories': ['BTC', 'Crypto'],
                            'votes': {'upvotes': 0, 'downvotes': 0},
                            'lang': 'EN'
                        })
        except Exception as e:
            print(f"[RSS] Error fetching {source_name}: {e}")
            continue
    
    # Sort by title (as proxy for recency) and return top 10
    return all_news[:10]

@app.route('/news', methods=['GET'])
def get_crypto_news():
    """Get latest crypto news from RSS feeds (free, no rate limits)"""
    search_query = request.args.get('search', '')
    
    # Try CryptoCompare first (may be rate limited)
    try:
        base_url = "https://min-api.cryptocompare.com/data/v2/news/"
        params = {"lang": "EN"}
        
        if search_query:
            search_query_clean = search_query.strip().lower()
            currency_code = search_query.upper()
            for coin in COINS_LIST:
                if coin['id'] == search_query_clean or coin['name'].lower() == search_query_clean:
                    currency_code = coin['symbol'].upper()
                    break
            params['categories'] = currency_code
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if rate limited
            if data.get('Response') == 'Error' or not data.get('Data'):
                print("[NEWS] CryptoCompare rate limited, using RSS feeds...")
                raise Exception("Rate limited")
            
            news_data = data.get('Data', [])
            if isinstance(news_data, dict):
                news_data = list(news_data.values()) if news_data else []
            
            news_items = []
            for item in list(news_data)[:10]:
                categories_str = item.get('categories', '') or ''
                categories = categories_str.split('|')
                source_info = item.get('source_info') or {}
                source_name = source_info.get('name', item.get('source', 'Unknown'))
                
                news_items.append({
                    'id': item.get('id'),
                    'title': item.get('title', 'No title'),
                    'description': item.get('body', ''),
                    'source': source_name,
                    'url': item.get('url', ''),
                    'imageurl': item.get('imageurl', ''),
                    'published_at': item.get('published_on', ''),
                    'tags': item.get('tags', ''),
                    'categories': [cat.strip() for cat in categories if cat.strip()],
                    'votes': {
                        'upvotes': item.get('upvotes', 0),
                        'downvotes': item.get('downvotes', 0)
                    },
                    'lang': item.get('lang', 'EN')
                })
            
            if news_items:
                return jsonify({
                    'success': True,
                    'source': 'cryptocompare',
                    'search_query': search_query if search_query else None,
                    'count': len(news_items),
                    'news': news_items
                })
                
    except Exception as e:
        print(f"[NEWS] CryptoCompare failed: {e}")
    
    # Fallback to RSS feeds (always free, no rate limits)
    print("[NEWS] Using RSS feeds fallback...")
    rss_news = fetch_rss_crypto_news()
    
    if rss_news:
        # Filter by search query if provided
        if search_query:
            search_lower = search_query.lower()
            rss_news = [n for n in rss_news if search_lower in n['title'].lower()][:10]
        
        return jsonify({
            'success': True,
            'source': 'rss_feeds',
            'search_query': search_query if search_query else None,
            'count': len(rss_news),
            'news': rss_news
        })
    
    return jsonify({
        'success': False,
        'error': 'Unable to fetch news at this time',
        'news': []
    }), 503

    
# Newsletter Subscription Routes
@app.route('/api/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    """Subscribe a user to the newsletter"""
    try:
        data = request.json
        email = data.get('email')
        topics = data.get('topics', [])
        user_name = data.get('userName', 'User')
        
        print(f"Newsletter subscription request - Email: {email}, Topics: {topics}")
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not topics or len(topics) == 0:
            return jsonify({'error': 'At least one topic must be selected'}), 400
        
        # Subscribe via Brevo API
        result = subscribe_to_newsletter(email, topics, user_name)
        
        print(f"Newsletter subscription result: {result}")
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message'),
                'email': email,
                'topics': topics
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('message')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/newsletter/unsubscribe', methods=['POST'])
def newsletter_unsubscribe():
    """Unsubscribe a user from the newsletter"""
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        result = unsubscribe_from_newsletter(email)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('message')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/newsletter/topics/<email>', methods=['GET'])
def get_newsletter_topics(email):
    """Get user's subscribed topics"""
    try:
        print(f"Checking subscription for email: {email}")
        result = get_subscriber_info(email)
        print(f"Subscription check result: {result}")
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'email': email,
                'topics': result.get('topics', []),
                'name': result.get('name', 'User')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('message'),
                'topics': []
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'topics': []
        }), 500


@app.route('/api/newsletter/topics/update', methods=['POST'])
def update_newsletter_topics():
    """Update user's newsletter topics (supports both merge and replace modes)"""
    try:
        data = request.json
        email = data.get('email')
        new_topics = data.get('topics', [])
        user_name = data.get('userName', 'User')
        mode = data.get('mode', 'replace')  # 'merge' or 'replace' (default: replace)
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not new_topics or len(new_topics) == 0:
            return jsonify({'error': 'At least one topic must be provided'}), 400
        
        result = update_subscriber_topics(email, new_topics, user_name, mode)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message'),
                'email': email,
                'topics': result.get('topics', [])
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('message')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    print("Using Groq AI with Llama 3.3 70B model")
    app.run(debug=True, port=5000)
