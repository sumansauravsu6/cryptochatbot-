import requests
import re
import json
import sys
from typing import Optional

# === CONFIG ===
OLLAMA_URL = "http://localhost:11434/api/generate"   # change if your Ollama runs elsewhere
OLLAMA_MODEL = "qwen2.5:3b"                     # change to your installed model name
ALLOWED_API_HOST = "api.frankfurter.dev"        # only allow Frankfurter API returned by model
TIMEOUT = 60

# === Strict system prompt to force model to output EXACTLY one URL ===
SYSTEM_PROMPT = """
You are an assistant that *must* parse a user's request about currency exchange rates
and produce EXACTLY ONE runnable URL (and nothing else) pointing to the Frankfurter API.
The model should not emit any extra commentary, JSON, or explanation — only the single URL string.

Rules:
1. If the user asked for a historical date (any YYYY-MM-DD or phrasing like "on Jan 5 2024", "on 2024-01-05", "on 5 Jan 2024"),
   return the URL using the date path: https://api.frankfurter.dev/v1/YYYY-MM-DD
   Example: https://api.frankfurter.dev/v1/2024-01-01?from=USD&to=EUR

2. If the user did NOT specify a date, return the latest endpoint:
   https://api.frankfurter.dev/v1/latest?from=BASE&to=SYMBOLS
   If 'to' (target currency) is not specified by the user, omit the 'to' parameter (the API will return all rates).
   If 'from' (base) is not specified, default base to USD.

3. Use query parameter names exactly: 'from' and 'to'. (Example:
   https://api.frankfurter.dev/v1/latest?from=USD&to=EUR)

4. Allowed currencies: assume the user may use currency codes like USD, EUR, INR, JPY, GBP, etc.
   Normalize extracted codes to uppercase.

5. Output MUST be the single URL only, with no surrounding ticks, code blocks, or whitespace lines.
   If you cannot parse the user's request, produce a URL defaulting to latest with base=USD and no 'to' (i.e. all rates):
   https://api.frankfurter.dev/v1/latest?from=USD

6. Do NOT call any external API yourself — only output the URL string.

Examples of correct outputs (single-line only):
https://api.frankfurter.dev/v1/2024-01-01?from=USD&to=EUR
https://api.frankfurter.dev/v1/latest?from=INR&to=USD
https://api.frankfurter.dev/v1/latest?from=USD

Remember: EXACTLY ONE URL string, nothing else.
"""

# Helper: call Ollama generate endpoint with system prompt + user message
def ask_ollama_return_url(user_text: str) -> str:
    full_prompt = SYSTEM_PROMPT + "\n\nUser request: " + user_text
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    # Ollama's /api/generate returns {"response": "..."}
    url_candidate = data.get("response", "").strip()
    
    # Handle multiple URLs (one per line)
    urls = [line.strip() for line in url_candidate.split('\n') if line.strip()]
    return urls

# Validate that returned string is a safe Frankfurter API URL
def validate_frankfurter_url(url: str) -> Optional[str]:
    # Allow only https and the ALLOWED_API_HOST
    # Accept both /v1/latest and /v1/YYYY-MM-DD
    pattern = rf"^https?://{re.escape(ALLOWED_API_HOST)}/v1(?:/latest|/\d{{4}}-\d{{2}}-\d{{2}})(?:\?.*)?$"
    if re.match(pattern, url):
        return url
    return None

# Run the validated URL and return JSON
def fetch_url_json(url: str):
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

# Send API response to LLM for natural language explanation
def ask_ollama_for_explanation(user_query: str, api_responses: list) -> str:
    # Format multiple API responses for the LLM
    if len(api_responses) == 1:
        response_text = json.dumps(api_responses[0], indent=2)
    else:
        response_text = "\n\n".join([f"Response {i+1}:\n{json.dumps(resp, indent=2)}" 
                                      for i, resp in enumerate(api_responses)])
    
    prompt = f"""You are a helpful assistant. The user asked: "{user_query}"

I called an exchange rate API and got this response:
{response_text}

Please provide a clear, natural language explanation of this data that directly answers the user's question. Be concise and friendly."""
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "").strip()

# CLI usage: python ollama_rate_url_runner.py "what's USD to EUR on 2024-01-01?"
def main():
    if len(sys.argv) < 2:
        print("Usage: python ollama_rate_url_runner.py \"<user question>\"")
        sys.exit(1)

    user_input = sys.argv[1]
    try:
        urls = ask_ollama_return_url(user_input)
    except Exception as e:
        print(f"Error calling Ollama: {e}", file=sys.stderr)
        sys.exit(2)

    # Validate all URLs
    valid_urls = []
    for url_str in urls:
        valid_url = validate_frankfurter_url(url_str)
        if valid_url:
            valid_urls.append(valid_url)
        else:
            print(f"Warning: Invalid URL ignored: {url_str}", file=sys.stderr)
    
    if not valid_urls:
        print("No valid Frankfurter API URLs found. Output was:")
        print('\n'.join(urls))
        sys.exit(3)

    # Fetch the exchange rate data for all URLs
    results = []
    try:
        for url in valid_urls:
            result = fetch_url_json(url)
            results.append(result)
    except Exception as e:
        print(f"Error fetching the URL: {e}", file=sys.stderr)
        sys.exit(4)

    # Send to LLM for natural language explanation
    try:
        explanation = ask_ollama_for_explanation(user_input, results)
        print(explanation)
    except Exception as e:
        print(f"Error getting explanation from Ollama: {e}", file=sys.stderr)
        # Fallback: print the raw JSON
        for i, result in enumerate(results):
            if len(results) > 1:
                print(f"\nResult {i+1}:")
            print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
