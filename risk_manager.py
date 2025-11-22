# risk_manager.py

from datetime import date


class RiskManager:
    """
    Faz o controle de risco diário com base em % da banca inicial do dia.
    """

    def __init__(self, target_pct: float, stop_pct: float):
        self.target_pct = target_pct      # ex.: 0.01 (1%)
        self.stop_pct = stop_pct          # ex.: 0.005 (0.5%)

        self.daily_target: float | None = None
        self.daily_stop_loss: float | None = None
        self.starting_equity: float | None = None
        self.current_pnl: float = 0.0
        self.trading_allowed: bool = True
        self.current_day = date.today()

    def reset_for_new_day(self, starting_equity: float):
        self.current_day = date.today()
        self.starting_equity = starting_equity

        # Calcula meta e stop em valor
        self.daily_target = self.starting_equity * self.target_pct
        self.daily_stop_loss = -self.starting_equity * self.stop_pct

        self.current_pnl = 0.0
        self.trading_allowed = True

        print(
            f"[RISK] Novo dia iniciado. Equity inicial: {self.starting_equity:.2f} | "
            f"Meta: {self.daily_target:.2f} | Stop: {self.daily_stop_loss:.2f}"
        )

    def update_pnl(self, current_equity: float):
        if self.starting_equity is None:
            # se for a primeira chamada, inicializa
            self.reset_for_new_day(current_equity)

        self.current_pnl = current_equity - self.starting_equity
        print(f"[RISK] PnL atual do dia: {self.current_pnl:.2f}")

        if self.daily_target is None or self.daily_stop_loss is None:
            return

        if self.current_pnl >= self.daily_target:
            self.trading_allowed = False
            print(f"[RISK] ✅ Meta diária atingida (+{self.current_pnl:.2f}).")
        elif self.current_pnl <= self.daily_stop_loss:
            self.trading_allowed = False
            print(f"[RISK] ⛔ Stop loss diário atingido ({self.current_pnl:.2f}).")

    def can_trade(self) -> bool:
        # Se virou o dia, reseta em cima da equity final de ontem
        if date.today() != self.current_day and self.starting_equity is not None:
            print("[RISK] Mudança de dia detectada, resetando controles.")
            self.reset_for_new_day(self.starting_equity + self.current_pnl)

        return self.trading_allowed
