import yfinance as yf
import requests
import os

WATCHERS = [
    {
        "symbol": "DELL",
        "above":  152.00,
        "below":   90.00,
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

def get_price(symbol):
    ticker = yf.Ticker(symbol)
    price = ticker.fast_info["last_price"]
    if price is None:
        raise ValueError(f"No data returned for {symbol}")
    return round(float(price), 2)

def send_alert(ntfy_topic, title, message, priority="high"):
    url = "https://ntfy.sh/" + ntfy_topic
    print("  Sending to URL: " + url)
    headers = {
        "Title": title,
        "Priority": priority,
        "Tags": "chart_increasing"
    }
    response = requests.post(url, data=message.encode("utf-8"), headers=headers)
    response.raise_for_status()
    print("  Alert sent OK")

def check_watcher(watcher):
    symbol = watcher["symbol"]
    above  = watcher["above"]
    below  = watcher["below"]
    ntfy   = watcher["ntfy"]
    name   = watcher.get("name", "")

    print("Checking " + symbol + " for " + name + "...")
    price = get_price(symbol)
    print("  Current price: $" + str(price))

    if price > above:
        send_alert(
            ntfy_topic=ntfy,
            title=symbol + " Price Alert HIGH",
            message=symbol + " is now $" + str(price) + " above your threshold of $" + str(above)
        )
    elif price < below:
        send_alert(
            ntfy_topic=ntfy,
            title=symbol + " Price Alert LOW",
            message=symbol + " is now $" + str(price) + " below your threshold of $" + str(below)
        )
    else:
        print("  Price $" + str(price) + " is within range. No alert sent.")

def main():
    for watcher in WATCHERS:
        try:
            check_watcher(watcher)
        except Exception as e:
            print("  Error checking " + str(watcher.get("symbol")) + ": " + str(e))

if __name__ == "__main__":
    main()
