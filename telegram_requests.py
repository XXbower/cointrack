import requests


def send_message(bot_token: str, chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={text}&parse_mode=html" \
          f"&disable_web_page_preview=True"
    return requests.get(url)
