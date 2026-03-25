import requests
import time
import os
import math
from datetime import datetime, timezone, timedelta


SINARMAS_CALENDAR = {
    1: {1:"U",2:"O",3:"L",4:"L",5:"O",6:"O",7:"L",8:"L",9:"U",10:"L",
        11:"L",12:"O",13:"U",14:"O",15:"O",16:"L",17:"L",18:"L",19:"L",
        20:"L",21:"U",22:"L",23:"L",24:"O",25:"U",26:"O",27:"L",28:"L",
        29:"L",30:"O",31:"L"},
    2: {1:"O",2:"U",3:"U",4:"L",5:"O",6:"L",7:"U",8:"O",9:"O",10:"L",
        11:"L",12:"O",13:"L",14:"O",15:"U",16:"L",17:"L",18:"O",19:"U",
        20:"O",21:"L",22:"L",23:"O",24:"O",25:"L",26:"L",27:"U",28:"L"},
    3: {1:"U",2:"U",3:"U",4:"O",5:"L",6:"O",7:"O",8:"O",9:"O",10:"L",
        11:"L",12:"U",13:"L",14:"L",15:"U",16:"O",17:"O",18:"O",19:"U",
        20:"L",21:"O",22:"L",23:"O",24:"U",25:"U",26:"L",27:"U",28:"O",
        29:"L",30:"O",31:"L"},
    4: {1:"L",2:"O",3:"L",4:"O",5:"L",6:"U",7:"O",8:"U",9:"O",10:"L",
        11:"O",12:"O",13:"O",14:"O",15:"O",16:"L",17:"L",18:"U",19:"O",
        20:"U",21:"L",22:"O",23:"O",24:"O",25:"L",26:"O",27:"O",28:"L",
        29:"L",30:"U"},
    5: {1:"U",2:"U",3:"L",4:"U",5:"O",6:"L",7:"L",8:"L",9:"O",10:"L",
        11:"O",12:"O",13:"U",14:"U",15:"O",16:"L",17:"L",18:"O",19:"O",
        20:"L",21:"L",22:"O",23:"O",24:"L",25:"U",26:"U",27:"L",28:"O",
        29:"O",30:"L",31:"L"},
    6: {1:"O",2:"O",3:"O",4:"L",5:"L",6:"O",7:"U",8:"O",9:"L",10:"O",
        11:"L",12:"O",13:"O",14:"L",15:"L",16:"L",17:"L",18:"O",19:"U",
        20:"U",21:"L",22:"O",23:"O",24:"O",25:"O",26:"L",27:"L",28:"L",
        29:"L",30:"U"},
    7: {1:"U",2:"O",3:"L",4:"O",5:"L",6:"O",7:"O",8:"L",9:"L",10:"O",
        11:"O",12:"L",13:"U",14:"U",15:"L",16:"L",17:"O",18:"O",19:"L",
        20:"O",21:"L",22:"O",23:"L",24:"O",25:"U",26:"U",27:"L",28:"L",
        29:"L",30:"O",31:"O"},
    8: {1:"O",2:"O",3:"L",4:"O",5:"L",6:"U",7:"U",8:"U",9:"O",10:"O",
        11:"L",12:"U",13:"O",14:"L",15:"O",16:"L",17:"O",18:"U",19:"O",
        20:"U",21:"L",22:"L",23:"L",24:"O",25:"L",26:"L",27:"L",28:"U",
        29:"U",30:"U",31:"L"},
    9: {1:"U",2:"O",3:"L",4:"L",5:"L",6:"O",7:"O",8:"O",9:"O",10:"L",
        11:"U",12:"L",13:"O",14:"U",15:"L",16:"L",17:"O",18:"L",19:"L",
        20:"L",21:"O",22:"U",23:"U",24:"O",25:"L",26:"U",27:"O",28:"L",
        29:"O",30:"L"},
    10:{1:"L",2:"O",3:"L",4:"L",5:"U",6:"L",7:"O",8:"U",9:"U",10:"O",
        11:"L",12:"O",13:"L",14:"O",15:"L",16:"O",17:"U",18:"L",19:"L",
        20:"O",21:"U",22:"U",23:"L",24:"O",25:"L",26:"L",27:"O",28:"U",
        29:"U",30:"O",31:"O"},
    11:{1:"L",2:"U",3:"L",4:"L",5:"O",6:"U",7:"O",8:"O",9:"O",10:"U",
        11:"O",12:"L",13:"L",14:"O",15:"U",16:"L",17:"L",18:"O",19:"L",
        20:"O",21:"O",22:"U",23:"L",24:"L",25:"L",26:"L",27:"U",28:"O",
        29:"L",30:"O"},
    12:{1:"L",2:"O",3:"O",4:"U",5:"O",6:"L",7:"O",8:"L",9:"O",10:"U",
        11:"O",12:"L",13:"O",14:"L",15:"O",16:"U",17:"L",18:"O",19:"O",
        20:"L",21:"U",22:"U",23:"O",24:"L",25:"L",26:"O",27:"U",28:"U",
        29:"L",30:"L",31:"O"},
}

def get_luck_status(date=None):
    """Ambil status luck hari ini dari kalender Sinarmas"""
    if date is None:
        date = now_wita()
    month = date.month
    day   = date.day
    status = SINARMAS_CALENDAR.get(month, {}).get(day, "O")
    if status == "L":
        return {
            "status": "LUCKY",
            "emoji": "🍀",
            "label": "🍀 LUCKY DAY",
            "color": "MERAH",
            "desc": "Hari baik untuk trading! Energi positif mendukung keputusan.",
            "trading": "✅ Hari bagus untuk entry\n✅ Percayai setup yang valid\n✅ Target bisa lebih agresif"
        }
    elif status == "U":
        return {
            "status": "UNLUCKY",
            "emoji": "⚠️",
            "label": "⚠️ UNLUCKY DAY",
            "color": "HITAM",
            "desc": "Hari kurang baik. Hindari keputusan besar & overtrading.",
            "trading": "⛔ Kurangi ukuran posisi\n⚠️ Hindari FOMO\n❌ Skip kalau setup tidak jelas"
        }
    else:
        return {
            "status": "ORDINARY",
            "emoji": "📅",
            "label": "📅 ORDINARY DAY",
            "color": "HIJAU",
            "desc": "Hari biasa. Trading normal sesuai metode.",
            "trading": "✅ Trading normal\n✅ Ikuti setup seperti biasa"
        }


BOT_TOKEN = os.environ.get("7660942709:AAHjvW4sLMeUFlyEKui_fCaJoUa5JGrZzoY")
CHAT_ID   = os.environ.get("5402843009")
FETCH_INTERVAL = 15
SR_TOLERANCE   = 10

if not BOT_TOKEN or not CHAT_ID:
    print("[ERROR] BOT_TOKEN dan CHAT_ID harus diset!")
    exit(1)

# WITA = UTC+8
WITA = timezone(timedelta(hours=8))
WIB  = timezone(timedelta(hours=7))

def now_wita():
    return datetime.now(WITA)

def now_wib():
    return datetime.now(WIB)

def get_session():
    t = now_wita().hour + now_wita().minute / 60
    if t < 10:  return "asia"
    if t < 15:  return "pre"
    if t < 23:  return "london"
    return "ny"

def market_open():
    n = datetime.now(timezone.utc)
    d, h = n.weekday(), n.hour
    if d == 6: return False
    if d == 5: return False
    if d == 4 and h >= 22: return False
    return True

def get_day_name():
    days = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
    return days[now_wita().weekday()]

def get_month_name(m=None):
    months = ["","Januari","Februari","Maret","April","Mei","Juni",
              "Juli","Agustus","September","Oktober","November","Desember"]
    return months[m or now_wita().month]

