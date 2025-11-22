# risk_manager.py

from datetime import date


class RiskManager:
    """
    Controle de risco diário baseado em % da banca,
    com opção de meta manual em valor.
    """

    def __init__(self, target_pct: float, stop_pct: float):
        # target_pct aqui passa a ser o "pct efetivo" do dia (auto ou manual)
        self.target_pct = target_pct      # ex.: 0.01 (1% da banca)
        self.stop_pct = stop_pct          # ex.: 0.005 (0.5% da banca)

        self.daily_target: float | None = None
        self.daily_stop_loss: float | None = None
        self.starting_equity: float | None = None
        self.current_pnl: float = 0.0
        self.trading_allowed: bool = True
        self.current_day = date.today()

    def reset_for_new_day(self, starting_equity: float, manual_target: float | None = None):
        """
        Reseta controles para um novo dia.
        Se manual_target for informado, usa esse valor como meta; senão usa %.
        """
        self.current_day = date.today()
        self.starting_equity = starting_equity

        if manual_target is not None and manual_target > 0:
            # meta manual em valor
            self.daily_target = manual_target
            # recalcula % efetivo só para exibição no painel
            self.target_pct = manual_target / self.starting_equity
        else:
            # meta automática em % da banca
            self.daily_target = self.starting_equity * self.target_pct

        # stop continua sempre em % da banca
        self.daily_stop_loss = -self.starting_equity * self.stop_pct

        self.current_pnl = 0.0
        self.trading_allowed = True

        print(
            f"[RISK] Novo dia iniciado. Equity inicial: {self.starting_equity:.2f} | "
            f"Meta: {self.daily_target:.2f} | Stop: {self.daily_stop_loss:.2f}"
        )

    def update_pnl(self, current_equity: float):
        if self.starting_equity is None:
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
        # Se virou o dia, reseta em cima da equity final de ontem (com meta auto em %)
        if date.today() != self.current_day and self.starting_equity is not None:
            print("[RISK] Mudança de dia detectada, resetando controles.")
            self.reset_for_new_day(self.starting_equity + self.current_pnl)

        return self.trading_allowed
