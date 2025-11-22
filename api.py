# api.py

from threading import Thread
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from bot import TradingBot

app = FastAPI(title="Trade Analista IA - Bot Demo")

bot = TradingBot()
bot_thread: Thread | None = None


# ---------- FRONTEND (index.html) ----------


@app.get("/", response_class=HTMLResponse)
def root():
    """
    Retorna o painel HTML.
    """
    index_path = Path("index.html")
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>Painel não encontrado</h1>", status_code=500)


# ---------- API DO BOT ----------


@app.get("/status")
def status():
    """
    Status básico do bot + metas de risco.
    """
    rm = bot.risk_manager

    return {
        "is_running": bot.is_running,
        "last_equity": bot.last_equity,
        "last_pnl": bot.last_pnl,
        "daily_target": rm.daily_target,
        "daily_stop_loss": rm.daily_stop_loss,
        "target_pct": rm.target_pct,
        "stop_pct": rm.stop_pct,
    }


@app.get("/history")
def history():
    """
    Histórico simples das últimas operações.
    """
    return JSONResponse({"trades": bot.trades})


@app.post("/start")
def start_bot():
    """
    Inicia o bot em uma thread separada.
    """
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
    """
    Para o bot (se estiver rodando).
    """
    if not bot.is_running:
        return {"status": "already_stopped"}

    bot.stop()
    return {"status": "stopping"}
