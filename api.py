# api.py

from fastapi import FastAPI
from threading import Thread
from bot import TradingBot

app = FastAPI(title="Trade Analista IA - Bot Demo")

bot = TradingBot()
bot_thread: Thread | None = None


@app.get("/")
def root():
    return {"message": "API do Trade Analista IA online"}


@app.get("/status")
def status():
    return {
        "is_running": bot.is_running,
        "last_equity": bot.last_equity,
        "last_pnl": bot.last_pnl,
    }


@app.post("/start")
def start_bot():
    global bot_thread

    if bot.is_running:
        return {"status": "already_running"}

    def run():
        bot.start()

    bot_thread = Thread(target=run, daemon=True)
    bot_thread.start()

    return {"status": "started"}


@app.post("/stop")
def stop_bot():
    if not bot.is_running:
        return {"status": "already_stopped"}

    bot.stop()
    return {"status": "stopping"}
