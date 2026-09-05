import re
import requests
from bs4 import BeautifulSoup

URL = "https://milli.gold/"

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

    # قیمت ۱ گرم طلای ۱۸ عیار
    pattern = r"([\d,]+)\s*ریال\s*قیمت\s*1?\s*گرم\s*طلای\s*18\s*عیار"

    match = re.search(pattern, text)

    if not match:
        raise ValueError("قیمت میلی در صفحه پیدا نشد.")

    price_rial = int(match.group(1).replace(",", ""))
    price_toman = price_rial // 10

    return price_toman


if __name__ == "__main__":
    price = get_milli_price()

    print("MILLI GOLD")
    print("-" * 30)
    print(f"Price: {price:,} تومان")
