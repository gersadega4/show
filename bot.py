import requests
import time
import json
from datetime import datetime, timezone, timedelta

# ── Konfigurasi ──────────────────────────────────────────
BOT_TOKEN = "8732972288:AAGNqtZecH2dJ3A8Tc2gZS9cJ4SJIcFdjq8"
CHAT_ID    = "6772610365"
FETCH_INTERVAL = 15  # detik

# ── WIB UTC+7 ─────────────────────────────────────────────
WIB = timezone(timedelta(hours=7))

def now_wib():
    return datetime.now(WIB)

def get_session():
    t = now_wib().hour + now_wib().minute / 60
    if t < 9:   return "asia"
    if t < 14:  return "pre"
    if t < 22:  return "london"
    return "ny"

def market_open():
    n = datetime.now(timezone.utc)
    d, h = n.weekday(), n.hour  # 0=Mon, 6=Sun
    if d == 6: return False       # Minggu
    if d == 5: return False       # Sabtu
    if d == 4 and h >= 22: return False  # Jumat malam
    return True

# ── Telegram ──────────────────────────────────────────────
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[TG ERROR] {e}")
        return False

# ── Harga Gold ────────────────────────────────────────────
def fetch_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        data = r.json()
        return float(data["price"])
    except Exception as e:
        print(f"[PRICE ERROR] {e}")
        return None

# ── BOS Detection ─────────────────────────────────────────
def detect_bos(candles, lookback=5):
    if len(candles) < lookback + 2:
        return None
    recent = candles[-(lookback + 1):]
    last   = recent[-1]
    prev   = recent[:-1]
    swing_high = max(c["high"] for c in prev)
    swing_low  = min(c["low"]  for c in prev)
    if last["close"] > swing_high: return "BULL"
    if last["close"] < swing_low:  return "BEAR"
    return None

# ── Fibonacci ─────────────────────────────────────────────
def calc_fib(lo, hi):
    r = hi - lo
    return {
        "f0":   round(hi, 2),
        "f382": round(hi - r * 0.382, 2),
        "f618": round(hi - r * 0.618, 2),
        "f100": round(lo, 2),
    }

# ── State ─────────────────────────────────────────────────
state = {
    "candles":     [],
    "cur_candle":  None,
    "prev_price":  None,
    "asia_lo":     None,
    "asia_hi":     None,
    "fib":         None,
    "fib_locked":  False,
    "buy_done":    False,
    "sell_done":   False,
    "buy2_done":   False,
    "alerted":     set(),
    "last_day":    None,
}

def reset_daily():
    wib_now = now_wib()
    today   = wib_now.strftime("%Y-%m-%d")
    if state["last_day"] == today:
        return
    print(f"[RESET] Hari baru: {today}")
    state["asia_lo"]    = None
    state["asia_hi"]    = None
    state["fib"]        = None
    state["fib_locked"] = False
    state["buy_done"]   = False
    state["sell_done"]  = False
    state["buy2_done"]  = False
    state["alerted"]    = set()
    state["cur_candle"] = None
    state["last_day"]   = today
    send_telegram(
        f"🔄 *Reset Harian XAUUSD Bot*\n"
        f"📅 {today}\n"
        f"🕐 {wib_now.strftime('%H:%M')} WIB\n"
        f"Bot siap monitoring sesi Asia!"
    )

def signal(sig_type, price, detail):
    key = f"{sig_type}-{now_wib().strftime('%Y-%m-%d-%H-%M')[:13]}"
    if key in state["alerted"]:
        return
    state["alerted"].add(key)

    labels = {
        "BUY1": "📈 BUY — Sesi Asia",
        "SELL": "📉 SELL — London Open",
        "BUY2": "🔄 BUY ke-2 — Level 61.8%",
    }
    msg = (
        f"🥇 *XAUUSD SIGNAL M5*\n"
        f"━━━━━━━━━━━━━━\n"
        f"{labels[sig_type]}\n"
        f"💰 Harga: *${price:.2f}*\n"
        f"{detail}\n"
        f"🕐 {now_wib().strftime('%H:%M:%S')} WIB\n"
        f"━━━━━━━━━━━━━━\n"
        f"⚠️ _Bukan saran investasi_"
    )
    ok = send_telegram(msg)
    print(f"[SIGNAL] {labels[sig_type]} @ ${price:.2f} | TG: {ok}")