# ── Killzone Schedule (WITA) ──────────────────────────────
KILLZONES = [
    {
        "name":    "Asian Killzone",
        "emoji":   "🌏",
        "start_h": 1, "start_m": 0,
        "end_h":   4, "end_m":   0,
        "desc":    "Sesi Asia dimulai! Low & High Asia mulai terbentuk.",
        "action":  "✅ Tracking Low & High Asia\n✅ Catat range Asia\n⚠️ Jangan entry dulu",
        "danger":  False,
    },
    {
        "name":    "Pre-London Aktif",
        "emoji":   "⏳",
        "start_h": 10, "start_m": 0,
        "end_h":   15, "end_m":   0,
        "desc":    "Market mulai bersiap. Volume mulai naik.",
        "action":  "✅ Tandai High & Low Asia\n✅ Tarik Fibonacci\n⏳ Standby untuk London",
        "danger":  False,
    },
    {
        "name":    "LONDON OPEN — JUDAS SWING!",
        "emoji":   "🇬🇧",
        "start_h": 15, "start_m": 0,
        "end_h":   15, "end_m":   30,
        "desc":    "BAHAYA! London open = zona Judas Swing. Fake move sering terjadi ke atas/bawah sebelum arah asli terbentuk!",
        "action":  "⛔ JANGAN entry sekarang!\n⚠️ Tunggu sweep selesai\n👀 Pantau High & Low Asia\n📐 Siap entry di 61.8%",
        "danger":  True,
    },
    {
        "name":    "London Main — Entry Zone",
        "emoji":   "✅",
        "start_h": 15, "start_m": 30,
        "end_h":   18, "end_m":   0,
        "desc":    "Judas Swing selesai. Arah dominan London mulai terbentuk. Ini waktu entry terbaik!",
        "action":  "✅ Cari BOS konfirmasi\n✅ Entry di 61.8% Fib\n✅ Sweep Low Asia → BUY\n🎯 Target High Asia",
        "danger":  False,
    },
    {
        "name":    "LONDON-NY OVERLAP — PALING VOLATILE!",
        "emoji":   "🔥",
        "start_h": 20, "start_m": 0,
        "end_h":   21, "end_m":   30,
        "desc":    "Overlap London-NY! Pergerakan TERBESAR hari ini. Volume sangat tinggi. Peluang dan risiko sama besar!",
        "action":  "🔥 Volume paling tinggi!\n✅ Entry kalau belum dapat setup\n⚠️ SL wajib lebih lebar\n🎯 Target besar possible",
        "danger":  False,
    },
    {
        "name":    "NYSE Open — Data US!",
        "emoji":   "🇺🇸",
        "start_h": 21, "start_m": 30,
        "end_h":   22, "end_m":   0,
        "desc":    "NYSE open! Data ekonomi US sering keluar. Displacement besar bisa terjadi tiba-tiba.",
        "action":  "⚠️ Waspada data ekonomi US\n✅ SL sudah di profit?\n✅ Konfirmasi arah hari ini\n📊 Arah NY = arah dominan",
        "danger":  False,
    },
    {
        "name":    "NY Main Session",
        "emoji":   "🇺🇸",
        "start_h": 22, "start_m": 0,
        "end_h":   23, "end_m":   59,
        "desc":    "New York session utama. Konfirmasi arah dominan hari ini.",
        "action":  "✅ Hold posisi yang sudah profit\n✅ Partial close jika sudah target\n⚠️ Jangan buka posisi baru besar",
        "danger":  False,
    },
    {
        "name":    "London Close — Reversal Zone",
        "emoji":   "🔚",
        "start_h": 0, "start_m": 0,
        "end_h":   2, "end_m":   0,
        "desc":    "London tutup. Institusi London menutup posisi. Sering terjadi reversal dari tren hari ini.",
        "action":  "⚠️ Reversal mungkin terjadi!\n✅ Pertimbangkan close posisi\n✅ Jangan buka posisi baru\n🌙 Persiapkan Asia besok",
        "danger":  False,
    },
]

def get_current_killzone():
    now = now_wita()
    h, m = now.hour, now.minute
    t = h * 60 + m
    for kz in KILLZONES:
        start = kz["start_h"] * 60 + kz["start_m"]
        end   = kz["end_h"]   * 60 + kz["end_m"]
        if start <= t < end:
            return kz
    return None

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

# ── 🕯️ CANDLE PATTERNS ───────────────────────────────────
def analyze_candle(candles):
    if len(candles) < 3: return None
    c1, c2, c3 = candles[-1], candles[-2], candles[-3]
    body1  = abs(c1["close"] - c1["open"])
    body2  = abs(c2["close"] - c2["open"])
    body3  = abs(c3["close"] - c3["open"])
    uw1    = c1["high"] - max(c1["open"], c1["close"])
    lw1    = min(c1["open"], c1["close"]) - c1["low"]
    total1 = c1["high"] - c1["low"]
    uw2    = c2["high"] - max(c2["open"], c2["close"])
    lw2    = min(c2["open"], c2["close"]) - c2["low"]
    bull1  = c1["close"] > c1["open"]
    bear1  = c1["close"] < c1["open"]
    bull2  = c2["close"] > c2["open"]
    bear2  = c2["close"] < c2["open"]
    patterns = []

    # TIER 1
    if bull1 and bear2 and c1["open"] <= c2["close"] and c1["close"] >= c2["open"] and body1 > body2 * 0.8:
        patterns.append({"tier":1,"bias":"BULL","name":"🔴 Bullish Engulfing","emoji":"📈",
            "desc":"Buyer mengambil alih! Candle hijau menelan candle merah.","action":"✅ BUY kuat! Konfirmasi BOS."})
    if bear1 and bull2 and c1["open"] >= c2["close"] and c1["close"] <= c2["open"] and body1 > body2 * 0.8:
        patterns.append({"tier":1,"bias":"BEAR","name":"🔴 Bearish Engulfing","emoji":"📉",
            "desc":"Seller mengambil alih! Candle merah menelan candle hijau.","action":"✅ SELL kuat! Konfirmasi BOS."})
    if total1 > 0 and lw1 > body1*2.0 and lw1 > total1*0.5 and uw1 < body1*0.5:
        patterns.append({"tier":1,"bias":"BULL","name":"🔴 Bullish Pin Bar","emoji":"📈",
            "desc":"Rejection kuat ke bawah! Seller gagal.","action":"✅ BUY kuat di support/61.8%!"})
    if total1 > 0 and uw1 > body1*2.0 and uw1 > total1*0.5 and lw1 < body1*0.5:
        patterns.append({"tier":1,"bias":"BEAR","name":"🔴 Bearish Pin Bar","emoji":"📉",
            "desc":"Rejection kuat ke atas! Buyer gagal.","action":"✅ SELL kuat di resistance/61.8%!"})
    if bear2 and bull1 and body2 < body3*0.3 and c3["close"] < c3["open"] and c1["close"] > (c3["open"]+c3["close"])/2:
        patterns.append({"tier":1,"bias":"BULL","name":"🔴 Morning Star ⭐","emoji":"📈",
            "desc":"3 candle reversal! Merah+Doji+Hijau. Sangat kuat!","action":"✅ BUY setup sangat kuat!"})
    if bull2 and bear1 and body2 < body3*0.3 and c3["close"] > c3["open"] and c1["close"] < (c3["open"]+c3["close"])/2:
        patterns.append({"tier":1,"bias":"BEAR","name":"🔴 Evening Star ⭐","emoji":"📉",
            "desc":"3 candle reversal! Hijau+Doji+Merah. Sangat kuat!","action":"✅ SELL setup sangat kuat!"})

    # TIER 2
    if total1 > 0 and lw1 > body1*1.5 and lw1 > total1*0.4 and uw1 < body1*1.0 and bull1:
        patterns.append({"tier":2,"bias":"BULL","name":"🟡 Hammer 🔨","emoji":"📈",
            "desc":"Ekor bawah panjang di support.","action":"⏳ Watch! Tunggu candle konfirmasi."})
    if total1 > 0 and uw1 > body1*1.5 and uw1 > total1*0.4 and lw1 < body1*1.0 and bear1:
        patterns.append({"tier":2,"bias":"BEAR","name":"🟡 Shooting Star ⭐","emoji":"📉",
            "desc":"Ekor atas panjang di resistance.","action":"⏳ Watch! Tunggu candle konfirmasi."})
    if abs(c1["low"]-c2["low"]) < 3 and bear2 and bull1:
        patterns.append({"tier":2,"bias":"BULL","name":"🟡 Tweezer Bottom","emoji":"📈",
            "desc":"Double low! Support sangat kuat.","action":"⏳ Watch! Double bottom terkonfirmasi."})
    if abs(c1["high"]-c2["high"]) < 3 and bull2 and bear1:
        patterns.append({"tier":2,"bias":"BEAR","name":"🟡 Tweezer Top","emoji":"📉",
            "desc":"Double high! Resistance sangat kuat.","action":"⏳ Watch! Double top terkonfirmasi."})
    if bull1 and bear2 and c1["open"] > c2["close"] and c1["close"] < c2["open"] and body1 < body2*0.5:
        patterns.append({"tier":2,"bias":"BULL","name":"🟡 Bullish Harami","emoji":"📈",
            "desc":"Candle kecil hijau dalam candle merah besar.","action":"⏳ Watch! Tunggu BOS bullish."})
    if bear1 and bull2 and c1["open"] < c2["close"] and c1["close"] > c2["open"] and body1 < body2*0.5:
        patterns.append({"tier":2,"bias":"BEAR","name":"🟡 Bearish Harami","emoji":"📉",
            "desc":"Candle kecil merah dalam candle hijau besar.","action":"⏳ Watch! Tunggu BOS bearish."})

    # TIER 3
    if total1 > 0 and body1 < total1*0.1 and total1 > 5:
        doji_type = "Dragonfly" if lw1 > uw1*2 else "Gravestone" if uw1 > lw1*2 else "Doji"
        doji_bias = "BULL" if lw1 > uw1 else "BEAR"
        patterns.append({"tier":3,"bias":doji_bias,"name":f"🟢 {doji_type} Doji","emoji":"⚠️",
            "desc":"Kebimbangan market!","action":"ℹ️ Info. Tunggu candle berikutnya."})
    if c1["high"] < c2["high"] and c1["low"] > c2["low"]:
        patterns.append({"tier":3,"bias":"NEUTRAL","name":"🟢 Inside Bar","emoji":"⏸️",
            "desc":"Konsolidasi. Breakout akan terjadi!","action":"ℹ️ Siapkan entry breakout!"})
    if bull1 and total1 > 0 and body1 > total1*0.85 and body1 > 15:
        patterns.append({"tier":3,"bias":"BULL","name":"🟢 Bullish Marubozu","emoji":"📈",
            "desc":"Momentum bullish kuat!","action":"ℹ️ BUY di pullback berikutnya."})
    if bear1 and total1 > 0 and body1 > total1*0.85 and body1 > 15:
        patterns.append({"tier":3,"bias":"BEAR","name":"🟢 Bearish Marubozu","emoji":"📉",
            "desc":"Momentum bearish kuat!","action":"ℹ️ SELL di rally berikutnya."})

    return patterns if patterns else None

