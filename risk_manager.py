# risk_manager.py

from datetime import datetime, date

class RiskManager:
    def __init__(self, daily_target: float, daily_stop_loss: float):
        self.daily_target = daily_target
        self.daily_stop_loss = daily_stop_loss
        self.reset_for_new_day()

    def reset_for_new_day(self, starting_equity: float | None = None):
        self.current_day = date.today()
        self.starting_equity = starting_equity
        self.current_pnl = 0.0
        self.trading_allowed = True

    def update_pnl(self, current_equity: float):
        if self.starting_equity is None:
            self.starting_equity = current_equity
            self.current_pnl = 0.0
            return

        self.current_pnl = current_equity - self.starting_equity

        # Checar meta e stop
        if self.current_pnl >= self.daily_target:
            self.trading_allowed = False
            print(f"[RISK] Meta diária atingida: +{self.current_pnl:.2f}")
        elif self.current_pnl <= self.daily_stop_loss:
            self.trading_allowed = False
            print(f"[RISK] Stop loss diário atingido: {self.current_pnl:.2f}")

    def can_trade(self) -> bool:
        # Se virou o dia, reseta
        if date.today() != self.current_day:
            print("[RISK] Novo dia detectado, resetando PnL.")
            self.reset_for_new_day()
        return self.trading_allowed
