import re
import json
import os
import requests
from bs4 import BeautifulSoup

URL = "https://milli.gold/"
THRESHOLD = 400_000
STATE_FILE = "price_state.json"


def normalize_digits(text):
    translation = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    )
    return text.translate(translation)


def get_milli_price():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)
    text = normalize_digits(text)

    # Price of 1 gram of 18k gold
    pattern = r"([\d,]+)\s*ریال\s*قیمت\s*1\s*گرم\s*طلای\s*18\s*عیار"

    match = re.search(pattern, text)

    if not match:
        raise ValueError("Milli gold price was not found.")

    price_rial = int(match.group(1).replace(",", ""))
    price_toman = price_rial // 10

    return price_toman


def load_base_price():
    if not os.path.exists(STATE_FILE):
        return None

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data["base_price"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def save_base_price(price):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"base_price": price}, f)


if __name__ == "__main__":
    price = get_milli_price()
    base_price = load_base_price()

    print("MILLI GOLD")
    print("-" * 30)
    print(f"Price: {price:,} تومان")

    if base_price is None:
        save_base_price(price)
        print(f"Base price initialized: {price:,} تومان")
        print("Alert: NONE")

    else:
        change = price - base_price

        print(f"Base price: {base_price:,} تومان")
        print(f"Change: {change:+,} تومان")

        if change >= THRESHOLD:
            print("Alert: UP")
            print(f"Movement: +{change:,} تومان")
            save_base_price(price)

        elif change <= -THRESHOLD:
            print("Alert: DOWN")
            print(f"Movement: {change:,} تومان")
            save_base_price(price)

        else:
            print("Alert: NONE")
