# broker_client.py

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Position:
    symbol: str
    qty: float
    side: str  # "LONG" ou "SHORT"
    entry_price: float

class BrokerClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        # aqui você inicializaria o cliente oficial da corretora (ex: binance, alpaca etc.)

    def get_balance(self) -> float:
        """
        Retorna o saldo da conta.
        Em produção, chame a API real.
        """
        # TODO: implementar com a corretora real
        raise NotImplementedError

    def get_last_price(self, symbol: str) -> float:
        """
        Retorna o último preço do símbolo.
        """
        # TODO: implementar com a corretora real
        raise NotImplementedError

    def get_historical_candles(self, symbol: str, minutes: int, limit: int = 100):
        """
        Retorna candles históricos (OHLC) para usar na estratégia.
        """
        # TODO: implementar com a corretora real
        raise NotImplementedError

    def market_buy(self, symbol: str, qty: float) -> dict:
        """
        Envia uma ordem de compra a mercado.
        """
        # TODO: implementar com a corretora real
        raise NotImplementedError

    def market_sell(self, symbol: str, qty: float) -> dict:
        """
        Envia uma ordem de venda a mercado.
        """
        # TODO: implementar com a corretora real
        raise NotImplementedError