def calc_fib(lo, hi):
    r = hi - lo
    return {
        "f0":   round(hi, 2),   "f382": round(hi-r*0.382, 2),
        "f618": round(hi-r*0.618, 2), "f786": round(hi-r*0.786, 2),
        "f100": round(lo, 2),   "f127": round(lo-r*0.272, 2),
        "f161": round(lo-r*0.618, 2),
    }

def detect_bos(candles, lb=5):
    if len(candles) < lb+2: return None
    rec = candles[-(lb+1):]
    last, prev = rec[-1], rec[:-1]
    if last["close"] > max(c["high"] for c in prev): return "BULL"
    if last["close"] < min(c["low"]  for c in prev): return "BEAR"
    return None

def detect_bos_m15(lb=5):
    """Deteksi BOS di timeframe M15"""
    candles = state["candles_m15"]
    if len(candles) < lb+2: return None
    rec = candles[-(lb+1):]
    last, prev = rec[-1], rec[:-1]
    if last["close"] > max(c["high"] for c in prev): return "BULL"
    if last["close"] < min(c["low"]  for c in prev): return "BEAR"
    return None

def get_m15_status():
    """Ambil status BOS M15 untuk display"""
    bos = state.get("bos_m15")
    t   = state.get("bos_m15_time")
    if not bos: return "⏳ Belum ada BOS M15"
    time_str = t.strftime("%H:%M") if t else ""
    if bos == "BULL":
        return f"📈 BULLISH BOS M15 ({time_str} WITA)"
    else:
        return f"📉 BEARISH BOS M15 ({time_str} WITA)"

# ── 🌙 ASTROLOGI ──────────────────────────────────────────
def get_moon_phase():
    now = datetime.now(timezone.utc)
    known_new_moon = datetime(2026, 3, 18, 0, 23, 0, tzinfo=timezone.utc)
    lunar_cycle = 29.53058867
    phase_days = ((now-known_new_moon).total_seconds()/86400) % lunar_cycle
    if phase_days < 0: phase_days += lunar_cycle
    illumination = round((1-math.cos(2*math.pi*phase_days/lunar_cycle))/2*100)
    if phase_days < 1.85:    phase,phase_en = "🌑 New Moon",        "new_moon"
    elif phase_days < 7.38:  phase,phase_en = "🌒 Waxing Crescent", "waxing_crescent"
    elif phase_days < 9.22:  phase,phase_en = "🌓 First Quarter",   "first_quarter"
    elif phase_days < 14.77: phase,phase_en = "🌔 Waxing Gibbous",  "waxing_gibbous"
    elif phase_days < 16.61: phase,phase_en = "🌕 Full Moon",       "full_moon"
    elif phase_days < 22.15: phase,phase_en = "🌖 Waning Gibbous",  "waning_gibbous"
    elif phase_days < 23.99: phase,phase_en = "🌗 Last Quarter",    "last_quarter"
    else:                    phase,phase_en = "🌘 Waning Crescent", "waning_crescent"
    return {"phase":phase,"phase_en":phase_en,"days":round(phase_days,1),
            "illumination":illumination,
            "next_full":round(14.77-phase_days if phase_days<14.77 else lunar_cycle-phase_days+14.77,1),
            "next_new":round(lunar_cycle-phase_days,1)}

def get_moon_impact(phase_en):
    impacts = {
        "new_moon":        {"bias":"⚠️ NETRAL","signal":"neutral","desc":"Siklus baru. Sering REVERSAL.","trading":"⛔ Hindari posisi besar"},
        "waxing_crescent": {"bias":"📈 BULLISH","signal":"bullish","desc":"Energi naik.","trading":"✅ Fokus BUY"},
        "first_quarter":   {"bias":"📈 BULLISH KUAT","signal":"bullish","desc":"Momentum naik kuat.","trading":"✅ BUY setiap pullback"},
        "waxing_gibbous":  {"bias":"📈 BULLISH","signal":"bullish_caution","desc":"Mendekati puncak.","trading":"✅ Hold BUY"},
        "full_moon":       {"bias":"📉 BEARISH","signal":"bearish","desc":"Puncak. REVERSAL.","trading":"✅ Fokus SELL"},
        "waning_gibbous":  {"bias":"📉 BEARISH","signal":"bearish","desc":"Energi turun.","trading":"✅ SELL di resistance"},
        "last_quarter":    {"bias":"📉 MELEMAH","signal":"bearish","desc":"Momentum melemah.","trading":"⚠️ Market ranging"},
        "waning_crescent": {"bias":"⚠️ NETRAL","signal":"neutral","desc":"Energi lemah.","trading":"⛔ Kurangi trading"},
    }
    return impacts.get(phase_en, impacts["new_moon"])

def get_planet_info():
    now = now_wita()
    month, day = now.month, now.day
    planets = []
    if (month==2 and day>=15) or month==3 or (month==4 and day<=9):
        planets.append("☿ Mercury Retrograde — Fake moves ekstrem")
    if month==3 or (month==2 and day>=1):
        planets.append("♀ Venus di Pisces — Volatilitas tinggi")
    if month==3 and day<=22:
        planets.append("♂ Mars di Pisces — Spike brutal tiba-tiba")
    planets.append("♄ Saturn di Aries — S&R sangat kuat")
    return planets

