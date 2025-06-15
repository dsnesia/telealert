import os
import asyncio
import logging
import aiohttp
from telegram import Bot
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
alerts = {}

bot = Bot(token=TOKEN)

async def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}USDT"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return float(data['price'])

async def price_monitor():
    while True:
        for coin, target in list(alerts.items()):
            price = await get_price(coin)
            if (price >= target):
                await bot.send_message(chat_id=CHAT_ID, text=f"🚨 {coin.upper()} naik menyentuh {price:.6f} (Target: {target})")
                del alerts[coin]
        await asyncio.sleep(60)

async def start(update, context):
    await update.message.reply_text("✅ Bot aktif! Gunakan /alert <coin> <harga> untuk set alert.")

async def alert(update, context):
    coin = context.args[0]
    harga = float(context.args[1])
    alerts[coin.lower()] = harga
    await update.message.reply_text(f"📡 Alert disimpan: {coin.upper()} ke {harga}")

async def cek(update, context):
    coin = context.args[0]
    price = await get_price(coin)
    await update.message.reply_text(f"💹 Harga {coin.upper()} sekarang: {price:.6f}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("alert", alert))
    app.add_handler(CommandHandler("cek", cek))
    loop = asyncio.get_event_loop()
    loop.create_task(price_monitor())
    app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
  
