import requests
import time
import os
from datetime import datetime, timezone, timedelta

# ── Konfigurasi ───────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID   = os.environ.get("CHAT_ID")
FETCH_INTERVAL = 15
SR_TOLERANCE   = 10  # ±10 poin

if not BOT_TOKEN or not CHAT_ID:
    print("[ERROR] BOT_TOKEN dan CHAT_ID harus diset di environment variables!")
    exit(1)

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
    d, h = n.weekday(), n.hour
    if d == 6: return False
    if d == 5: return False
    if d == 4 and h >= 22: return False
    return True

# ── Telegram ──────────────────────────────────────────────
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"[TG ERROR] {e}")
        return False

def get_updates(offset=None):
    try:
        params = {"timeout": 1, "allowed_updates": ["message"]}
        if offset: params["offset"] = offset
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params=params, timeout=5)
        return r.json().get("result", [])
    except:
        return []

# ── Harga Gold ────────────────────────────────────────────
def fetch_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        return float(r.json()["price"])
    except Exception as e:
        print(f"[PRICE ERROR] {e}")
        return None

# ── Indikator ─────────────────────────────────────────────
def detect_bos(candles, lb=5):
    if len(candles) < lb + 2: return None
    rec = candles[-(lb+1):]
    last, prev = rec[-1], rec[:-1]
    if last["close"] > max(c["high"] for c in prev): return "BULL"
    if last["close"] < min(c["low"]  for c in prev): return "BEAR"
    return None

def detect_rejection(c):
    body = abs(c["close"] - c["open"])
    uw   = c["high"] - max(c["open"], c["close"])
    lw   = min(c["open"], c["close"]) - c["low"]
    tot  = c["high"] - c["low"]
    if tot == 0: return None
    if lw > body * 1.5 and lw > tot * 0.4: return "BULLISH"
    if uw > body * 1.5 and uw > tot * 0.4: return "BEARISH"
    return None

def calc_fib(lo, hi):
    r = hi - lo
    return {
        "f0":   round(hi, 2),
        "f382": round(hi - r * 0.382, 2),
        "f618": round(hi - r * 0.618, 2),
        "f100": round(lo, 2),
    }

