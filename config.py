import os

BSCSCAN_TOKEN = os.getenv('BSCSCAN_TOKEN')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
ADDRESS = os.getenv('ADDRESS')
SYMBOL = os.getenv('SYMBOL')
SHORT_NAME = os.getenv('SHORT_NAME', SYMBOL)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
BUY_URL = os.getenv('BUY_URL')
CHART_URL = os.getenv('CHART_URL')
SUPPLY = int(os.getenv('SUPPLY'))

COIN_ROUND = int(os.getenv('COIN_ROUND', 5))
BNB_ROUND = int(os.getenv('BNB_ROUND', 5))

COIN_RATE_ROUND = int(os.getenv('COIN_RATE_ROUND', 5))

COIN_RATE_MULTIPLIER = int(os.getenv('COIN_RATE_MULTIPLIER', 1))
COIN_RATE_MULTIPLIER_SYMBOL = os.getenv('COIN_RATE_MULTIPLIER_SYMBOL', "")

MCAP_ROUND = int(os.getenv('MCAP_ROUND', 5))

SLEEP_TIME = float(os.getenv('SLEEP_TIME', 0.5))
TX_PER_REQUEST = int(os.getenv('TX_PER_REQUEST', 10))
DEBUG = bool(os.getenv('DEBUG', False))

VALUE_COEFFICIENT = float(os.getenv('VALUE_COEFFICIENT', 1.0))
COIN_VALUE_COEFFICIENT = float(os.getenv('COIN_VALUE_COEFFICIENT', 1.0))