# ── 🌪️ PERFECT STORM ─────────────────────────────────────
def detect_perfect_storm(candles, price):
    score=0; factors=[]; warnings=[]
    moon = get_moon_phase()
    if moon["phase_en"] in ["new_moon","full_moon"]:
        score+=3; factors.append(f"🌙 {moon['phase']} (+3)")
    elif moon["phase_en"] in ["first_quarter","last_quarter"]:
        score+=2; factors.append(f"🌙 Quarter Moon (+2)")
    now = now_wita()
    if (now.month==2 and now.day>=15) or now.month==3 or (now.month==4 and now.day<=9):
        score+=2; factors.append("☿ Mercury Retrograde (+2)")
    if now.weekday()==2:
        score+=2; factors.append("☀️ Anchor Day Rabu (+2)")
    if len(candles)>=10:
        last10=candles[-10:]
        r=max(c["high"] for c in last10)-min(c["low"] for c in last10)
        if r<15: score+=2; factors.append(f"😴 Sideways brutal {r:.1f}pts (+2)"); warnings.append("⚡ Hurricane siap!")
        eq_h=sum(1 for i in range(len(last10)-1) if abs(last10[i]["high"]-last10[i+1]["high"])<3)
        eq_l=sum(1 for i in range(len(last10)-1) if abs(last10[i]["low"]-last10[i+1]["low"])<3)
        if eq_h>=3 or eq_l>=3: score+=2; factors.append("💧 Liquidity buildup (+2)"); warnings.append("⚡ Sweep akan brutal!")
    base=int(price/100)*100
    for rn in [base,base+100,base+50]:
        if abs(price-rn)<=15: score+=1; factors.append(f"🎯 Round ${rn} (+1)"); break
    if score>=9:   level="🌪️🌪️🌪️ PERFECT STORM EXTREME!"; action="💥 DOMINANT STRATEGY AKTIF!"
    elif score>=6: level="🌪️🌪️ HURRICANE WARNING!";         action="⚡ Pergerakan besar mendekat!"
    elif score>=3: level="⛈️ STORM BUILDING";               action="⚠️ Kondisi memanas."
    else:          level="☀️ NORMAL";                        action="✅ Kondisi normal."
    return {"score":score,"level":level,"factors":factors,"warnings":warnings,"action":action}

# ── Auto S&R ──────────────────────────────────────────────
def get_auto_sr(candles, current_price):
    levels=[]
    if len(candles)<10: return levels
    if len(candles)>=576:
        y=candles[-576:-288]
        if y:
            levels.append({"price":round(max(c["high"] for c in y),2),"label":"PDH","type":"resistance"})
            levels.append({"price":round(min(c["low"] for c in y),2), "label":"PDL","type":"support"})
    if len(candles)>=2016:
        wk=candles[-2016:]
        levels.append({"price":round(max(c["high"] for c in wk),2),"label":"Weekly High","type":"resistance"})
        levels.append({"price":round(min(c["low"] for c in wk),2), "label":"Weekly Low", "type":"support"})
    base=int(current_price/100)*100
    for mult in range(-3,5):
        rn=base+mult*100
        if rn>0 and abs(current_price-rn)<=150:
            levels.append({"price":float(rn),"label":f"Round ${rn}","type":"resistance" if rn>current_price else "support"})
    unique=[]
    for lv in sorted(levels,key=lambda x:x["price"]):
        if not unique or abs(lv["price"]-unique[-1]["price"])>=5:
            unique.append(lv)
    return unique

# ── 🌅 BRIEFING ───────────────────────────────────────────
def send_morning_briefing(price):
    now=now_wita(); moon=get_moon_phase(); impact=get_moon_impact(moon["phase_en"])
    planets=get_planet_info(); storm=detect_perfect_storm(state["candles"],price)
    luck=get_luck_status(now)
    day=get_day_name()
    planet_text="\n".join([f"  • {p}" for p in planets])
    factor_text="\n".join([f"  {f}" for f in storm["factors"]]) if storm["factors"] else "  Tidak ada"
    if day in ["Sabtu","Minggu"]: market_note="🔴 PASAR TUTUP"; setup_plan="Istirahat & persiapkan strategi!"
    elif day=="Senin": market_note="🟡 SENIN — Range Asia belum sempurna"; setup_plan="⚠️ Skip Asia, fokus London & NY"
    elif day=="Rabu":  market_note="🟡 RABU — Anchor Day!"; setup_plan="⚠️ Kurangi posisi saat news"
    elif day=="Jumat": market_note="🟡 JUMAT — Profit taking!"; setup_plan="⚠️ Close sebelum 23:00 WITA"
    else: market_note="🟢 PASAR BUKA — Normal"; setup_plan="✅ Asia: Low Asia → BUY BOS\n✅ London: SELL High Asia\n✅ 61.8%: BUY ke-2"
    bias="📈 BULLISH" if impact["signal"]=="bullish" else "📉 BEARISH" if impact["signal"]=="bearish" else "⚠️ NETRAL"
    targets=f"🎯 Naik: ${price+50:.0f}→${price+100:.0f}" if impact["signal"]=="bullish" else f"🎯 Turun: ${price-50:.0f}→${price-100:.0f}" if impact["signal"]=="bearish" else f"🎯 Range: ${price-50:.0f}–${price+50:.0f}"
    base=int(price/100)*100
    send_telegram(
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌅 *GOLD MORNING BRIEFING*\n"
        f"📅 {day}, {now.day} {get_month_name()} {now.year}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"☀️ *Selamat pagi, Trader!* ☕\n\n"
        f"💰 *HARGA:* *${price:.2f}*\n"
        f"Round: ${base} | Half: ${base+50} | Res: ${base+100}\n\n"
        f"📊 {market_note}\n\n"
        f"🌪️ *Storm:* {storm['level']} ({storm['score']}/12)\n"
        f"{factor_text}\n\n"
        f"🎯 *Bias:* {bias} | {targets}\n\n"
        f"📋 *Setup:*\n{setup_plan}\n\n"
        f"⏰ *Killzone WITA:*\n"
        f"🌏 Asia:    01:00–04:00\n"
        f"🇬🇧 London:  15:00–18:00\n"
        f"⚠️ Judas:   15:00–15:30 ← BAHAYA!\n"
        f"🔥 Overlap: 20:00–21:30 ← TERKUAT!\n"
        f"🇺🇸 NYSE:    21:30–22:00\n"
        f"🔚 Close:   00:00–02:00\n\n"
        f"🌙 {moon['phase']} ({moon['illumination']}%) | {impact['bias']}\n"
        f"📝 {impact['desc']}\n"
        f"💡 {impact['trading']}\n\n"
        f"🪐\n{planet_text}\n\n"
        f"⚠️ *Rules:* BOS dulu | SL wajib | R:R 1:2\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Semangat! 💪🥇\n⚠️ _Bukan saran investasi_"
    )
    print("[BRIEFING] Daily sent")

def send_weekly_briefing(price):
    now=now_wita(); moon=get_moon_phase(); impact=get_moon_impact(moon["phase_en"])
    planets=get_planet_info(); storm=detect_perfect_storm(state["candles"],price)
    luck=get_luck_status(now)
    planet_text="\n".join([f"  • {p}" for p in planets])
    monday=now-timedelta(days=now.weekday())
    day_notes={0:"Senin  → Range Asia belum sempurna",1:"Selasa → Hari terbaik 🌟",
               2:"Rabu   → ⚠️ Anchor Day",3:"Kamis  → Bagus 🌟",4:"Jumat  → Profit taking"}
    calendar="\n".join([f"  {(monday+timedelta(days=i)).strftime('%d %b')} {day_notes.get(i,'')}" for i in range(5)])
    weekly_bias="📈 BULLISH" if impact["signal"] in ["bullish","bullish_caution"] else "📉 BEARISH" if impact["signal"]=="bearish" else "⚠️ NETRAL"
    base=int(price/100)*100
    # Lucky days minggu ini
    monday_date = now - timedelta(days=now.weekday())
    week_luck = []
    day_names = ["Sen","Sel","Rab","Kam","Jum"]
    for i in range(5):
        d = monday_date + timedelta(days=i)
        lk = get_luck_status(d)
        week_luck.append(f"{day_names[i]} {d.day}: {lk['emoji']}")
    week_luck_text = " | ".join(week_luck)
    send_telegram(
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 *GOLD WEEKLY BRIEFING*\n"
        f"Minggu {monday.strftime('%d')}–{(monday+timedelta(days=4)).strftime('%d')} {get_month_name(monday.month)}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 *${price:.2f}* | Bias: {weekly_bias}\n\n"
        f"🍀 *Luck Week:*\n{week_luck_text}\n"
        f"🍀=Lucky | 📅=Biasa | ⚠️=Unlucky\n\n"
        f"🗓️ *Kalender:*\n{calendar}\n\n"
        f"🌪️ *Storm:* {storm['level']} ({storm['score']}/12)\n\n"
        f"🌙 {moon['phase']} ({moon['illumination']}%)\n"
        f"Full Moon: {moon['next_full']:.0f}hr | New Moon: {moon['next_new']:.0f}hr\n\n"
        f"🪐 Planet:\n{planet_text}\n\n"
        f"🎯 *Level:*\n"
        f"🔴 Res: ${base+100}→${base+150}→${base+200}\n"
        f"📍 Now: ${price:.2f}\n"
        f"🟢 Sup: ${base}→${base-50}→${base-100}\n\n"
        f"⏰ *Killzone WITA:*\n"
        f"🌏 Asia 01:00–04:00 | ⚠️ Judas 15:00–15:30\n"
        f"✅ Entry 15:30–18:00 | 🔥 Overlap 20:00–21:30\n"
        f"🇺🇸 NYSE 21:30–22:00 | 🔚 Close 00:00–02:00\n\n"
        f"🧠 *Dominant Strategy:*\n"
        f"1. Asia sideway → London Hurricane (15:00)\n"
        f"2. Sweep Low Asia → Entry 61.8% BUY\n"
        f"3. NY Overlap 20:00 = Arah Dominan\n\n"
        f"⚠️ Max 2/hari | SL wajib | Close Jumat\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Semangat minggu ini! 💪🥇"
    )
    print("[BRIEFING] Weekly sent")

