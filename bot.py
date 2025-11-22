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
    # noqa
from strategy import moving_average_crossover_strategy
from risk_manager import RiskManager


class TradingBot:
    def __init__(self):
        self.broker = BrokerClient(API_KEY, API_SECRET)
        self.risk_manager = RiskManager(DAILY_TARGET_PCT, DAILY_STOP_PCT)

        self.is_running: bool = False
        self.last_equity: float | None = None
        self.last_pnl: float | None = None

        # histórico de operações
        self.trades: list[dict] = []

    def _add_trade(self, order_result: dict):
        if order_result.get("status") != "filled":
            return

        trade = {
            "time": order_result.get("time"),
            "symbol": order_result.get("symbol"),
            "side": order_result.get("order_type"),  # BUY / SELL
            "qty": order_result.get("qty"),
            "price": order_result.get("price"),
            "closed_pnl": order_result.get("closed_pnl"),
        }

        self.trades.append(trade)
        # guarda só as últimas 100 pra não crescer infinito
        if len(self.trades) > 100:
            self.trades = self.trades[-100:]

    def start(self):
        print("[BOT] Iniciando robô em modo DEMO (paper trading).")
        equity = self.broker.get_balance()
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

                self.risk_manager.update_pnl(current_equity)
                self.last_pnl = self.risk_manager.current_pnl

                if not self.risk_manager.can_trade():
                    print("[BOT] Operações bloqueadas (meta/stop). Encerrando loop.")
                    self.stop()
                    break

                candles = self.broker.get_historical_candles(
                    SYMBOL, minutes=TIMEFRAME_MINUTES, limit=100
                )

                signal = moving_average_crossover_strategy(candles)
                last_price = self.broker.get_last_price(SYMBOL)

                print(
                    f"[{datetime.now().isoformat()}] Sinal: {signal} | Preço: {last_price:.2f}"
                )

                if signal == "BUY":
                    result = self.broker.market_buy(SYMBOL, POSITION_SIZE)
                    self._add_trade(result)
                elif signal == "SELL":
                    result = self.broker.market_sell(SYMBOL, POSITION_SIZE)
                    self._add_trade(result)

            except Exception as e:
                print(f"[ERRO] {e}")

            time.sleep(LOOP_SLEEP_SECONDS)