# ── Auto S&R Detection ────────────────────────────────────
def get_auto_sr(candles, current_price):
    levels = []
    if len(candles) < 10:
        return levels

    # ── 1. PDH / PDL (1 hari = 288 candle M5) ────────────
    day = 288
    if len(candles) >= day * 2:
        yesterday = candles[-(day*2):-(day)]
        pdh = round(max(c["high"] for c in yesterday), 2)
        pdl = round(min(c["low"]  for c in yesterday), 2)
        levels.append({"price": pdh, "label": "PDH (High Kemarin)", "type": "resistance"})
        levels.append({"price": pdl, "label": "PDL (Low Kemarin)",  "type": "support"})
    elif len(candles) >= day:
        prev = candles[:-(min(len(candles)//2, day))]
        if prev:
            levels.append({"price": round(max(c["high"] for c in prev), 2), "label": "PDH", "type": "resistance"})
            levels.append({"price": round(min(c["low"]  for c in prev), 2), "label": "PDL", "type": "support"})

    # ── 2. Weekly High / Low (1 minggu = 2016 candle M5) ──
    week = 2016
    if len(candles) >= week:
        wk = candles[-week:]
        wkh = round(max(c["high"] for c in wk), 2)
        wkl = round(min(c["low"]  for c in wk), 2)
        levels.append({"price": wkh, "label": "Weekly High", "type": "resistance"})
        levels.append({"price": wkl, "label": "Weekly Low",  "type": "support"})
    elif len(candles) >= day * 3:
        wk = candles[-(day*3):]
        levels.append({"price": round(max(c["high"] for c in wk), 2), "label": "Weekly High (~3d)", "type": "resistance"})
        levels.append({"price": round(min(c["low"]  for c in wk), 2), "label": "Weekly Low (~3d)",  "type": "support"})

    # ── 3. Monthly High / Low (1 bulan = ~8640 candle M5) ─
    month = 8640
    if len(candles) >= month:
        mo = candles[-month:]
        moh = round(max(c["high"] for c in mo), 2)
        mol = round(min(c["low"]  for c in mo), 2)
        levels.append({"price": moh, "label": "Monthly High", "type": "resistance"})
        levels.append({"price": mol, "label": "Monthly Low",  "type": "support"})
    elif len(candles) >= day * 7:
        mo = candles[-(day*7):]
        levels.append({"price": round(max(c["high"] for c in mo), 2), "label": "Monthly High (~7d)", "type": "resistance"})
        levels.append({"price": round(min(c["low"]  for c in mo), 2), "label": "Monthly Low (~7d)",  "type": "support"})

    # ── 4. Round Numbers ($100 interval) ──────────────────
    base = int(current_price / 100) * 100
    for mult in range(-3, 5):
        rn = base + mult * 100
        if rn > 0:
            diff = abs(current_price - rn)
            if diff <= 150:  # tampilkan round number dalam range ±150
                rn_type = "resistance" if rn > current_price else "support"
                levels.append({"price": float(rn), "label": f"Round Number ${rn}", "type": rn_type})

    # ── 5. Half Round Numbers ($50 interval) ──────────────
    base50 = int(current_price / 50) * 50
    for mult in range(-2, 4):
        rn = base50 + mult * 50
        if rn % 100 != 0 and rn > 0:  # skip yang sudah ada di round 100
            diff = abs(current_price - rn)
            if diff <= 80:
                rn_type = "resistance" if rn > current_price else "support"
                levels.append({"price": float(rn), "label": f"Half Round ${rn}", "type": rn_type})

    # Hapus duplikat level yang terlalu dekat (< 5 poin)
    unique = []
    for lv in sorted(levels, key=lambda x: x["price"]):
        if not unique or abs(lv["price"] - unique[-1]["price"]) >= 5:
            unique.append(lv)

    return unique

# ── State ─────────────────────────────────────────────────
state = {
    "candles":    [],
    "cur_candle": None,
    "prev_price": None,
    "asia_lo":    None,
    "asia_hi":    None,
    "fib":        None,
    "fib_locked": False,
    "buy_done":   False,
    "sell_done":  False,
    "buy2_done":  False,
    "alerted":    set(),
    "sr_alerted": set(),
    "last_day":   None,
    "last_update": 0,
}

def reset_daily():
    today = now_wib().strftime("%Y-%m-%d")
    if state["last_day"] == today: return
    print(f"[RESET] Hari baru: {today}")
    state.update({
        "asia_lo": None, "asia_hi": None,
        "fib": None, "fib_locked": False,
        "buy_done": False, "sell_done": False, "buy2_done": False,
        "alerted": set(), "sr_alerted": set(),
        "cur_candle": None, "last_day": today
    })
    send_telegram(
        f"🔄 *Reset Harian XAUUSD Bot*\n"
        f"📅 {today} | 🕐 {now_wib().strftime('%H:%M')} WIB\n"
        f"━━━━━━━━━━━━━━\n"
        f"Bot siap monitoring sesi Asia!\n"
        f"S&R otomatis aktif 🤖\n"
        f"Ketik /help untuk commands"
    )

# ── Signal BOS Asia/London ────────────────────────────────
def signal(sig_type, price, detail):
    key = f"{sig_type}-{now_wib().strftime('%Y-%m-%d-%H')}"
    if key in state["alerted"]: return
    state["alerted"].add(key)
    labels = {
        "BUY1": "📈 BUY — Sesi Asia",
        "SELL": "📉 SELL — London Open",
        "BUY2": "🔄 BUY ke-2 — Level 61.8%",
    }
    send_telegram(
        f"🥇 *XAUUSD SIGNAL M5*\n"
        f"━━━━━━━━━━━━━━\n"
        f"{labels[sig_type]}\n"
        f"💰 Harga: *${price:.2f}*\n"
        f"{detail}\n"
        f"🕐 {now_wib().strftime('%H:%M:%S')} WIB\n"
        f"━━━━━━━━━━━━━━\n"
        f"⚠️ _Bukan saran investasi_"
    )
    print(f"[SIGNAL] {labels[sig_type]} @ ${price:.2f}")

# ── Cek S&R Otomatis ──────────────────────────────────────
def check_sr(candle, all_candles):
    if not market_open(): return
    price    = candle["close"]
    b        = detect_bos(all_candles)
    rej      = detect_rejection(candle)
    auto_sr  = get_auto_sr(all_candles, price)

    for sr in auto_sr:
        level   = sr["price"]
        label   = sr["label"]
        sr_type = sr["type"]

        if abs(price - level) > SR_TOLERANCE:
            continue

        # Touch
        touch_key = f"touch-{label}-{now_wib().strftime('%Y-%m-%d-%H')}"
        if touch_key not in state["sr_alerted"]:
            state["sr_alerted"].add(touch_key)
            emoji = "🔴" if sr_type == "resistance" else "🟢"
            send_telegram(
                f"📍 *Harga Menyentuh {sr_type.upper()}*\n"
                f"━━━━━━━━━━━━━━\n"
                f"{emoji} *{label}*: ${level:.2f}\n"
                f"💰 Harga: *${price:.2f}*\n"
                f"📏 Jarak: {abs(price-level):.1f} poin\n"
                f"🕐 {now_wib().strftime('%H:%M:%S')} WIB\n"
                f"⏳ _Tunggu konfirmasi candle..._"
            )
            print(f"[SR TOUCH] {label} @ ${price:.2f}")

        # Rejection
        if rej:
            rej_key = f"rej-{label}-{now_wib().strftime('%Y-%m-%d-%H-%M')}"
            if rej_key not in state["sr_alerted"]:
                state["sr_alerted"].add(rej_key)
                action = "BUY 📈" if rej == "BULLISH" else "SELL 📉"
                send_telegram(
                    f"🕯 *Rejection di {sr_type.upper()}!*\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"*{action}* Signal\n"
                    f"📍 {label}: *${level:.2f}*\n"
                    f"💰 Harga: *${price:.2f}*\n"
                    f"🕯 Pola: {rej} Rejection\n"
                    f"🕐 {now_wib().strftime('%H:%M:%S')} WIB\n"
                    f"📊 TF: M5"
                )
                print(f"[SR REJ] {rej} @ {label} ${price:.2f}")

        # BOS konfirmasi
        if b:
            bos_key = f"bos-{label}-{b}-{now_wib().strftime('%Y-%m-%d-%H-%M')}"
            if bos_key not in state["sr_alerted"]:
                state["sr_alerted"].add(bos_key)
                if b == "BULL" and sr_type == "support":
                    send_telegram(
                        f"💥 *BOS Bullish di SUPPORT!*\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"📈 *KONFIRMASI BUY*\n"
                        f"📍 {label}: *${level:.2f}*\n"
                        f"💰 Harga: *${price:.2f}*\n"
                        f"✅ BOS terkonfirmasi M5\n"
                        f"🎯 Target: Resistance terdekat\n"
                        f"🛡 SL: Di bawah {label}\n"
                        f"🕐 {now_wib().strftime('%H:%M:%S')} WIB"
                    )
                elif b == "BEAR" and sr_type == "resistance":
                    send_telegram(
                        f"💥 *BOS Bearish di RESISTANCE!*\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"📉 *KONFIRMASI SELL*\n"
                        f"📍 {label}: *${level:.2f}*\n"
                        f"💰 Harga: *${price:.2f}*\n"
                        f"✅ BOS terkonfirmasi M5\n"
                        f"🎯 Target: Support terdekat\n"
                        f"🛡 SL: Di atas {label}\n"
                        f"🕐 {now_wib().strftime('%H:%M:%S')} WIB"
                    )
                print(f"[SR BOS] {b} @ {label} ${price:.2f}")

# ── Process Candle ────────────────────────────────────────
def process_candle(candle):
    if not market_open(): return
    sess  = get_session()
    all_c = state["candles"]
    b     = detect_bos(all_c)

    check_sr(candle, all_c)

    if sess == "asia":
        state["asia_lo"] = candle["low"]  if state["asia_lo"] is None else min(state["asia_lo"], candle["low"])
        state["asia_hi"] = candle["high"] if state["asia_hi"] is None else max(state["asia_hi"], candle["high"])
        if b == "BULL" and not state["buy_done"]:
            state["buy_done"] = True
            signal("BUY1", candle["close"],
                f"📍 Low Asia: *${state['asia_lo']:.2f}*\n"
                f"🎯 Target: High Asia *${state['asia_hi']:.2f}*\n"
                f"🛡 SL: Di bawah Low Asia\n📊 TF: M5")

    if sess in ("pre", "london"):
        if state["asia_lo"] and state["asia_hi"] and not state["fib_locked"]:
            state["fib"]        = calc_fib(state["asia_lo"], state["asia_hi"])
            state["fib_locked"] = True
            f = state["fib"]
            send_telegram(
                f"📐 *Fibonacci Terbentuk*\n"
                f"━━━━━━━━━━━━━━\n"
                f"🟦 Low Asia:  *${f['f100']:.2f}*\n"
                f"🟡 38.2%:    *${f['f382']:.2f}*\n"
                f"🔴 61.8%:    *${f['f618']:.2f}*\n"
                f"🟢 High Asia: *${f['f0']:.2f}*\n"
                f"🕐 {now_wib().strftime('%H:%M')} WIB"
            )

    if sess == "london" and state["asia_hi"] and state["fib"]:
        hi, f = state["asia_hi"], state["fib"]
        if abs(candle["close"] - hi) <= 8 and b == "BEAR" and not state["sell_done"]:
            state["sell_done"] = True
            signal("SELL", candle["close"],
                f"📍 High Asia: *${hi:.2f}*\n"
                f"🎯 TP: 61.8% *${f['f618']:.2f}*\n"
                f"🛡 SL: Di atas High Asia\n📊 TF: M5")
        if abs(candle["close"] - f["f618"]) <= 8 and b == "BULL" and not state["buy2_done"]:
            state["buy2_done"] = True
            signal("BUY2", candle["close"],
                f"📍 Level 61.8%: *${f['f618']:.2f}*\n"
                f"🎯 TP: High Asia *${hi:.2f}*\n"
                f"🛡 SL: Bawah 61.8%\n📊 TF: M5")

# ── Command Handler ───────────────────────────────────────
def handle_commands():
    updates = get_updates(offset=state["last_update"])
    for upd in updates:
        state["last_update"] = upd["update_id"] + 1
        text = upd.get("message", {}).get("text", "").strip()
        if not text: continue
        print(f"[CMD] {text}")

        if text in ("/start", "/help"):
            send_telegram(
                f"🥇 *XAUUSD Bot v3 - Auto S&R*\n"
                f"━━━━━━━━━━━━━━\n"
                f"/status → Harga & status bot\n"
                f"/listsr → Semua level S&R aktif\n"
                f"/help   → Menu ini\n"
                f"━━━━━━━━━━━━━━\n"
                f"🤖 S&R otomatis:\n"
                f"• PDH/PDL (High Low kemarin)\n"
                f"• Weekly High/Low\n"
                f"• Monthly High/Low\n"
                f"• Round Numbers ($100, $50)\n"
                f"━━━━━━━━━━━━━━\n"
                f"Bot aktif 24 jam • M5 • gold-api.com"
            )

        elif text == "/status":
            p = state["prev_price"]
            sr_count = len(get_auto_sr(state["candles"], p or 0))
            send_telegram(
                f"📊 *Status Bot XAUUSD*\n"
                f"━━━━━━━━━━━━━━\n"
                f"💰 Harga: *${p:.2f}*\n"
                f"🌏 Sesi: *{get_session()}*\n"
                f"📍 Low Asia: *${state['asia_lo']:.2f}*\n" if state["asia_lo"] else
                f"📍 Low Asia: Belum ada\n"
                f"📍 High Asia: *${state['asia_hi']:.2f}*\n" if state["asia_hi"] else
                f"📍 High Asia: Belum ada\n"
                f"📐 Fib: {'✅ Aktif' if state['fib'] else '⏳ Belum'}\n"
                f"📈 BUY Asia: {'✅' if state['buy_done'] else '⏳'}\n"
                f"📉 SELL London: {'✅' if state['sell_done'] else '⏳'}\n"
                f"🔄 BUY 61.8%: {'✅' if state['buy2_done'] else '⏳'}\n"
                f"🎯 Level S&R aktif: {sr_count}\n"
                f"🕐 {now_wib().strftime('%H:%M:%S')} WIB"
            )

        elif text == "/listsr":
            p = state["prev_price"] or 0
            levels = get_auto_sr(state["candles"], p)
            if not levels:
                send_telegram("⏳ Data S&R belum cukup. Tunggu beberapa jam lagi.")
            else:
                res = [l for l in levels if l["type"] == "resistance" and l["price"] > p]
                sup = [l for l in levels if l["type"] == "support"    and l["price"] < p]
                res = sorted(res, key=lambda x: x["price"])[:5]
                sup = sorted(sup, key=lambda x: x["price"], reverse=True)[:5]
                msg = [f"📋 *Level S&R Aktif* (harga: ${p:.2f})\n"]
                if res:
                    msg.append("🔴 *Resistance:*")
                    for l in res:
                        msg.append(f"  • {l['label']}: *${l['price']:.2f}* (+{l['price']-p:.1f})")
                if sup:
                    msg.append("\n🟢 *Support:*")
                    for l in sup:
                        msg.append(f"  • {l['label']}: *${l['price']:.2f}* (-{p-l['price']:.1f})")
                send_telegram("\n".join(msg))

# ── Main Loop ─────────────────────────────────────────────
def main():
    print("=" * 45)
    print("  XAUUSD Auto Alert Bot v3 - M5")
    print("  BOS + Fibonacci + Auto S&R")
    print("  PDH/PDL + Weekly + Monthly + Round Numbers")
    print("=" * 45)

    send_telegram(
        f"🚀 *XAUUSD Bot v3 Started!*\n"
        f"━━━━━━━━━━━━━━\n"
        f"📡 API: gold-api.com (unlimited)\n"
        f"📊 Timeframe: M5\n"
        f"🤖 *Auto S&R aktif:*\n"
        f"• PDH / PDL\n"
        f"• Weekly High / Low\n"
        f"• Monthly High / Low\n"
        f"• Round Numbers ($100 & $50)\n"
        f"🔒 Token: environment variable ✅\n"
        f"🕐 {now_wib().strftime('%d %b %Y %H:%M')} WIB\n"
        f"Ketik /help untuk commands!"
    )

    while True:
        try:
            reset_daily()
            handle_commands()
            price = fetch_price()

            if price:
                prev  = state["prev_price"]
                chg   = round(price - prev, 2) if prev else 0
                arrow = "▲" if chg >= 0 else "▼"
                sess  = get_session()
                print(f"[{now_wib().strftime('%H:%M:%S')}] ${price:.2f} {arrow}{abs(chg):.2f} | {sess} | Lo:{state['asia_lo']} Hi:{state['asia_hi']}")

                mk = int(time.time() // 300)
                if state["cur_candle"] is None or state["cur_candle"]["mk"] != mk:
                    if state["cur_candle"] is not None:
                        closed = {k: state["cur_candle"][k] for k in ["open","high","low","close"]}
                        state["candles"] = state["candles"][-8640:] + [closed]
                        process_candle(closed)
                    state["cur_candle"] = {"mk": mk, "open": price, "high": price, "low": price, "close": price}
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