# ── State ─────────────────────────────────────────────────
state = {
    "candles":[],"cur_candle":None,"prev_price":None,
    # M15 candles
    "candles_m15":[],"cur_candle_m15":None,
    "bos_m15":None,"bos_m15_time":None,
    "asia_lo":None,"asia_hi":None,"fib":None,"fib_locked":False,
    "buy_done":False,"sell_done":False,"buy2_done":False,
    "alerted":set(),"sr_alerted":set(),"pattern_alerted":set(),
    "last_day":None,"last_update":0,"briefing_sent":False,
    "weekly_sent":False,"storm_alerted":False,"low_asia_swept":False,
    "kz_alerted":set(),
}

def reset_daily():
    today=now_wita().strftime("%Y-%m-%d")
    if state["last_day"]==today: return
    print(f"[RESET] {today}")
    state.update({
        "asia_lo":None,"asia_hi":None,"fib":None,"fib_locked":False,
        "buy_done":False,"sell_done":False,"buy2_done":False,
        "alerted":set(),"sr_alerted":set(),"pattern_alerted":set(),
        "cur_candle":None,"cur_candle_m15":None,
        "bos_m15":None,"bos_m15_time":None,
        "last_day":today,"briefing_sent":False,
        "storm_alerted":False,"low_asia_swept":False,"kz_alerted":set(),
    })

# ── 🕐 KILLZONE ALERTS ────────────────────────────────────
def check_killzone_alerts():
    """Kirim alert saat masuk killzone baru"""
    if not market_open(): return
    now = now_wita()
    h, m = now.hour, now.minute

    for kz in KILLZONES:
        # Cek apakah sekarang tepat masuk killzone (dalam 1 menit pertama)
        if h == kz["start_h"] and m == kz["start_m"]:
            kz_key = f"kz-{kz['name']}-{now.strftime('%Y-%m-%d')}"
            if kz_key in state["kz_alerted"]: continue
            state["kz_alerted"].add(kz_key)

            p = state["prev_price"] or 0
            moon = get_moon_phase()
            impact = get_moon_impact(moon["phase_en"])

            # Hitung durasi killzone
            start_min = kz["start_h"]*60 + kz["start_m"]
            end_min   = kz["end_h"]*60   + kz["end_m"]
            duration  = end_min - start_min

            # Header berbeda untuk killzone bahaya
            if kz["danger"]:
                header = f"🚨 *{kz['emoji']} {kz['name']}*"
            else:
                header = f"⏰ *{kz['emoji']} {kz['name']}*"

            # Info Asia Range kalau ada
            asia_info = ""
            if state["asia_lo"] and state["asia_hi"]:
                asia_info = (
                    f"\n━━━━━━━━━━━━━━\n"
                    f"📍 Range Asia:\n"
                    f"Low: *${state['asia_lo']:.2f}*\n"
                    f"High: *${state['asia_hi']:.2f}*\n"
                    f"Range: {state['asia_hi']-state['asia_lo']:.1f} poin"
                )
                if state["fib"]:
                    asia_info += f"\n🔴 61.8%: *${state['fib']['f618']:.2f}*"

            send_telegram(
                f"━━━━━━━━━━━━━━\n"
                f"{header}\n"
                f"🕐 {h:02d}:{m:02d} WITA | Durasi: {duration} menit\n"
                f"━━━━━━━━━━━━━━\n"
                f"💰 Harga: *${p:.2f}*\n\n"
                f"📝 *{kz['desc']}*\n\n"
                f"💡 *Action:*\n{kz['action']}"
                f"{asia_info}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🌙 {moon['phase']} | {impact['bias']}\n"
                f"⚠️ _Bukan saran investasi_"
            )
            print(f"[KILLZONE] {kz['name']} @ {h:02d}:{m:02d} WITA")

def check_briefings():
    now=now_wita(); p=state["prev_price"]
    if not p: return
    if now.hour==8 and now.minute<1 and not state["briefing_sent"]:
        state["briefing_sent"]=True; send_morning_briefing(p)
    if now.weekday()==0 and now.hour==8 and 30<=now.minute<31 and not state["weekly_sent"]:
        state["weekly_sent"]=True; send_weekly_briefing(p)

def signal(sig_type, price, detail):
    key=f"{sig_type}-{now_wita().strftime('%Y-%m-%d-%H')}"
    if key in state["alerted"]: return
    state["alerted"].add(key)
    labels={"BUY1":"📈 BUY — Sesi Asia","SELL":"📉 SELL — London","BUY2":"🔄 BUY ke-2 — 61.8%"}
    moon=get_moon_phase(); impact=get_moon_impact(moon["phase_en"])
    send_telegram(
        f"🥇 *XAUUSD SIGNAL M5*\n━━━━━━━━━━━━━━\n"
        f"{labels[sig_type]}\n💰 *${price:.2f}*\n{detail}\n"
        f"━━━━━━━━━━━━━━\n🌙 {moon['phase']} | {impact['bias']}\n"
        f"🕐 {now_wita().strftime('%H:%M:%S')} WITA\n⚠️ _Bukan saran investasi_"
    )

def check_sr_and_patterns(candle, all_candles):
    if not market_open(): return
    price=candle["close"]; b=detect_bos(all_candles)

    # Perfect Storm
    if not state["storm_alerted"]:
        storm=detect_perfect_storm(all_candles,price)
        if storm["score"]>=6:
            state["storm_alerted"]=True
            factor_text="\n".join([f"  {f}" for f in storm["factors"]])
            send_telegram(
                f"🌪️ *PERFECT STORM DETECTED!*\n━━━━━━━━━━━━━━\n"
                f"Level: {storm['level']} ({storm['score']}/12)\n\n"
                f"Faktor:\n{factor_text}\n\n💥 *{storm['action']}*\n"
                f"━━━━━━━━━━━━━━\n"
                f"🎯 Watch:\n1. Asia sideway → London Hurricane 15:00\n"
                f"2. Sweep → 61.8% Golden Ratio\n3. NY 20:00 = Dominant\n"
                f"🕐 {now_wita().strftime('%H:%M:%S')} WITA"
            )

    # London Sweep Low Asia
    if state["asia_lo"] and get_session()=="london" and not state["low_asia_swept"]:
        if candle["low"]<state["asia_lo"]:
            state["low_asia_swept"]=True
            f=calc_fib(state["asia_lo"],state["asia_hi"]) if state["asia_hi"] else None
            fib_text=f"\n🔴 Golden Ratio 61.8%: *${f['f618']:.2f}*" if f else ""
            send_telegram(
                f"🌊 *LONDON SWEEP LOW ASIA!*\n━━━━━━━━━━━━━━\n"
                f"📍 Low Asia: *${state['asia_lo']:.2f}*\n"
                f"📍 Candle Low: *${candle['low']:.2f}*{fib_text}\n\n"
                f"🎯 Monitor 61.8% untuk BUY reversal!\n"
                f"🕐 {now_wita().strftime('%H:%M:%S')} WITA"
            )

    # Candle Patterns — DINONAKTIFKAN (terlalu banyak noise)
    # Gunakan /patterns untuk cek manual

    # S&R
    for sr in get_auto_sr(all_candles,price):
        level,label,sr_type=sr["price"],sr["label"],sr["type"]
        if abs(price-level)>SR_TOLERANCE: continue
        touch_key=f"touch-{label}-{now_wita().strftime('%Y-%m-%d-%H')}"
        if touch_key not in state["sr_alerted"]:
            state["sr_alerted"].add(touch_key)
            emoji="🔴" if sr_type=="resistance" else "🟢"
            send_telegram(
                f"📍 *Menyentuh {sr_type.upper()}*\n━━━━━━━━━━━━━━\n"
                f"{emoji} {label}: *${level:.2f}*\n💰 *${price:.2f}*\n"
                f"📏 Jarak: {abs(price-level):.1f} poin\n"
                f"🕐 {now_wita().strftime('%H:%M:%S')} WITA\n⏳ Tunggu konfirmasi..."
            )
        # BOS M5 di S&R — DINONAKTIFKAN
        # Gunakan /bos untuk cek manual
        # M15 BOS tetap aktif (lebih akurat)

