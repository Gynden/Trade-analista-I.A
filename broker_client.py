# broker_client.py

import random
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Position:
    symbol: str
    qty: float
    side: str  # "LONG" ou "SHORT"
    entry_price: float


class BrokerClient:
    """
    Cliente de 'corretora' em modo SIMULADO (paper trading).
    Não envia ordens reais, só simula preço, saldo e PnL.
    """

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

        # Estado interno do "cliente"
        self._cash_balance = 10_000.0     # saldo inicial fictício
        self._price = 100.0               # preço inicial fictício
        self._position: Position | None = None

        # Para gerar candles
        self._last_candle_time = datetime.utcnow()

    # --------- Funções de estado ---------

    def _update_price(self):
        """Atualiza o preço com um 'random walk' simples."""
        move = random.uniform(-1.0, 1.0)
        self._price = max(1.0, self._price + move)

    def _unrealized_pnl(self) -> float:
        if not self._position:
            return 0.0

        if self._position.side == "LONG":
            return (self._price - self._position.entry_price) * self._position.qty
        elif self._position.side == "SHORT":
            return (self._position.entry_price - self._price) * self._position.qty
        return 0.0

    def get_balance(self) -> float:
        """
        Retorna o 'equity' total (caixa + PnL não realizado).
        """
        self._update_price()
        return self._cash_balance + self._unrealized_pnl()

    def get_last_price(self, symbol: str) -> float:
        """
        Último preço do ativo (simulado).
        """
        self._update_price()
        return self._price

    def get_historical_candles(self, symbol: str, minutes: int, limit: int = 100):
        """
        Gera candles sintéticos para a estratégia.
        Cada candle tem: time, open, high, low, close.
        """
        candles = []
        now = datetime.utcnow()
        # recomeça a timeline dos candles a partir de agora
        start_time = now - timedelta(minutes=minutes * limit)
        t = start_time
        price = self._price

        for _ in range(limit):
            # random walk por candle
            move = random.uniform(-1.5, 1.5)
            open_price = price
            close_price = max(1.0, price + move)
            high_price = max(open_price, close_price) + random.uniform(0, 0.5)
            low_price = min(open_price, close_price) - random.uniform(0, 0.5)

            candles.append({
                "time": t.isoformat(),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
            })

            price = close_price
            t += timedelta(minutes=minutes)

        # atualiza o preço interno para o último close
        self._price = price
        self._last_candle_time = t
        return candles

    # --------- Execução de ordens ---------

    def _close_position_if_exists(self):
        """
        Fecha posição atual, se existir, realizando o PnL.
        """
        if not self._position:
            return

        price = self._price
        pnl = 0.0

        if self._position.side == "LONG":
            pnl = (price - self._position.entry_price) * self._position.qty
        elif self._position.side == "SHORT":
            pnl = (self._position.entry_price - price) * self._position.qty

        self._cash_balance += pnl
        print(f"[BROKER] Posição fechada | side={self._position.side} qty={self._position.qty} "
              f"entry={self._position.entry_price:.2f} exit={price:.2f} pnl={pnl:.2f}")

        self._position = None

    def market_buy(self, symbol: str, qty: float) -> dict:
        """
        Simula uma ordem de compra a mercado.
        Se houver SHORT aberta, fecha antes.
        """
        self._update_price()
        price = self._price

        # se tiver short, fecha
        if self._position and self._position.side == "SHORT":
            self._close_position_if_exists()

        cost = qty * price
        if cost > self._cash_balance:
            print("[BROKER] Saldo insuficiente para COMPRA.")
            return {"status": "rejected", "reason": "insufficient_funds"}

        self._cash_balance -= cost
        self._position = Position(symbol=symbol, qty=qty, side="LONG", entry_price=price)

        print(f"[BROKER] COMPRA executada | {symbol} qty={qty} price={price:.2f}")
        return {
            "status": "filled",
            "side": "BUY",
            "symbol": symbol,
            "qty": qty,
            "price": price,
            "time": datetime.utcnow().isoformat()
        }

    def market_sell(self, symbol: str, qty: float) -> dict:
        """
        Simula uma ordem de venda a mercado.
        Se houver LONG aberta, fecha antes.
        """
        self._update_price()
        price = self._price

        # se tiver long, fecha
        if self._position and self._position.side == "LONG":
            self._close_position_if_exists()

        # em modo demo vamos permitir abrir short sem margem por simplicidade
        self._position = Position(symbol=symbol, qty=qty, side="SHORT", entry_price=price)

        print(f"[BROKER] VENDA executada | {symbol} qty={qty} price={price:.2f}")
        return {
            "status": "filled",
            "side": "SELL",
            "symbol": symbol,
            "qty": qty,
            "price": price,
            "time": datetime.utcnow().isoformat()
        }
