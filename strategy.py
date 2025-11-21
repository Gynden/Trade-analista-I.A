# strategy.py

import numpy as np

def moving_average_crossover_strategy(candles) -> str:
    """
    candles: lista de dicts ou objetos com 'close'
    Retorna: "BUY", "SELL" ou "HOLD"
    """
    closes = np.array([c["close"] for c in candles])

    if len(closes) < 50:
        return "HOLD"

    short_ma = closes[-10:].mean()
    long_ma  = closes[-50:].mean()

    if short_ma > long_ma * 1.001:   # margem mínima pra evitar ruído
        return "BUY"
    elif short_ma < long_ma * 0.999:
        return "SELL"
    else:
        return "HOLD"
