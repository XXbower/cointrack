import urllib

from loguru import logger

from config import *


def _make_bold(s: str) -> str:
    return '<b>' + s + '</b>'


def _make_ulr(title: str, url: str) -> str:
    return f"<a href='{urllib.parse.quote_plus(url)}'>{title}</a>"


def prettify_message(transaction_info) -> str:
    transaction_url = f"https://bscscan.com/tx/{transaction_info.hash}"
    msg_words = []
    if transaction_info.is_buy_coin:
        msg_words.append('✅ Bought')

        indicator_emoji = '🟢'
        for _ in range(int(float(transaction_info.value) - 1)):
            indicator_emoji += '🟢'
    else:
        msg_words.append('📛 Sold')
        indicator_emoji = '🔴'
        for _ in range(int(float(transaction_info.value) - 1)):
            indicator_emoji += '🔴'

    value_symbol = 'BNB' if transaction_info.is_wbnb else 'BUSD'
    msg_words.extend(
        [f"{round(float(transaction_info.coin_value), COIN_ROUND):.{COIN_ROUND}f} {transaction_info.symbol}",
         'For',
         f"{round(float(transaction_info.value), BNB_ROUND):.{BNB_ROUND}f} {value_symbol} "
         f"(${transaction_info.value_usd})",
         'On PancakeSwap'])

    msg_words[1], msg_words[3], = map(_make_bold, (msg_words[1], msg_words[3]))

    swap_msg = " ".join(msg_words)
    coin_rate_msg = f"1{COIN_RATE_MULTIPLIER_SYMBOL} {transaction_info.symbol} = " \
                    f"${round(transaction_info.coin_rate * COIN_RATE_MULTIPLIER, COIN_RATE_ROUND):.{COIN_RATE_ROUND}f}"
    coin_rate_msg = _make_bold(coin_rate_msg)
    bnb_rate_msg = f"1 BNB = ${transaction_info.bnb_value}"
    mcap_value = SUPPLY * transaction_info.coin_rate
    mcap_msg = f"M.Cap = ${round(mcap_value, MCAP_ROUND)}"
    bnb_rate_msg = _make_bold(bnb_rate_msg)
    mcap_msg = _make_bold(mcap_msg)
    tx_url_mgs = _make_ulr("📶Tx. Hash📶", transaction_url)
    buy_url_mgs = _make_ulr("🍔Buy On Pancakeswap🍔", BUY_URL)
    chart_url_mgs = _make_ulr("📈Chart📈", CHART_URL)
    footer_msg = f"{tx_url_mgs} | {buy_url_mgs} | {chart_url_mgs}"

    msg = f"{swap_msg}\n\n{indicator_emoji}\n\n{coin_rate_msg}\n\n{bnb_rate_msg}\n{mcap_msg}\n\n" \
          f"{footer_msg}"
    logger.debug(f"Message:\n{msg}")
    return msg


def fix_prices(transaction_info):
    transaction_info.value = float(transaction_info.value) * VALUE_COEFFICIENT
    transaction_info.value_usd = float(transaction_info.value_usd) * VALUE_COEFFICIENT
    transaction_info.coin_value = float(transaction_info.coin_value) * COIN_VALUE_COEFFICIENT
    return transaction_info
