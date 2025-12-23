import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import json,os

# Load coin list for ID lookup
def load_coin_list():
    try:
        with open('coins.json', 'r') as f:
            return json.load(f)
    except:
        return []

COINS_LIST = load_coin_list()

def find_coin_id(coin_name):
    """Find the correct coin ID from coins.json by searching name, symbol, or id"""
    coin_name_lower = coin_name.lower().strip()
    
    # First, try exact match on id
    for coin in COINS_LIST:
        if coin['id'] == coin_name_lower:
            return coin['id']
    
    # Then try exact match on symbol
    for coin in COINS_LIST:
        if coin['symbol'].lower() == coin_name_lower:
            return coin['id']
    
    # Then try exact match on name
    for coin in COINS_LIST:
        if coin['name'].lower() == coin_name_lower:
            return coin['id']
    
    # Finally, try partial match on name or symbol
    for coin in COINS_LIST:
        if coin_name_lower in coin['name'].lower() or coin_name_lower in coin['symbol'].lower():
            return coin['id']
    
    # If not found, return the original input
    return coin_name_lower

def greet(name):
    return f"Hello, {name}!"

def get_crypto_global_market_data():
    url = "https://api.coingecko.com/api/v3/global"

    headers = {"x-cg-demo-api-key": "CG-bm1iokxRmUk2d17v5EamRWso"}
    response = requests.get(url, headers=headers)
    
    return response.json()


def get_coin_price(vs_currency: str="inr", coin_id: str = "bitcoin"):
    # Resolve coin_id using coins.json
    resolved_id = find_coin_id(coin_id)
    url = f"https://api.coingecko.com/api/v3/simple/price?vs_currencies={vs_currency}&ids={resolved_id}"

    headers = {"x-cg-demo-api-key": "CG-bm1iokxRmUk2d17v5EamRWso"}
    response = requests.get(url, headers=headers)
    
    return response.json()


def get_exchange_rate(from_currency: str = "USD", to_currency: str = "EUR"):
    """Get exchange rate between two currencies by converting 1 unit"""
    url = "https://api.exchangerate.host/convert"
    params = {
        "from": from_currency,
        "to": to_currency,
        "amount": 1,
        "access_key": "686b242c0505e671eeac38e561b169a6"
    }
    response = requests.get(url, params=params)
    return response.json()

def get_exchange_rate_for_time_period(from_currency: str, to_currency: str, start_date: str, end_date: str):
    """Get exchange rates between two currencies for a specific time period"""
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

