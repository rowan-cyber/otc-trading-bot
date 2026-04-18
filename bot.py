import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import PIL.Image
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """You are an expert Pocket Option OTC trading advisor. You specialize in OTC binary/digital options on Pocket Option platform.

OTC CONTEXT:
- OTC markets run 24/7 including weekends, they are synthetic/simulated pairs
- Common OTC pairs: EUR/USD OTC, GBP/USD OTC, AUD/USD OTC, USD/JPY OTC, BTC/USD OTC, EUR/JPY OTC
- Fixed expiry times: 60s, 2m, 3m, 5m, 15m, 30m, 1h
- Payout: 70-92% on wins, 100% loss on losses

YOU HELP WITH:
1. Signals: UP or DOWN calls with pair, expiry, confidence, reasoning
2. Patterns: pin bars, engulfing candles, S/R bounces, trend continuation
3. Indicators: RSI, MACD, Bollinger Bands, stochastic, moving averages
4. Risk management: 1-5% per trade max, position sizing, when to stop
5. Expiry selection: M1 chart = 60-120s, M5 = 5-15m, M15 = 15-30m

SIGNAL FORMAT (always use this when giving signals):
📊 Pair: [name]
📈 Direction: UP ⬆️ or DOWN ⬇️
⏱ Expiry: [time]
🎯 Confidence: Low / Medium / High
💡 Reason: [2-3 sentences]
⚠️ Risk: [1 sentence]

Rules:
- Be direct and practical
- Short paragraphs, no bullet dashes
- Always note this is analysis not guaranteed profit
- Warn about OTC synthetic pricing risks
- Keep responses under 200 words unless deep explanation needed
- Use emojis to make messages readable on Telegram"""

user_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to your *Pocket Option OTC Advisor!*\n\n"
        "I can help you with:\n"
        "📊 Live signals for OTC pairs\n"
        "📈 Chart pattern analysis\n"
        "💰 Risk management advice\n"
        "⏱ Expiry time selection\n\n"
        "Just ask me anything or send a screenshot of your chart!\n\n"
        "Try: _Give me a signal for EUR/USD OTC on M1_",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *OTC Advisor Commands*\n\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/signal EUR/USD - Quick signal for a pair\n"
        "/risk - Risk management tips\n"
        "/clear - Clear conversation history\n\n"
        "Or just type any question naturally!\n"
        "You can also send chart screenshots 📸",
        parse_mode="Markdown"
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("🔄 Conversation cleared! Starting fresh.")

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = " ".join(context.args) if context.args else "EUR/USD OTC"
    await handle_query(update, context, f"Give me a signal for {pair} right now on M1 timeframe")

async def risk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_query(update, context, "Give me the most important risk management rules for Pocket Option OTC trading")

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    user_id = update.effective_user.id
    if user_id not in user_histories:
        user_histories[user_id] = []

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        user_histories[user_id].append(text)
        if len(user_histories[user_id]) > 10:
            user_histories[user_id] = user_histories[user_id][-10:]

        history_text = "\n".join(user_histories[user_id][-6:])
        full_prompt = f"{SYSTEM_PROMPT}\n\nConversation so far:\n{history_text}\n\nRespond to the last message."

        response = model.generate_content(full_prompt)
        reply = response.text

        user_histories[user_id].append(f"Assistant: {reply}")
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Something went wrong. Please try again.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_query(update, context, f"User: {update.message.text}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()

        image = PIL.Image.open(io.BytesIO(file_bytes))
        caption = update.message.caption or "Analyze this chart and give me a trading signal."

        prompt = f"{SYSTEM_PROMPT}\n\n{caption}\n\nLook at this chart carefully and give a clear UP or DOWN signal with expiry, confidence level, and reasoning."

        response = model.generate_content([prompt, image])
        reply = response.text

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Photo error: {e}")
        await update.message.reply_text("⚠️ Could not analyze the chart. Please try again.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("risk", risk_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