def process_bos_m15(bos, old_bos, price):
    """Proses saat BOS M15 terbentuk - kirim notif"""
    if not market_open(): return
    moon   = get_moon_phase()
    impact = get_moon_impact(moon["phase_en"])
    luck   = get_luck_status()
    sess_map = {"asia":"🌏 Asia","pre":"⏳ Pre-London",
                "london":"🇬🇧 London","ny":"🇺🇸 New York"}

    # Cek apakah M5 BOS searah
    bos_m5 = detect_bos(state["candles"])
    confirmation = ""
    power = ""

    if bos_m5 == bos:
        confirmation = "✅ *M5 BOS KONFIRMASI!* → ENTRY VALID!"
        power = "🔥🔥🔥 SANGAT KUAT"
    else:
        confirmation = "⏳ Tunggu M5 BOS konfirmasi dulu"
        power = "⭐⭐ SEDANG"

    # Cek fib confluence
    fib_text = ""
    if state["fib"]:
        f = state["fib"]
        if abs(price - f["f618"]) <= 15:
            fib_text = f"\n🎯 *Dekat 61.8% Golden Ratio!* ${f['f618']:.2f}"
            power = "🔥🔥🔥🔥 SUPER KUAT!" if bos_m5 == bos else "🔥🔥🔥 KUAT"

    key = f"bos_m15_{bos}_{now_wita().strftime('%Y-%m-%d-%H-%M')}"
    if key in state["alerted"]: return
    state["alerted"].add(key)

    emoji = "📈" if bos == "BULL" else "📉"
    direction = "BULLISH" if bos == "BULL" else "BEARISH"
    action = "BUY 📈" if bos == "BULL" else "SELL 📉"

    send_telegram(
        f"⚡ *BOS M15 TERBENTUK!*\n"
        f"━━━━━━━━━━━━━━\n"
        f"{emoji} *{direction} BOS M15*\n"
        f"💰 Harga: *${price:.2f}*\n"
        f"📊 Kekuatan: {power}\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"*🎯 Konfirmasi M5:*\n"
        f"{confirmation}{fib_text}\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"*💡 Yang harus dilakukan:*\n"
        f"{'✅ Entry ' + action + ' sekarang!' if bos_m5 == bos else '👀 Buka chart M5'}\n"
        f"{'✅ M15 + M5 + Fib = TRIPLE KONFIRMASI!' if bos_m5 == bos and fib_text else ''}\n"
        f"🛡 Set SL sebelum entry!\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"🌏 Sesi: {sess_map.get(get_session())}\n"
        f"🌙 {moon['phase']} | {impact['bias']}\n"
        f"{luck['emoji']} {luck['label']}\n"
        f"🕐 {now_wita().strftime('%H:%M:%S')} WITA\n"
        f"━━━━━━━━━━━━━━\n"
        f"⚠️ _Konfirmasi di chart sebelum entry!_"
    )
    print(f"[BOS M15] {direction} @ ${price:.2f} | M5:{bos_m5} | Power:{power}")

def process_candle(candle):
    if not market_open(): return
    sess=get_session(); all_c=state["candles"]; b=detect_bos(all_c)
    check_sr_and_patterns(candle,all_c)
    if sess=="asia":
        state["asia_lo"]=candle["low"] if state["asia_lo"] is None else min(state["asia_lo"],candle["low"])
        state["asia_hi"]=candle["high"] if state["asia_hi"] is None else max(state["asia_hi"],candle["high"])
        if b=="BULL" and not state["buy_done"]:
            state["buy_done"]=True
            signal("BUY1",candle["close"],
                f"📍 Low Asia: *${state['asia_lo']:.2f}*\n"
                f"🎯 Target: High Asia *${state['asia_hi']:.2f}*\n"
                f"🛡 SL: Di bawah Low Asia\n📊 TF: M5")
    if sess in ("pre","london"):
        if state["asia_lo"] and state["asia_hi"] and not state["fib_locked"]:
            f=calc_fib(state["asia_lo"],state["asia_hi"])
            state["fib"]=f; state["fib_locked"]=True
            send_telegram(
                f"📐 *Fibonacci Terbentuk*\n━━━━━━━━━━━━━━\n"
                f"🟦 Low:  *${f['f100']:.2f}*\n"
                f"🟡 38.2%: *${f['f382']:.2f}*\n"
                f"🔴 61.8%: *${f['f618']:.2f}* ← Golden Ratio\n"
                f"🟤 78.6%: *${f['f786']:.2f}*\n"
                f"🟢 High:  *${f['f0']:.2f}*\n"
                f"🚀 Ext 127%: *${f['f127']:.2f}*\n"
                f"🕐 {now_wita().strftime('%H:%M')} WITA"
            )
    if sess=="london" and state["asia_hi"] and state["fib"]:
        hi,f=state["asia_hi"],state["fib"]
        if abs(candle["close"]-hi)<=8 and b=="BEAR" and not state["sell_done"]:
            state["sell_done"]=True
            signal("SELL",candle["close"],
                f"📍 High Asia: *${hi:.2f}*\n"
                f"🎯 TP1: 61.8% *${f['f618']:.2f}*\n"
                f"🎯 TP2: 78.6% *${f['f786']:.2f}*\n"
                f"🛡 SL: Atas High Asia\n📊 TF: M5")
        if abs(candle["close"]-f["f618"])<=8 and b=="BULL" and not state["buy2_done"]:
            state["buy2_done"]=True
            signal("BUY2",candle["close"],
                f"📍 Golden Ratio 61.8%: *${f['f618']:.2f}*\n"
                f"🎯 TP1: High Asia *${hi:.2f}*\n"
                f"🎯 TP2: Extension *${f['f127']:.2f}*\n"
                f"🛡 SL: Bawah 61.8%\n📊 TF: M5")

