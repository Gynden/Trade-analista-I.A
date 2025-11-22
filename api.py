# api.py

from pathlib import Path
from threading import Thread

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from bot import TradingBot

app = FastAPI(title="Trade Analista IA - Bot Demo")

bot = TradingBot()
bot_thread: Thread | None = None


# ---------- FRONTEND ----------


@app.get("/", response_class=HTMLResponse)
def root():
    index_path = Path("index.html")
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>Painel não encontrado</h1>", status_code=500)


# ---------- API BOT ----------


@app.get("/status")
def status():
    rm = bot.risk_manager

    return {
        "is_running": bot.is_running,
        "last_equity": bot.last_equity,
        "last_pnl": bot.last_pnl,
        "daily_target": rm.daily_target,
        "daily_stop_loss": rm.daily_stop_loss,
        "target_pct": rm.target_pct,
        "stop_pct": rm.stop_pct,
        "strategy_stats": bot.strategy_stats,
    }


@app.get("/history")
def history():
    return JSONResponse({"trades": bot.trades})


@app.get("/brain")
def brain():
    """Placar das estratégias."""
    return {
        "strategy_stats": bot.strategy_stats
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
