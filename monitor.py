import yfinance as yf
import requests
import os
from collections import defaultdict

WATCHERS = [
    {
        "symbol": "DELL",
        "above":  152.00,
        "below":   90.00,
        "ntfy":   os.environ.get("NTFY_TOPIC", ""),
        "name":   "Me",
    },
    {
        "symbol": "NVDA",
        "above":  200.00,
        "below":  130.00,
        "ntfy":   os.environ.get("NTFY_TOPIC", ""),
        "name":   "Me",
    },
    {
        "symbol": "AMZN",
        "above":  250.00,
        "below":  180.00,
        "ntfy":   os.environ.get("NTFY_TOPIC", ""),
        "name":   "Me",
    },
    {
        "symbol": "^GSPC",  # S&P 500 Index
        "above":  6800.00,
        "below":  6000.00,
        "ntfy":   os.environ.get("NTFY_TOPIC", ""),
        "name":   "Me",
    },
    {
        "symbol": "AMD",
        "above":  250.00,
        "below":  160.00,
        "ntfy":   os.environ.get("NTFY_TOPIC", ""),
        "name":   "Me",
    },
    {
        "symbol": "KO",  # Coca-Cola
        "above":  85.00,
        "below":  65.00,
        "ntfy":   os.environ.get("NTFY_TOPIC", ""),
        "name":   "Me",
    },
    {
        "symbol": "AAPL",
        "above":  280.00,
        "below":  200.00,
        "ntfy":   os.environ.get("NTFY_TOPIC", ""),
        "name":   "Me",
    },
    {
        "symbol": "MSFT",
        "above":  420.00,
        "below":  340.00,
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
    if not ntfy_topic:
        print(f"  Skipping alert '{title}' - no ntfy topic configured.")
        return
        
    url = "https://ntfy.sh/" + ntfy_topic
    print("  Sending to URL: " + url)
    
    # Ensure headers are strictly ASCII to prevent requests/urllib3 crash
    safe_title = title.encode("ascii", "ignore").decode("ascii")
    
    headers = {
        "Title": safe_title,
        "Priority": priority,
        "Tags": "chart_increasing"
    }
    
    # The body can contain emojis safely (encoded as UTF-8 bytes)
    response = requests.post(url, data=message.encode("utf-8"), headers=headers)
    response.raise_for_status()
    print("  Alert sent OK")

def check_watcher(watcher) -> tuple[str, bool]:
    """Returns (message_string, is_triggered)."""
    symbol = watcher["symbol"]
    above  = watcher["above"]
    below  = watcher["below"]
    name   = watcher.get("name", "")

    print(f"Checking {symbol} for {name}...")
    price = get_price(symbol)
    print(f"  Current price: ${price}")

    if price > above:
        return f"🟢 {symbol}: ${price} (above ${above})", True
    elif price < below:
        return f"🔴 {symbol}: ${price} (below ${below})", True
    else:
        return f"⚪ {symbol}: ${price}", False

def main():
    # Group alerts by ntfy_topic so we only send one message per phone
    messages_by_topic = defaultdict(list)
    topic_triggered = defaultdict(bool)
    
    for watcher in WATCHERS:
        try:
            msg, triggered = check_watcher(watcher)
            topic = watcher["ntfy"]
            messages_by_topic[topic].append(msg)
            if triggered:
                topic_triggered[topic] = True
        except Exception as e:
            print(f"  Error checking {watcher.get('symbol')}: {e}")

    # Send the bundled alerts ONLY if at least one stock for that topic triggered
    for topic, messages in messages_by_topic.items():
        if not topic:
            continue
            
        if not topic_triggered[topic]:
            print(f"\nNo triggers for topic '{topic}'. Skipping notification.")
            continue
            
        # HTTP headers must be Latin-1, so avoid emojis in the Title header
        title = "Stock Price Alerts"
        
        # We can safely use emojis in the message body
        combined_message = "📈 **Market Update:**\n\n" + "\n".join(messages)
        
        print(f"\nSending bundled alert to topic '{topic}':")
        print(combined_message)
        send_alert(topic, title, combined_message)

if __name__ == "__main__":
    main()
