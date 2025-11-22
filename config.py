# config.py

API_KEY = "DEMO_KEY"
API_SECRET = "DEMO_SECRET"

# Ativo "padrão" (no demo é simbólico)
SYMBOL = "BTCUSDT"
TIMEFRAME_MINUTES = 5

# Meta / stop em % da banca inicial do dia
DAILY_TARGET_PCT = 0.01   # 1% de lucro
DAILY_STOP_PCT = 0.005    # 0.5% de perda

# Tamanho padrão da posição (unidades do ativo)
POSITION_SIZE = 0.01

# Intervalo entre ciclos do bot (segundos)
LOOP_SLEEP_SECONDS = 5
