import re
import time
from dataclasses import dataclass
from typing import Union, List, Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger

from utils import fix_prices


@dataclass
class TransactionInfo:
    name: str = ''
    symbol: str = ''
    hash: str = ''
    bnb_value: str = ''
    coin_value: str = ''
    value: str = ''
    value_usd: str = ''
    coin_rate: float = 1
    busd_rate: float = 1
    is_buy_coin: bool = None
    is_wbnb: bool = None


class CoinData:
    def __init__(self, contract_address: str, address: str, symbol: str, short_name: str, bsc_token: str, offset: int):
        self._bsc_token: str = bsc_token
        self._contract_address: str = contract_address
        self._address: str = address
        self.symbol = symbol
        self.short_name = short_name
        self._offset = offset
        self._last_transaction_hash: dict = {}
        self._base_transfers_url = "https://api.bscscan.com/api?module=account&action=tokentx" \
                                   "&contractaddress={contract_address}&address={address}&sort=desc" \
                                   "&page=1&offset={offset}&apikey={bsc_token}"
        self._base_transaction_url = "https://bscscan.com/tx/{transaction_hash}"

    def _get_transfers(self) -> Optional[List[dict]]:
        url = self._base_transfers_url.format(contract_address=self._contract_address,
                                              address=self._address,
                                              offset=self._offset,
                                              bsc_token=self._bsc_token)
        try:
            response_data = requests.get(url).json()
        except requests.exceptions.ConnectionError:
            logger.info(f"Connection issue...")
            time.sleep(10)
            return
        else:
            logger.debug(f"API response:\n{response_data}")
            return response_data['result']

    def get_updates(self) -> List[TransactionInfo]:
        transfers = self._get_transfers()
        if not isinstance(transfers, list):
            logger.warning(f"Unexpected response:\n{transfers}")
            return []
        if transfers[0]['tokenSymbol'] != self.symbol:
            raise ValueError("SYMBOL from config didn't match the received symbol from bscscan.")
        hashes = [t['hash'] for t in transfers]
        if self._last_transaction_hash and self._last_transaction_hash in hashes:
            last_index = hashes.index(self._last_transaction_hash)
            new_transactions = transfers[:last_index]
            logger.debug(f"{len(new_transactions)} new transactions: {new_transactions}")
        else:
            new_transactions = [transfers[0]]
        self._last_transaction_hash = transfers[0]['hash']
        result = []
        unique_transactions = {item['hash']: item for item in new_transactions}.values()
        for transaction in unique_transactions:
            data = self.get_transaction_data(transaction['hash'],
                                             transaction['tokenName'],
                                             transaction['tokenSymbol'])
            if data:
                data = fix_prices(data)
                result.append(data)
        return result

    @staticmethod
    def value_to_float(value: str) -> float:
        value = value.replace(",", '')
        if value:
            return float(value)
        return 0.0

    def get_transaction_data(self, transaction_hash: str, transaction_name: str,
                             transaction_symbol: str) -> Union[TransactionInfo, None]:
        """ Returns TransactionInfo dataclass with transaction's info. """
        transaction_data = TransactionInfo()
        transaction_data.hash = transaction_hash
        transaction_data.name = transaction_name
        transaction_data.symbol = transaction_symbol
        logger.debug(f"Requesting data for transaction: {transaction_hash}")
        url = self._base_transaction_url.format(transaction_hash=transaction_hash)
        response_text = requests.get(url).text
        logger.debug(f"Response:\n{response_text}")
        soup = BeautifulSoup(response_text, 'html.parser')
        transaction_data.bnb_value = float(soup.find(id='ethPrice').find('span').text[6:])

        coin_transfers = [div.get_text(" ") for div in soup.find_all("div", {"class": "media-body"})
                          if '>From<' in str(div)]
        logger.debug(f"Coin transfers:\n{coin_transfers}")
        if not coin_transfers:
            return
        for transfer in reversed(coin_transfers):
            if 'WBNB' in transfer or 'BUSD' in transfer:
                transaction_data.is_buy_coin = False
                break
            elif transaction_data.symbol.lower() in transfer.lower() \
                    or self.short_name.lower() in transfer.lower():
                transaction_data.is_buy_coin = True
                break

        for transfer in coin_transfers:
            transfer = transfer[transfer.find('For'):]
            if 'WBNB' in transfer:
                transaction_data.value, transaction_data.value_usd = re.findall(r'\b[0-9.,]+\b',
                                                                                transfer)
                transaction_data.is_wbnb = True
            elif 'BUSD' in transfer:
                transaction_data.value, transaction_data.value_usd = re.findall(r'\b[0-9.,]+\b',
                                                                                transfer)
                transaction_data.is_wbnb = False

            if transaction_data.symbol.lower() in transfer.lower() \
                    or self.short_name.lower() in transfer.lower():
                transaction_data.coin_value = re.findall(r'\b[0-9.,]+\b', transfer)[0].replace(',', '')

        if not all([transaction_data.value, transaction_data.value_usd, transaction_data.coin_value]):
            return
            # raise ValueError("Prices fetching failed.")

        if transaction_data.is_wbnb:
            transaction_data.coin_rate = (self.value_to_float(transaction_data.value) * transaction_data.bnb_value
                                          / self.value_to_float(transaction_data.coin_value))
        else:
            transaction_data.coin_rate = (self.value_to_float(transaction_data.value_usd)
                                          / self.value_to_float(transaction_data.coin_value))

        logger.debug(f"Transaction data:\n{transaction_data}")
        return transaction_data
