# strategy.py

import numpy as np

# ---------- Indicadores ----------


def rsi(closes: np.ndarray, period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0

    deltas = np.diff(closes)
    ups = np.where(deltas > 0, deltas, 0.0)
    downs = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = ups[-period:].mean()
    avg_loss = downs[-period:].mean() if downs[-period:].mean() != 0 else 1e-9

    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


# ---------- Estratégias ----------


def strategy_ma_trend(candles) -> str:
    """Tendência: cruzamento de médias."""
    closes = np.array([c["close"] for c in candles])
    if len(closes) < 50:
        return "HOLD"

    short_ma = closes[-10:].mean()
    long_ma = closes[-50:].mean()

    if short_ma > long_ma * 1.002:
        return "BUY"
    elif short_ma < long_ma * 0.998:
        return "SELL"
    return "HOLD"


def strategy_rsi_reversion(candles) -> str:
    """Reversão: RSI sobrecomprado/sobrevendido."""
    closes = np.array([c["close"] for c in candles])
    if len(closes) < 20:
        return "HOLD"

    value = rsi(closes, period=14)
    if value < 30:
        return "BUY"
    elif value > 70:
        return "SELL"
    return "HOLD"


def strategy_breakout(candles) -> str:
    """Breakout: rompimento de máxima/mínima recente."""
    closes = np.array([c["close"] for c in candles])
    if len(closes) < 40:
        return "HOLD"

    recent = closes[-20:]
    prev = closes[-40:-20]

    recent_high = recent.max()
    recent_low = recent.min()
    prev_high = prev.max()
    prev_low = prev.min()

    if recent_high > prev_high * 1.002:
        return "BUY"
    if recent_low < prev_low * 0.998:
        return "SELL"
    return "HOLD"


# ---------- Combinação / "aprendizado" ----------


def choose_best_signal(candles, strategy_stats: dict) -> tuple[str, str]:
    """
    Calcula sinal de várias estratégias e escolhe a que está performando melhor.
    Retorna: (signal, strategy_name)
    """
    strategies = {
        "ma_trend": strategy_ma_trend,
        "rsi_reversion": strategy_rsi_reversion,
        "breakout": strategy_breakout,
    }

    votes = []

    for name, fn in strategies.items():
        signal = fn(candles)
        if signal == "HOLD":
            continue

        stats = strategy_stats.get(name, {"pnl": 0.0, "trades": 0})
        base_score = 1.0
        pnl_boost = max(0.0, stats["pnl"]) / 50.0  # mais peso se pnl > 0
        score = base_score + pnl_boost

        votes.append((signal, score, name))

    if not votes:
        return "HOLD", "none"

    best_signal, _, best_name = max(votes, key=lambda x: x[1])
    return best_signal, best_name
