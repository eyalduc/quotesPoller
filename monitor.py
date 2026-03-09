import yfinance as yf
import requests
import os

# ============================================================
#  WATCHERS — add or edit entries here
#  Each watcher monitors one stock and alerts one ntfy topic
# ============================================================
WATCHERS = [
    {
        "symbol": "DELL",
        "above":  140.00,       # alert if price goes ABOVE this
        "below":   90.00,       # alert if price goes BELOW this
        "ntfy":   os.environ.get("NTFY_TOPIC", ""),
        "name":   "Me",
    }, 
    {
         "symbol": "HTZWW",
         "above":  3.00,
         "below":  2.01,
         "ntfy":   os.environ.get("NTFY_TOPIC_DAD", ""),
         "name":   "Dad",
     },
]
# ============================================================

def get_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    price = ticker.fast_info["last_price"]
    if price is None:
        raise ValueError(f"No data returned for {symbol}")
    return round(float(price), 2)

def send_alert(ntfy_topic: str, title: str, message: str, priority: str = "high"):
    url = f"https://ntfy.sh/{ntfy_topic}"
    print(f"  → Sending to URL: {url}")  # add this line
    headers = {
        "Title": title,
        "Priority": priority,
        "Tags": "chart_increasing"
    }
    response = requests.post(url, data=message.encode("utf-8"), headers=headers)
    response.raise_for_status()
    print(f"  → Alert sent to {ntfy_topic}: {message}")

def check_watcher(watcher: dict):
    symbol = watcher["symbol"]
    above  = watcher["above"]
    below  = watcher["below"]
    ntfy   = watcher["ntfy"]
    name   = watcher.get("name", "")

    print(f"Checking {symbol} for {name}...")
    price = get_price(symbol)
    print(f"  Current price: ${price}")

    if price > above:
        send_alert(
            ntfy_topic=ntfy,
            title=f"{symbol} Price Alert - HIGH",
            message=f"{symbol} is now ${price} - above your threshold of ${above}"
        )
    elif price < below:
        send_alert(
            ntfy_topic=ntfy,
            title=f"{symbol} Price Alert - LOW",
            message=f"{symbol} is now ${price} - below your threshold of ${below}"
        )
    else:
        print(f"  Price ${price} is within range (${below} - ${above}). No alert sent.")

def main():
    for watcher in WATCHERS:
        try:
            check_watcher(watcher)
        except Exception as e:
            print(f"  Error checking {watcher.get('symbol')}: {e}")

if __name__ == "__main__":
    main()