# ── Commands ──────────────────────────────────────────────
def handle_commands():
    updates=get_updates(offset=state["last_update"])
    for upd in updates:
        state["last_update"]=upd["update_id"]+1
        text=upd.get("message",{}).get("text","").strip()
        if not text: continue
        print(f"[CMD] {text}")

        if text in ("/start","/help"):
            send_telegram(
                f"🥇 *XAUUSD Bot v9 — Sinarmas Edition*\n━━━━━━━━━━━━━━\n"
                f"/briefing  → Daily briefing sekarang\n"
                f"/weekly    → Weekly briefing\n"
                f"/luck      → Cek luck hari ini (Sinarmas)\n"
                f"/luckmonth → Luck calendar bulan ini\n"
                f"/killzone  → Jadwal killzone hari ini\n"
                f"/storm     → Perfect Storm meter\n"
                f"/status    → Status + astro + luck\n"
                f"/moon      → Fase bulan\n"
                f"/astro     → Planet hari ini\n"
                f"/listsr    → Level S&R\n"
                f"/bos       → Status BOS M15 & M5 sekarang\n"
                f"/patterns  → Info candle patterns\n"
                f"/help      → Menu ini\n"
                f"━━━━━━━━━━━━━━\n"
                f"🌅 Daily: *08:00 WITA*\n"
                f"📅 Weekly: *Senin 08:30 WITA*\n"
                f"⏰ Killzone auto-alert WITA\n"
                f"🌪️ Perfect Storm auto\n"
                f"🕯 Candle Pattern 3 Tier\n"
                f"━━━━━━━━━━━━━━\n"
                f"Bot aktif 24 jam • gold-api.com"
            )

        elif text=="/luck":
            luck=get_luck_status()
            now_d=now_wita()
            send_telegram(
                f"🍀 *LUCK STATUS HARI INI*\n"
                f"━━━━━━━━━━━━━━\n"
                f"📅 {now_d.day} {get_month_name()} {now_d.year}\n\n"
                f"Status: {luck['label']}\n"
                f"Warna: {luck['color']}\n\n"
                f"📝 {luck['desc']}\n\n"
                f"💡 *Saran Trading:*\n{luck['trading']}\n"
                f"━━━━━━━━━━━━━━\n"
                f"Sumber: Kalender Bank Sinarmas 2026\n"
                f"🔴 Lucky = Hari baik\n"
                f"📅 Ordinary = Hari biasa\n"
                f"⚠️ Unlucky = Hindari keputusan besar"
            )

        elif text=="/luckmonth":
            now_d=now_wita()
            month_data=SINARMAS_CALENDAR.get(now_d.month,{})
            import calendar
            lucky_days=[str(d) for d,s in month_data.items() if s=="L"]
            unlucky_days=[str(d) for d,s in month_data.items() if s=="U"]
            send_telegram(
                f"🍀 *LUCK CALENDAR — {get_month_name()} {now_d.year}*\n"
                f"━━━━━━━━━━━━━━\n"
                f"🔴 *Lucky Days ({len(lucky_days)} hari):*\n"
                f"{', '.join(lucky_days)}\n\n"
                f"⚠️ *Unlucky Days ({len(unlucky_days)} hari):*\n"
                f"{', '.join(unlucky_days)}\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"💡 *Trading Strategy:*\n"
                f"🔴 Lucky → Full size, confident entry\n"
                f"📅 Ordinary → Normal trading\n"
                f"⚠️ Unlucky → Kurangi size, ekstra hati-hati\n"
                f"━━━━━━━━━━━━━━\n"
                f"Sumber: Bank Sinarmas 2026"
            )

        elif text=="/briefing":
            p=state["prev_price"]
            if p: send_morning_briefing(p)
            else: send_telegram("⏳ Harga belum tersedia.")

        elif text=="/weekly":
            p=state["prev_price"]
            if p: send_weekly_briefing(p)
            else: send_telegram("⏳ Harga belum tersedia.")

        elif text=="/killzone":
            now=now_wita()
            kz_list=[]
            for kz in KILLZONES:
                h,m=now.hour,now.minute
                t=h*60+m
                start=kz["start_h"]*60+kz["start_m"]
                end=kz["end_h"]*60+kz["end_m"]
                is_active="🔴 AKTIF SEKARANG!" if start<=t<end else ""
                kz_list.append(
                    f"{kz['emoji']} *{kz['name']}*\n"
                    f"   {kz['start_h']:02d}:{kz['start_m']:02d}–{kz['end_h']:02d}:{kz['end_m']:02d} WITA {is_active}"
                )
            kz_text="\n\n".join(kz_list)
            kz_now=get_current_killzone()
            current_text=f"\n\n📍 *Sekarang:* {kz_now['emoji']} {kz_now['name']}" if kz_now else "\n\n📍 *Sekarang:* Di luar killzone"
            send_telegram(
                f"⏰ *KILLZONE SCHEDULE WITA*\n━━━━━━━━━━━━━━\n\n"
                f"{kz_text}{current_text}\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"⚠️ Judas Swing: 15:00–15:30 WITA\n"
                f"🔥 Paling volatile: 20:00–21:30 WITA\n"
                f"❌ Dead zone: 04:00–10:00 WITA\n"
                f"🕐 {now.strftime('%H:%M:%S')} WITA"
            )

        elif text=="/storm":
            p=state["prev_price"] or 0
            storm=detect_perfect_storm(state["candles"],p)
            factor_text="\n".join([f"  {f}" for f in storm["factors"]]) if storm["factors"] else "  Tidak ada"
            send_telegram(
                f"🌪️ *PERFECT STORM METER*\n━━━━━━━━━━━━━━\n"
                f"Level: {storm['level']}\nScore: {storm['score']}/12\n\n"
                f"Faktor:\n{factor_text}\n\n💥 {storm['action']}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🎯 Dominant Strategy:\n"
                f"1. Asia sideway → London 15:00 Hurricane\n"
                f"2. Sweep Low Asia → 61.8% BUY\n"
                f"3. NY 20:00 = Arah Dominan\n"
                f"🕐 {now_wita().strftime('%H:%M:%S')} WITA"
            )

        elif text=="/status":
            p=state["prev_price"] or 0
            moon=get_moon_phase(); impact=get_moon_impact(moon["phase_en"])
            planets=get_planet_info(); storm=detect_perfect_storm(state["candles"],p)
            planet_text="\n".join([f"  • {pl}" for pl in planets])
            sess_map={"asia":"🌏 Asia","pre":"⏳ Pre-London","london":"🇬🇧 London","ny":"🇺🇸 New York"}
            kz=get_current_killzone()
            kz_text=f"\n⏰ Killzone: {kz['emoji']} {kz['name']}" if kz else ""
            luck=get_luck_status()
            m15_status = get_m15_status()
            bos_m5_now = detect_bos(state["candles"])
            m5_status  = f"📈 BULLISH" if bos_m5_now=="BULL" else f"📉 BEARISH" if bos_m5_now=="BEAR" else "⏳ Belum ada"
            # Triple konfirmasi check
            triple = ""
            if state["bos_m15"] and bos_m5_now == state["bos_m15"]:
                triple = f"\n🔥 *M15+M5 SEARAH = ENTRY VALID!*"
            send_telegram(
                f"📊 *STATUS XAUUSD BOT*\n━━━━━━━━━━━━━━\n"
                f"{luck['label']} | {luck['color']}\n"
                f"📝 {luck['desc']}\n\n"
                f"💰 *${p:.2f}* | {sess_map.get(get_session())}{kz_text}\n"
                f"📍 Low Asia: {'$'+str(state['asia_lo']) if state['asia_lo'] else 'Belum'}\n"
                f"📍 High Asia: {'$'+str(state['asia_hi']) if state['asia_hi'] else 'Belum'}\n"
                f"📐 Fib: {'✅' if state['fib'] else '⏳'}\n"
                f"📈 BUY: {'✅' if state['buy_done'] else '⏳'} | "
                f"📉 SELL: {'✅' if state['sell_done'] else '⏳'} | "
                f"🔄 BUY2: {'✅' if state['buy2_done'] else '⏳'}\n"
                f"🌊 Swept: {'✅' if state['low_asia_swept'] else '❌'}\n"
                f"━━━━━━━━━━━━━━\n"
                f"📊 *BOS Status:*\n"
                f"M15: {m15_status}\n"
                f"M5:  {m5_status}{triple}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🌪️ {storm['level']} ({storm['score']}/12)\n"
                f"━━━━━━━━━━━━━━\n"
                f"🌙 {moon['phase']} ({moon['illumination']}%)\n"
                f"Bias: {impact['bias']}\n{impact['desc']}\n"
                f"💡 {impact['trading']}\n\n"
                f"🪐\n{planet_text}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🕐 {now_wita().strftime('%d %b %Y %H:%M:%S')} WITA"
            )

        elif text=="/moon":
            moon=get_moon_phase(); impact=get_moon_impact(moon["phase_en"])
            send_telegram(
                f"🌙 *FASE BULAN & GOLD*\n━━━━━━━━━━━━━━\n"
                f"{moon['phase']} ({moon['illumination']}%)\n"
                f"Hari ke-{moon['days']} | Full: {moon['next_full']:.0f}hr | New: {moon['next_new']:.0f}hr\n\n"
                f"Bias: {impact['bias']}\n{impact['desc']}\n💡 {impact['trading']}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🌑 New → Reversal | 🌒🌓 Waxing → Naik\n"
                f"🌕 Full → Reversal | 🌖🌗 Waning → Turun"
            )

        elif text=="/astro":
            moon=get_moon_phase(); impact=get_moon_impact(moon["phase_en"])
            planets=get_planet_info(); planet_text="\n".join([f"• {p}" for p in planets])
            send_telegram(
                f"🔭 *ASTROLOGI — {now_wita().strftime('%d %b %Y')}*\n━━━━━━━━━━━━━━\n"
                f"🌙 {moon['phase']} ({moon['illumination']}%)\n\n"
                f"🪐 Planet:\n{planet_text}\n\n"
                f"Bias: {impact['bias']}\n{impact['desc']}\n💡 {impact['trading']}"
            )

        elif text=="/listsr":
            p=state["prev_price"] or 0
            levels=get_auto_sr(state["candles"],p)
            if not levels: send_telegram("⏳ Data S&R belum cukup.")
            else:
                res=sorted([l for l in levels if l["type"]=="resistance" and l["price"]>p],key=lambda x:x["price"])[:5]
                sup=sorted([l for l in levels if l["type"]=="support" and l["price"]<p],key=lambda x:x["price"],reverse=True)[:5]
                msg=[f"📋 *S&R* (${p:.2f})\n"]
                if res:
                    msg.append("🔴 *Resistance:*")
                    for l in res: msg.append(f"  • {l['label']}: *${l['price']:.2f}* (+{l['price']-p:.1f})")
                if sup:
                    msg.append("\n🟢 *Support:*")
                    for l in sup: msg.append(f"  • {l['label']}: *${l['price']:.2f}* (-{p-l['price']:.1f})")
                send_telegram("\n".join(msg))

        elif text=="/bos":
            p = state["prev_price"] or 0
            bos_m5  = detect_bos(state["candles"])
            bos_m15 = state.get("bos_m15")
            m15_t   = state.get("bos_m15_time")
            m5_str  = f"📈 BULLISH" if bos_m5=="BULL" else f"📉 BEARISH" if bos_m5=="BEAR" else "⏳ Belum ada"
            m15_str = f"📈 BULLISH" if bos_m15=="BULL" else f"📉 BEARISH" if bos_m15=="BEAR" else "⏳ Belum ada"
            m15_time = m15_t.strftime("%H:%M WITA") if m15_t else "-"
            # Power level
            if bos_m5 and bos_m15 and bos_m5 == bos_m15:
                power = "🔥🔥🔥🔥 SUPER KUAT — M15+M5 SEARAH!"
                action = "✅ ENTRY VALID! BUY" if bos_m15=="BULL" else "✅ ENTRY VALID! SELL"
            elif bos_m15:
                power = "⭐⭐⭐ KUAT — Tunggu M5 konfirmasi"
                action = f"⏳ Tunggu M5 BOS {'BULL' if bos_m15=='BULL' else 'BEAR'}"
            elif bos_m5:
                power = "⭐⭐ SEDANG — M5 saja, belum M15"
                action = "⚠️ Hati-hati, belum dikonfirmasi M15"
            else:
                power = "⏳ Belum ada BOS"
                action = "Tunggu BOS terbentuk"
            fib_note = ""
            if state["fib"] and p:
                f = state["fib"]
                if abs(p - f["f618"]) <= 20:
                    fib_note = f"\n🎯 *Dekat Golden Ratio 61.8%!* ${f['f618']:.2f}"
            send_telegram(
                f"📊 *BOS STATUS — XAUUSD*\n"
                f"━━━━━━━━━━━━━━\n"
                f"💰 Harga: *${p:.2f}*\n\n"
                f"⏱ *M15 BOS:* {m15_str}\n"
                f"   Terbentuk: {m15_time}\n\n"
                f"⚡ *M5 BOS:* {m5_str}\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"💪 *Kekuatan:*\n{power}{fib_note}\n\n"
                f"💡 *Action:*\n{action}\n"
                f"━━━━━━━━━━━━━━\n"
                f"📋 *Panduan:*\n"
                f"🔥🔥🔥🔥 M15+M5 = Entry langsung\n"
                f"⭐⭐⭐ M15 saja = Standby, tunggu M5\n"
                f"⭐⭐ M5 saja = Skip atau hati-hati\n"
                f"━━━━━━━━━━━━━━\n"
                f"🕐 {now_wita().strftime('%H:%M:%S')} WITA"
            )

        elif text=="/patterns":
            send_telegram(
                f"🕯 *CANDLE PATTERNS*\n━━━━━━━━━━━━━━\n\n"
                f"🔴 *TIER 1 — STRONG* (selalu kirim)\n"
                f"• Bullish/Bearish Engulfing\n"
                f"• Bullish/Bearish Pin Bar\n"
                f"• Morning/Evening Star\n\n"
                f"🟡 *TIER 2 — WATCH* (di level kunci)\n"
                f"• Hammer / Shooting Star\n"
                f"• Tweezer Top/Bottom\n"
                f"• Bullish/Bearish Harami\n\n"
                f"🟢 *TIER 3 — INFO* (hanya di level kunci)\n"
                f"• Doji / Inside Bar / Marubozu\n\n"
                f"Level kunci = S&R + Fibonacci\n"
                f"⚠️ Konfirmasi dengan BOS!"
            )