def create_graph(data_dict):
    """Create and display graphs from API data"""
    try:
        # Handle list of results (for comparisons)
        if isinstance(data_dict, list) and len(data_dict) > 1:
            # Try to create a comparison bar chart
            labels = []
            values = []
            
            for item in data_dict:
                if isinstance(item, dict):
                    # Extract coin price comparisons
                    for coin, data in item.items():
                        if isinstance(data, dict) and 'usd' in data:
                            labels.append(coin.capitalize())
                            values.append(data['usd'])
                    
                    # Extract exchange rate comparisons
                    if 'query' in item and 'result' in item:
                        query = item['query']
                        from_curr = query.get('from', '')
                        to_curr = query.get('to', '')
                        rate = item.get('result', 0)
                        labels.append(f"{from_curr} to {to_curr}")
                        values.append(rate)
            
            if labels and values:
                plt.figure(figsize=(10, 6))
                colors = plt.cm.viridis(range(len(labels)))
                bars = plt.bar(labels, values, color=colors, edgecolor='black', linewidth=1.5)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:,.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
                
                # Check if this is crypto or exchange rate comparison
                if any('to' in label for label in labels):
                    plt.xlabel('Currency Pair', fontsize=12, fontweight='bold')
                    plt.ylabel('Exchange Rate', fontsize=12, fontweight='bold')
                    plt.title('Exchange Rate Comparison', fontsize=14, fontweight='bold')
                    plt.savefig('exchange_rate_comparison.png', dpi=300, bbox_inches='tight')
                    graph_file = 'exchange_rate_comparison.png'
                else:
                    plt.xlabel('Cryptocurrency', fontsize=12, fontweight='bold')
                    plt.ylabel('Price (USD)', fontsize=12, fontweight='bold')
                    plt.title('Cryptocurrency Price Comparison', fontsize=14, fontweight='bold')
                    plt.savefig('crypto_comparison.png', dpi=300, bbox_inches='tight')
                    graph_file = 'crypto_comparison.png'
                
                plt.grid(True, alpha=0.3, linestyle='--', axis='y')
                plt.tight_layout()
                plt.show()
                return f"Graph saved as '{graph_file}'"
        
        # Check for crypto market dominance data
        if "market_cap_percentage" in str(data_dict):
            market_data = data_dict.get("data", {})
            market_cap_pct = market_data.get("market_cap_percentage", {})
            
            if market_cap_pct:
                coins = [coin.upper() for coin in list(market_cap_pct.keys())]
                percentages = list(market_cap_pct.values())
                
                plt.figure(figsize=(10, 6))
                colors = plt.cm.Set3(range(len(coins)))
                plt.pie(percentages, labels=coins, autopct='%1.1f%%', startangle=90, colors=colors)
                plt.title('Cryptocurrency Market Dominance', fontsize=14, fontweight='bold')
                plt.axis('equal')
                plt.tight_layout()
                plt.savefig('crypto_market_dominance.png', dpi=300, bbox_inches='tight')
                plt.show()
                return "Graph saved as 'crypto_market_dominance.png'"
        
        # Check for time series exchange rate data
        elif "quotes" in data_dict and isinstance(data_dict.get("quotes"), dict):
            quotes = data_dict.get("quotes", {})
            all_dates = sorted(quotes.keys())
            
            # Filter dates to only include those within the requested range
            start_date = data_dict.get("start_date", "")
            end_date = data_dict.get("end_date", "")
            
            if start_date and end_date:
                # Only include dates within the requested range
                dates = [date for date in all_dates if start_date <= date <= end_date]
            else:
                dates = all_dates
            
            values = [list(quotes[date].values())[0] for date in dates]
            source = data_dict.get("source", "")
            
            # Get target currency from first quote
            if dates and quotes[dates[0]]:
                target = list(quotes[dates[0]].keys())[0].replace(source, "")
            else:
                target = ""
            
            plt.figure(figsize=(12, 6))
            plt.plot(dates, values, marker='o', linestyle='-', linewidth=2, markersize=6, color='#2E86AB')
            plt.xlabel('Date', fontsize=12, fontweight='bold')
            plt.ylabel(f'Exchange Rate ({source} to {target})', fontsize=12, fontweight='bold')
            plt.title(f'{source} to {target} Exchange Rate Trend', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            plt.savefig('exchange_rate_trend.png', dpi=300, bbox_inches='tight')
            plt.show()
            return "Graph saved as 'exchange_rate_trend.png'"
        
        return None
    except Exception as e:
        return f"Error creating graph: {e}"

# Define available tools for function execution
tools = {
    "greet": greet,
    "get_crypto_global_market_data": get_crypto_global_market_data,
    "get_coin_price": get_coin_price,
    "get_exchange_rate": get_exchange_rate,
    "convert_currency": convert_currency,
    "get_exchange_rate_for_time_period": get_exchange_rate_for_time_period
}

user_input = input("Enter your question: ")

# API Configuration from environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_URL = os.getenv('GROQ_URL', 'https://api.groq.com/openai/v1/chat/completions')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')
EXCHANGERATE_API_KEY = os.getenv('EXCHANGERATE_API_KEY')
TIMEOUT = 60


coins = requests.get("https://api.coingecko.com/api/v3/coins/list").json()

# Get today's date for context
today = datetime.now().strftime("%Y-%m-%d")
days_15_ago = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")

prompt = f"""You are a helpful assistant that provides cryptocurrency and currency exchange information.

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
1. get_crypto_global_market_data() - Returns global cryptocurrency market data.
2. get_coin_price(vs_currency: str="inr", coin_id: str = "bitcoin") - Returns the price of a specific cryptocurrency in a given currency.
3. get_exchange_rate(from_currency: str = "USD", to_currency: str = "EUR") - Get latest exchange rate between two currencies.
4. convert_currency(from_currency: str, to_currency: str, amount: float) - Convert an amount from one currency to another.
5. greet(name) - Returns a greeting message for the given name.
6. get_exchange_rate_for_time_period(from_currency: str, to_currency: str, start_date: str, end_date: str) - Get exchange rates for a date range. Dates must be in YYYY-MM-DD format.

User question: "{user_input}"

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

When calculating dates for time period queries:
- "last 15 days" means from {days_15_ago} to {today}
- "last 7 days" means calculate 7 days before today
- "last month" means calculate 30 days before today
- Always use YYYY-MM-DD format
- Example: "INR to USD for last 15 days" -> FUNCTION_CALL: get_exchange_rate_for_time_period("INR", "USD", "{days_15_ago}", "{today}")

IMPORTANT: Use get_exchange_rate() for CURRENT rates. Only use get_exchange_rate_for_time_period() when user explicitly asks for historical data or mentions "last X days/weeks".
"""
payload = {
    "model": GROQ_MODEL,
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.7,
    "max_tokens": 1024
}
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}
resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=TIMEOUT)
resp.raise_for_status()
data = resp.json()
response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
print(f"\nLLM Response: {response_text}\n")

