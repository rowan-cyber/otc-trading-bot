# Pocket Option OTC Telegram Bot

An AI-powered trading advisor bot for Pocket Option OTC markets, built with Claude AI.

## Features
- UP/DOWN signals for any OTC pair
- Chart screenshot analysis (send a photo!)
- Risk management advice
- Remembers conversation context
- Commands: /signal, /risk, /clear, /help

## Deploy on Railway

### Step 1 — Upload to GitHub
1. Create a free account at github.com
2. Create a new repository (call it `otc-trading-bot`)
3. Upload all 4 files: bot.py, requirements.txt, Procfile, README.md

### Step 2 — Deploy on Railway
1. Go to railway.app and sign up free
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `otc-trading-bot` repo
4. Railway will detect it automatically

### Step 3 — Add Environment Variables
In Railway dashboard → your project → "Variables" tab, add:

TELEGRAM_TOKEN = your_telegram_bot_token_here
ANTHROPIC_API_KEY = your_anthropic_api_key_here

### Step 4 — Get your Anthropic API Key
1. Go to console.anthropic.com
2. Sign up / log in
3. Go to "API Keys" → "Create Key"
4. Copy it and paste into Railway Variables

### Step 5 — Deploy
Click "Deploy" — Railway will build and start your bot in ~2 minutes.

## How to Use the Bot
- /start — Welcome message
- /signal EUR/USD — Get a signal for any pair
- /risk — Risk management tips
- /clear — Reset conversation
- Send any message — Ask anything about OTC trading
- Send a chart screenshot — Bot will analyze it and give a signal!

## Pairs Supported
EUR/USD OTC, GBP/USD OTC, AUD/USD OTC, USD/JPY OTC, BTC/USD OTC, EUR/JPY OTC, and more.