# ── Main ──────────────────────────────────────────────────
def main():
    print("="*50)
    print("  XAUUSD Bot v8 — WITA + Killzone Edition")
    print("  Killzone Alert + Pattern 3Tier + Storm")
    print("="*50)
    moon=get_moon_phase(); impact=get_moon_impact(moon["phase_en"])
    send_telegram(
        f"🚀 *XAUUSD Bot v11 — Clean Signal Edition!*\n━━━━━━━━━━━━━━\n"
        f"📡 gold-api.com | 📊 M5 | 🕐 WITA\n\n"
        f"*Fitur:*\n"
        f"⏰ Killzone Alert otomatis (WITA)\n"
        f"📊 BOS M15 (utama) + M5 filter\n"
        f"🔕 Candle pattern & M5 BOS = silent mode\n"
        f"🕯 Candle Pattern 3 Tier\n"
        f"🌪️ Perfect Storm detection\n"
        f"🌊 London Sweep Low Asia\n"
        f"📐 Fibonacci + Extension\n"
        f"🌅 Daily briefing: *08:00 WITA*\n"
        f"📅 Weekly: *Senin 08:30 WITA*\n\n"
        f"⏰ *Killzone WITA:*\n"
        f"🌏 Asia: 01:00–04:00\n"
        f"⚠️ Judas: 15:00–15:30 ← BAHAYA!\n"
        f"✅ Entry: 15:30–18:00\n"
        f"🔥 Overlap: 20:00–21:30 ← TERKUAT!\n"
        f"🔚 Close: 00:00–02:00\n\n"
        f"🌙 {moon['phase']} | {impact['bias']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"/killzone untuk jadwal lengkap!\n"
        f"/luck untuk cek luck hari ini!\n"
        f"🕐 {now_wita().strftime('%d %b %Y %H:%M')} WITA"
    )

    while True:
        try:
            reset_daily()
            check_briefings()
            check_killzone_alerts()
            handle_commands()
            price=fetch_price()
            if price:
                prev=state["prev_price"]
                chg=round(price-prev,2) if prev else 0
                arrow="▲" if chg>=0 else "▼"
                print(f"[{now_wita().strftime('%H:%M:%S')} WITA] ${price:.2f} {arrow}{abs(chg):.2f} | {get_session()} | Lo:{state['asia_lo']} Hi:{state['asia_hi']}")
                mk=int(time.time()//300)
                if state["cur_candle"] is None or state["cur_candle"]["mk"]!=mk:
                    if state["cur_candle"] is not None:
                        closed={k:state["cur_candle"][k] for k in ["open","high","low","close"]}
                        state["candles"]=state["candles"][-8640:]+[closed]
                        process_candle(closed)
                    state["cur_candle"]={"mk":mk,"open":price,"high":price,"low":price,"close":price}
                else:
                    c=state["cur_candle"]
                    c["high"]=max(c["high"],price); c["low"]=min(c["low"],price); c["close"]=price
                state["prev_price"]=price
        except KeyboardInterrupt:
            print("\n[STOP]"); send_telegram("⏹ *Bot dihentikan.*"); break
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(FETCH_INTERVAL)

if __name__=="__main__":
    main()
