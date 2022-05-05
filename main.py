import sys

import config
from coin_data_parser import CoinData
import telegram_requests
from utils import prettify_message
import time
from loguru import logger


def main():
    logger.remove()
    logger.add(sys.stderr, level="DEBUG" if config.DEBUG else "INFO")
    logger.add(config.SYMBOL + "_{time}.log", encoding='utf-8', rotation="500 mb",
               level="DEBUG" if config.DEBUG else "INFO")
    logger.info("Starting bot...")
    config_vars = {k: v for k, v in config.__dict__.items() if not k.startswith("__")}
    logger.info(f"Config: {config_vars}")
    coin_data = CoinData(config.CONTRACT_ADDRESS, config.ADDRESS, config.SYMBOL, config.SHORT_NAME,
                         config.BSCSCAN_TOKEN, config.TX_PER_REQUEST)
    while True:
        updates = coin_data.get_updates()
        if updates:
            for update in updates:
                logger.info(f"Update:\n{update}")
                telegram_requests.send_message(config.TELEGRAM_TOKEN, config.CHANNEL_ID, prettify_message(update))
        logger.debug(f"Sleeping {config.SLEEP_TIME} sec.")
        time.sleep(config.SLEEP_TIME)


if __name__ == '__main__':
    main()