# Check if response contains a function call
if "FUNCTION_CALL:" in response_text:
    # Extract ALL function calls (support multiple)
    function_calls = []
    for line in response_text.split('\n'):
        if "FUNCTION_CALL:" in line:
            func_call = line.split("FUNCTION_CALL:")[-1].strip()
            if func_call:
                function_calls.append(func_call)
    
    # If only one function call on the line, use the old method
    if len(function_calls) == 0:
        function_calls = [response_text.split("FUNCTION_CALL:")[-1].strip()]
    
    print(f"Found {len(function_calls)} function call(s) to execute\n")
    
    all_results = []
    try:
        for i, function_call in enumerate(function_calls, 1):
            print(f"[{i}/{len(function_calls)}] Executing: {function_call}")
            
            # Safely evaluate the function call with available tools
            result = eval(function_call, {"__builtins__": {}}, tools)
            
            # If this is a time period query, add the date parameters to the result for graphing
            if "get_exchange_rate_for_time_period" in function_call and isinstance(result, dict):
                # Extract start_date and end_date from the function call
                import re
                match = re.search(r'get_exchange_rate_for_time_period\([^,]+,\s*[^,]+,\s*"([^"]+)",\s*"([^"]+)"\)', function_call)
                if match:
                    result['start_date'] = match.group(1)
                    result['end_date'] = match.group(2)
            
            all_results.append(result)
            
            print(f"\n{'='*50}")
            print(f"Function Result #{i}:")
            print(f"{'='*50}")
            
            # Pretty print the raw result
            if isinstance(result, dict):
                result_str = json.dumps(result, indent=2)
                print(result_str)
            else:
                result_str = str(result)
                print(result_str)
            print()
        
        # Combine all results for the LLM
        if len(all_results) == 1:
            combined_result_str = json.dumps(all_results[0], indent=2) if isinstance(all_results[0], dict) else str(all_results[0])
        else:
            combined_result_str = json.dumps(all_results, indent=2)
        
        # Ask LLM if this data should be visualized
        print(f"{'='*50}")
        print("Asking LLM if data should be visualized...")
        print(f"{'='*50}\n")
        
        visualization_prompt = f"""You are a data visualization expert. Analyze this data and determine if it would benefit from graphical visualization.

User's question: "{user_input}"

Data received:
{combined_result_str}

Should this data be visualized as a graph? Consider:
- Time series data (multiple dates) -> good for line graphs
- Market share/dominance data (percentages, market caps) -> good for pie charts
- Comparison data (comparing 2+ items with numerical values) -> good for bar charts
- Single values or simple conversions -> NO graph needed

Respond with ONLY one of these:
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
            print(f"LLM Decision: {viz_decision}\n")
            
            # Create graph based on LLM's decision
            if "GRAPH: YES" in viz_decision:
                # For comparisons with multiple results, pass all results together
                if "COMPARISON" in viz_decision and len(all_results) > 1:
                    graph_result = create_graph(all_results)
                    if graph_result and "saved" in graph_result.lower():
                        print(f"📊 {graph_result}")
                else:
                    # For single results or time series, graph each individually
                    for result in all_results:
                        graph_result = create_graph(result)
                        if graph_result and "saved" in graph_result.lower():
                            print(f"📊 {graph_result}")
                print()
        except Exception as e:
            print(f"Visualization check failed: {e}")
            print("Proceeding without graph...\n")
        
        # Send the result back to LLM for natural language response
        prompt2 = f"""You are a helpful assistant. The user asked: "{user_input}"

I called {len(function_calls)} function(s) and got this data:
{combined_result_str}

Please provide a clear, concise, and natural language answer to the user's question based on this data. 
If there are multiple results, compare them or provide a comprehensive answer.
Make it friendly and easy to understand. Extract the most relevant information."""
        
        payload2 = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt2}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        print(f"\n{'='*50}")
        print("Generating natural language response...")
        print(f"{'='*50}\n")
        
        resp2 = requests.post(GROQ_URL, json=payload2, headers=headers, timeout=TIMEOUT)
        resp2.raise_for_status()
        data2 = resp2.json()
        final_response = data2.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        print(f"Answer: {final_response}\n")

    except Exception as e:
        print(f"Error executing function: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No function call needed - this is a direct response.")

       