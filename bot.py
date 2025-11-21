# bot.py

import time
from datetime import datetime
from config import (
    API_KEY, API_SECRET, SYMBOL, TIMEFRAME_MINUTES,
    DAILY_TARGET, DAILY_STOP_LOSS, POSITION_SIZE,
    LOOP_SLEEP_SECONDS
)
from broker_client import BrokerClient
from strategy import moving_average_crossover_strategy
from risk_manager import RiskManager


class TradingBot:
    def __init__(self):
        self.broker = BrokerClient(API_KEY, API_SECRET)
        self.risk_manager = RiskManager(DAILY_TARGET, DAILY_STOP_LOSS)
        self.is_running = False

    def start(self):
        print("[BOT] Iniciando robô...")
        # pegar saldo inicial do dia
        equity = self.broker.get_balance()
        self.risk_manager.reset_for_new_day(starting_equity=equity)
        self.is_running = True
        self.run_loop()

    def stop(self):
        print("[BOT] Parando robô...")
        self.is_running = False

    def run_loop(self):
        while self.is_running:
            try:
                # Atualiza PnL
                current_equity = self.broker.get_balance()
                self.risk_manager.update_pnl(current_equity)

                if not self.risk_manager.can_trade():
                    print("[BOT] Operações bloqueadas (meta/stop atingido).")
                    self.stop()
                    break

                candles = self.broker.get_historical_candles(
                    SYMBOL,
                    minutes=TIMEFRAME_MINUTES,
                    limit=100
                )

                signal = moving_average_crossover_strategy(candles)
                last_price = self.broker.get_last_price(SYMBOL)

                print(f"[{datetime.now().isoformat()}] Sinal: {signal} | Preço: {last_price}")

                if signal == "BUY":
                    self.broker.market_buy(SYMBOL, POSITION_SIZE)
                    print(f"[BOT] Ordem de COMPRA enviada: {SYMBOL} qty={POSITION_SIZE}")
                elif signal == "SELL":
                    self.broker.market_sell(SYMBOL, POSITION_SIZE)
                    print(f"[BOT] Ordem de VENDA enviada: {SYMBOL} qty={POSITION_SIZE}")

            except Exception as e:
                print(f"[ERRO] {e}")

            time.sleep(LOOP_SLEEP_SECONDS)


if __name__ == "__main__":
    bot = TradingBot()
    bot.start()
