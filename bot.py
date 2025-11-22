# bot.py

import time
from datetime import datetime

from config import (
    API_KEY,
    API_SECRET,
    SYMBOL,
    TIMEFRAME_MINUTES,
    DAILY_TARGET_PCT,
    DAILY_STOP_PCT,
    POSITION_SIZE,
    LOOP_SLEEP_SECONDS,
)
from broker_client import BrokerClient
from strategy import choose_best_signal
from risk_manager import RiskManager


class TradingBot:
    def __init__(self):
        self.broker = BrokerClient(API_KEY, API_SECRET)
        self.risk_manager = RiskManager(DAILY_TARGET_PCT, DAILY_STOP_PCT)

        self.is_running: bool = False
        self.last_equity: float | None = None

        # 🔹 PnL exibido no painel (apenas operações fechadas)
        self.last_pnl: float | None = None
        self.realized_pnl: float = 0.0  # acumulador de PnL realizado do dia

        # histórico das operações
        self.trades: list[dict] = []

        # desempenho por estratégia: {nome: {"trades": int, "pnl": float}}
        self.strategy_stats: dict[str, dict] = {}

    # ---------- aprendizado / histórico ----------

    def _register_strategy_pnl(self, strategy_name: str, closed_pnl: float | None):
        if not strategy_name or strategy_name == "none" or closed_pnl is None:
            return

        stats = self.strategy_stats.setdefault(
            strategy_name, {"trades": 0, "pnl": 0.0}
        )
        stats["trades"] += 1
        stats["pnl"] += closed_pnl

    def _add_trade(self, order_result: dict, strategy_name: str):
        if order_result.get("status") != "filled":
            return

        trade = {
            "time": order_result.get("time"),
            "symbol": order_result.get("symbol"),
            "side": order_result.get("order_type"),  # BUY / SELL
            "qty": order_result.get("qty"),
            "price": order_result.get("price"),
            "closed_pnl": order_result.get("closed_pnl"),
            "strategy": strategy_name,
        }

        self.trades.append(trade)
        if len(self.trades) > 100:
            self.trades = self.trades[-100:]

        # 🔹 soma PnL realizado do dia
        if trade["closed_pnl"] is not None:
            self.realized_pnl += trade["closed_pnl"]

        # atualiza placar da estratégia
        self._register_strategy_pnl(strategy_name, trade["closed_pnl"])

    # ---------- loop principal ----------

    def start(self):
        print("[BOT] Iniciando robô em modo DEMO (paper trading).")
        equity = self.broker.get_balance()
        self.realized_pnl = 0.0  # 🔹 zera PnL realizado ao iniciar
        self.risk_manager.reset_for_new_day(starting_equity=equity)
        self.is_running = True
        self.run_loop()

    def stop(self):
        print("[BOT] Robô parado (stop solicitado).")
        self.is_running = False

    def run_loop(self):
        while self.is_running:
            try:
                current_equity = self.broker.get_balance()
                self.last_equity = current_equity

                # 🔹 RiskManager continua usando PnL total (equity)
                self.risk_manager.update_pnl(current_equity)

                # 🔹 Mas o painel vai mostrar APENAS PnL realizado
                self.last_pnl = self.realized_pnl

                if not self.risk_manager.can_trade():
                    print("[BOT] Operações bloqueadas (meta/stop). Encerrando loop.")
                    self.stop()
                    break

                candles = self.broker.get_historical_candles(
                    SYMBOL, minutes=TIMEFRAME_MINUTES, limit=120
                )

                signal, strategy_name = choose_best_signal(
                    candles, self.strategy_stats
                )
                last_price = self.broker.get_last_price(SYMBOL)

                print(
                    f"[{datetime.now().isoformat()}] Estrat: {strategy_name} "
                    f"| Sinal: {signal} | Preço: {last_price:.2f}"
                )

                if signal == "BUY":
                    result = self.broker.market_buy(SYMBOL, POSITION_SIZE)
                    self._add_trade(result, strategy_name)
                elif signal == "SELL":
                    result = self.broker.market_sell(SYMBOL, POSITION_SIZE)
                    self._add_trade(result, strategy_name)

            except Exception as e:
                print(f"[ERRO] {e}")

            time.sleep(LOOP_SLEEP_SECONDS)
