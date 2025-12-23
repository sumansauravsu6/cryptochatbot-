# Crypto & Currency Chatbot

A full-stack AI-powered chatbot for cryptocurrency and currency exchange information with interactive visualizations.

## Features

- 🤖 **AI-Powered**: Uses Groq AI with Llama 3.3 70B model for intelligent responses
- 💰 **Real-time Data**: Cryptocurrency prices from CoinGecko API and exchange rates from ExchangeRate.host
- 📊 **Interactive Graphs**: Automatic visualization of comparisons and time series data
- 🔥 **Trending Dashboard**: View trending coins, NFTs, and categories in real-time
- 🎨 **Modern UI**: React-based interface with dark/light mode
- 💾 **Session Management**: Save and manage multiple chat sessions
- 📝 **Formatted Responses**: Clean bullet-point responses for better readability

## Prerequisites

- Python 3.8+
- Node.js 14+
- pip (Python package manager)
- npm (Node package manager)

## Installation

### 1. Clone the repository

```bash
cd "path/to/poc project"
```

### 2. Set up environment variables

Create a `.env` file in the root directory:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here
EXCHANGERATE_API_KEY=your_exchangerate_api_key_here

# API URLs (optional, defaults provided)
GROQ_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Install Python dependencies

```bash
pip install flask flask-cors requests matplotlib python-dotenv
```

### 4. Install Node dependencies

```bash
cd chatbot-ui
npm install
cd ..
```

## Running the Application

### Start the Flask Backend

```bash
python flask_server.py
```

The backend will start on `http://localhost:5000`

### Start the React Frontend

In a new terminal:

```bash
cd chatbot-ui
npm start
```

The frontend will open automatically at `http://localhost:3000`

## Usage

### Console Version

Run the console-based chatbot:

```bash
python toll_calling.py
```

### Web Interface

1. Open `http://localhost:3000` in your browser
2. Type your question in the input box
3. Click the **Dashboard** button (top-right) to view trending data
4. Examples:
   - "Compare Bitcoin and Ethereum"
   - "What's the exchange rate from USD to EUR?"
   - "Show me USD to INR for the last 7 days"
   - "What are the top 3 cryptocurrencies?"

### Dashboard Features

The Trending Dashboard shows:
- **Trending Coins**: Top 6 trending cryptocurrencies with prices and market data
- **Trending NFTs**: Popular NFT collections with floor prices and 24h changes
- **Trending Categories**: Top 10 trending crypto categories with market cap data

Click the Dashboard button in the header to open it anytime!

## API Keys

### Getting API Keys

1. **Groq API**: Sign up at [console.groq.com](https://console.groq.com)
2. **CoinGecko API**: Get your key at [coingecko.com/api](https://www.coingecko.com/api)
3. **ExchangeRate.host**: Register at [exchangerate.host](https://exchangerate.host)

### Security

- Never commit your `.env` file to version control
- The `.gitignore` file is already configured to exclude `.env`
- Keep your API keys private

## Project Structure

```
poc project/
├── .env                    # Environment variables (create this)
├── .gitignore             # Git ignore rules
├── flask_server.py        # Flask backend server
├── toll_calling.py        # Console chatbot
├── coins.json             # Cryptocurrency database
├── chatbot-ui/            # React frontend
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── ChatInterface.js
│   │   │   └── Sidebar.js
│   │   └── context/
│   │       ├── ThemeContext.js
│   │       └── SessionContext.js
│   └── package.json
└── README.md
```

## Features in Detail

### Intelligent Function Calling

The chatbot automatically:
- Detects when to call APIs for data
- Handles multiple function calls for comparisons
- Decides when to generate graphs
- Formats responses in bullet points

### Interactive Graphs

- **Comparison Graphs**: Bar charts for comparing cryptocurrencies or exchange rates
- **Time Series**: Line graphs for historical data
- **Market Share**: Pie charts for market dominance
- **Actions**: Zoom, download, and view in modal

### Session Management

- Create multiple chat sessions
- Switch between sessions
- Delete old sessions
- All sessions persist in browser localStorage

## Troubleshooting

### "Module not found" errors

Install missing dependencies:
```bash
pip install -r requirements.txt
```

### "Port already in use"

Kill the process using the port:
```bash
# Windows PowerShell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force
```

### API Errors

- Check your `.env` file has valid API keys
- Ensure `python-dotenv` is installed
- Verify API keys are not expired

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
