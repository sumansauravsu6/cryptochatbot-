# Crypto Chatbot UI

A beautiful React.js chatbot interface with dark/light theme and session management for cryptocurrency and currency exchange queries.

## Features

- 🎨 **Beautiful UI** - Modern, responsive design
- 🌓 **Theme Toggle** - Switch between light and dark modes
- 💾 **Session Storage** - Saves all your chat history (like ChatGPT)
- 📊 **Real-time Data** - Cryptocurrency prices and exchange rates
- 📈 **Graph Support** - Visual charts for data
- 🔄 **Multi-chat** - Create and manage multiple chat sessions

## Setup Instructions

### 1. Install React Dependencies

```bash
cd chatbot-ui
npm install
```

### 2. Install Python Dependencies

```bash
pip install flask flask-cors
```

### 3. Start the Backend Server

In the main project folder:

```bash
python flask_server.py
```

The Flask server will start on `http://localhost:5000`

### 4. Start the React App

In the `chatbot-ui` folder:

```bash
npm start
```

The React app will open at `http://localhost:3000`

### 5. Make Sure Ollama is Running

```bash
ollama serve
```

## Usage

1. Type your question in the input field
2. Ask about:
   - Cryptocurrency prices (Bitcoin, Ethereum, XRP, etc.)
   - Exchange rates (USD to EUR, GBP to INR, etc.)
   - Historical data (last 7 days, last 15 days, etc.)
   - Comparisons (compare Bitcoin vs Ethereum)

3. Use the sidebar to:
   - Create new chats
   - Switch between conversations
   - Delete old chats
   - Toggle theme (light/dark mode)

## Example Queries

- "What is the price of Bitcoin in USD?"
- "Compare XRP and Zcash"
- "USD to EUR exchange rate for last 7 days"
- "Compare USD to INR and USD to JPY"
- "What is the exchange rate from pound to INR?"

## Architecture

- **Frontend**: React.js with Context API for state management
- **Backend**: Flask server connecting to your Python chatbot
- **AI**: Ollama (qwen2.5:3b) for natural language processing
- **APIs**: CoinGecko (crypto) and ExchangeRate.host (currency)

## Storage

All chat sessions are stored in browser's localStorage, so your conversations persist across page refreshes!
