# config.py

# "API" fictícia por enquanto (modo paper trading)
API_KEY = "DEMO_KEY"
API_SECRET = "DEMO_SECRET"

# Ativo que o bot vai operar (no demo é só um nome simbólico)
SYMBOL = "BTCUSDT"
TIMEFRAME_MINUTES = 5  # timeframe lógico da estratégia

# Gestão de risco automática baseada em % da banca inicial do dia
# Exemplo: 1% de meta e 0.5% de stop loss da banca
DAILY_TARGET_PCT = 0.01   # 1% de lucro
DAILY_STOP_PCT = 0.005    # 0.5% de perda

# Tamanho padrão da posição (em unidades do ativo)
POSITION_SIZE = 0.01

# Intervalo entre ciclos do bot (segundos)
LOOP_SLEEP_SECONDS = 5
