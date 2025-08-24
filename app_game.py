import ccxt
import pandas as pd
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

# ASCII Art สำหรับธีมเกม
GAME_HEADER = f"""
{Fore.RED}🕹️ Crypto Battle Arena - Quick Report 🕹️{Style.RESET_ALL}
{Fore.YELLOW}⚔️ สแกน 20 นักสู้ที่แข็งแกร่งที่สุดในสนามรบ! ⚔️{Style.RESET_ALL}
"""

# ---------------------------
# ฟังก์ชันสร้าง Price Bar (เหมือนหลอดเลือด)
# ---------------------------
def price_bar(current_price, swing_high, swing_low):
    total_range = swing_high - swing_low
    if total_range == 0:
        return f"{Fore.RED}[{'█' * 10}] 100% 💪{Style.RESET_ALL}", 100.0
    normalized_price = (current_price - swing_low) / total_range
    filled = int(normalized_price * 10)
    filled = max(0, min(filled, 10))  # ป้องกันเกินขอบเขต
    bar = f"{Fore.GREEN}{'█' * filled}{'░' * (10 - filled)}{Style.RESET_ALL}"
    percentage = normalized_price * 100
    status = "💪" if percentage > 70 else "⚠️" if percentage > 30 else "🩸"
    return f"{bar} {percentage:.1f}% {status}", percentage

# ---------------------------
# ฟังก์ชันคำนวณ Price ATK (% Change)
# ---------------------------
def price_atk(df):
    first_price = df["close"].iloc[0]
    last_price = df["close"].iloc[-1]
    change_percent = ((last_price - first_price) / first_price) * 100
    status = "🔥" if abs(change_percent) > 5 else "⚡" if abs(change_percent) > 2 else "🛡️"
    return f"{change_percent:.2f}% {status}"

# ---------------------------
# ฟังก์ชันวัดเทรนด์ (EMA, MACD, RSI)
# ---------------------------
def detect_trend(df):
    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()
    
    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9).mean()
    
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    last_ema20, last_ema50 = df["EMA20"].iloc[-1], df["EMA50"].iloc[-1]
    last_macd, last_signal = df["MACD"].iloc[-1], df["Signal"].iloc[-1]
    last_rsi = df["RSI"].iloc[-1]
    
    if last_ema20 > last_ema50 and last_macd > last_signal and last_rsi > 50:
        return f"{Fore.GREEN}⚔️ Bullish Power! 💥 นักสู้กำลังรุก!{Style.RESET_ALL}"
    elif last_ema20 < last_ema50 and last_macd < last_signal and last_rsi < 50:
        return f"{Fore.RED}🛡️ Bearish Defense! 😓 นักสู้กำลังถอย!{Style.RESET_ALL}"
    else:
        return f"{Fore.YELLOW}🏳️ Neutral Zone! ⚖️ สงบศึกชั่วคราว{Style.RESET_ALL}"

# ---------------------------
# ฟังก์ชันดึงราคา OHLCV
# ---------------------------
def get_ohlcv(symbol, timeframe="1h", limit=200):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# ---------------------------
# ดึง 20 เหรียญที่มี Volume สูงสุด
# ---------------------------
def get_top_20_symbols():
    exchange = ccxt.binance()
    tickers = exchange.fetch_tickers()
    usdt_symbols = [(s, tickers[s]["quoteVolume"]) for s in tickers if s.endswith("/USDT")]
    usdt_symbols = sorted(usdt_symbols, key=lambda x: x[1], reverse=True)[:20]
    return [s[0] for s in usdt_symbols]

# ---------------------------
# สร้าง Battle Report สำหรับแต่ละเหรียญ
# ---------------------------
def create_battle_report(symbol, df):
    current_price = df["close"].iloc[-1]
    swing_high = df["high"].max()
    swing_low = df["low"].min()
    price_hp, percentage = price_bar(current_price, swing_high, swing_low)
    atk = price_atk(df)
    trend = detect_trend(df)
    
    msg = f"{Fore.RED}⚔️ {symbol} (1h) - Battle Report ⚔️{Style.RESET_ALL}\n"
    msg += f"{trend}\n"
    msg += f"💰 Current Price: {current_price:.2f}\n"
    msg += f"🩸 Price HP: {price_hp}\n"
    msg += f"🎯 Swing High: {swing_high:.2f}\n"
    msg += f"🎯 Swing Low: {swing_low:.2f}\n"
    msg += f"💥 Price ATK: {atk}\n"
    msg += "-" * 50 + "\n"
    return msg

# ---------------------------
# Main Program
# ---------------------------
if __name__ == "__main__":
    print(GAME_HEADER)
    
    print(f"{Fore.CYAN}⏳ กำลังสแกนสนามรบ... ดึง 20 นักสู้ที่แข็งแกร่งที่สุด!{Style.RESET_ALL}")
    symbols = get_top_20_symbols()
    
    print(f"\n{Fore.YELLOW}📊 Battle Reports สำหรับ 20 นักสู้ (Timeframe: 1h, 200 รอบ){Style.RESET_ALL}\n")
    
    for symbol in symbols:
        try:
            df = get_ohlcv(symbol, timeframe="1h", limit=200)
            report = create_battle_report(symbol, df)
            print(report)
        except Exception as e:
            print(f"{Fore.RED}⚠️ ข้อผิดพลาดสำหรับ {symbol}: {str(e)}{Style.RESET_ALL}\n")
            continue