def process_candle(candle):
    if not market_open():
        return
    sess   = get_session()
    all_c  = state["candles"]
    b      = detect_bos(all_c)

    # ── Asia: tracking low & high ──────────────────────────
    if sess == "asia":
        lo = candle["low"]
        hi = candle["high"]
        state["asia_lo"] = lo if state["asia_lo"] is None else min(state["asia_lo"], lo)
        state["asia_hi"] = hi if state["asia_hi"] is None else max(state["asia_hi"], hi)

        if b == "BULL" and not state["buy_done"]:
            state["buy_done"] = True
            signal("BUY1", candle["close"],
                f"📍 Low Asia: *${state['asia_lo']:.2f}*\n"
                f"🎯 Target: High Asia *${state['asia_hi']:.2f}*\n"
                f"🛡 SL: Di bawah Low Asia\n"
                f"📊 TF: M5")

    # ── Pre/London: hitung Fib ─────────────────────────────
    if sess in ("pre", "london"):
        if state["asia_lo"] and state["asia_hi"] and not state["fib_locked"]:
            state["fib"]        = calc_fib(state["asia_lo"], state["asia_hi"])
            state["fib_locked"] = True
            f = state["fib"]
            print(f"[FIB] Lo={f['f100']} | 61.8%={f['f618']} | 38.2%={f['f382']} | Hi={f['f0']}")
            send_telegram(
                f"📐 *Fibonacci Terbentuk*\n"
                f"━━━━━━━━━━━━━━\n"
                f"🟦 Low Asia:  *${f['f100']:.2f}*\n"
                f"🟡 38.2%:    *${f['f382']:.2f}*\n"
                f"🔴 61.8%:    *${f['f618']:.2f}*\n"
                f"🟢 High Asia: *${f['f0']:.2f}*\n"
                f"🕐 {now_wib().strftime('%H:%M')} WIB"
            )

    # ── London: SELL & BUY2 ────────────────────────────────
    if sess == "london" and state["asia_hi"] and state["fib"]:
        hi = state["asia_hi"]
        f  = state["fib"]

        if abs(candle["close"] - hi) <= 8 and b == "BEAR" and not state["sell_done"]:
            state["sell_done"] = True
            signal("SELL", candle["close"],
                f"📍 High Asia: *${hi:.2f}*\n"
                f"🎯 TP: 61.8% *${f['f618']:.2f}*\n"
                f"🛡 SL: Di atas High Asia\n"
                f"📊 TF: M5")

        if abs(candle["close"] - f["f618"]) <= 8 and b == "BULL" and not state["buy2_done"]:
            state["buy2_done"] = True
            signal("BUY2", candle["close"],
                f"📍 Level 61.8%: *${f['f618']:.2f}*\n"
                f"🎯 TP: High Asia *${hi:.2f}*\n"
                f"🛡 SL: Di bawah 61.8%\n"
                f"📊 TF: M5")

# ── Main Loop ─────────────────────────────────────────────
def main():
    print("=" * 40)
    print("  XAUUSD Auto Alert Bot - M5")
    print("  gold-api.com | Telegram")
    print("=" * 40)

    send_telegram(
        f"🚀 *XAUUSD Bot Started!*\n"
        f"📡 API: gold-api.com (unlimited)\n"
        f"📊 Timeframe: M5\n"
        f"🕐 {now_wib().strftime('%d %b %Y %H:%M')} WIB\n"
        f"Bot siap mengirim sinyal BOS + Fibonacci!"
    )

    while True:
        try:
            reset_daily()
            price = fetch_price()

            if price:
                prev  = state["prev_price"]
                chg   = round(price - prev, 2) if prev else 0
                sess  = get_session()
                arrow = "▲" if chg >= 0 else "▼"
                print(f"[{now_wib().strftime('%H:%M:%S')}] ${price:.2f} {arrow}{abs(chg):.2f} | {sess} | Asia Lo:{state['asia_lo']} Hi:{state['asia_hi']}")

                # Build M5 candle
                mk = int(time.time() // 300)
                if state["cur_candle"] is None or state["cur_candle"]["mk"] != mk:
                    if state["cur_candle"] is not None:
                        closed = {k: state["cur_candle"][k] for k in ["open","high","low","close"]}
                        state["candles"] = state["candles"][-99:] + [closed]
                        process_candle(closed)
                    state["cur_candle"] = {
                        "mk": mk, "open": price,
                        "high": price, "low": price, "close": price
                    }
                else:
                    c = state["cur_candle"]
                    c["high"]  = max(c["high"], price)
                    c["low"]   = min(c["low"],  price)
                    c["close"] = price

                state["prev_price"] = price

        except KeyboardInterrupt:
            print("\n[STOP] Bot dihentikan.")
            send_telegram("⏹ *XAUUSD Bot dihentikan.*")
            break
        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    main()
