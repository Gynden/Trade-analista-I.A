# config.py

# "API" fictícia por enquanto (modo paper trading)
API_KEY = "DEMO_KEY"
API_SECRET = "DEMO_SECRET"

# Ativo e parâmetros
SYMBOL = "BTCUSDT"        # só um nome simbólico no modo demo
TIMEFRAME_MINUTES = 5     # timeframe lógico da estratégia

# Gestão de risco
DAILY_TARGET = 50.0       # meta de lucro diária (ex.: +50)
DAILY_STOP_LOSS = -30.0   # stop diário (ex.: -30)

# Tamanho padrão da posição (em unidades do ativo)
POSITION_SIZE = 0.01

# Bot
LOOP_SLEEP_SECONDS = 5    # segundos entre cada ciclo de análise (aumenta depois se quiser)
