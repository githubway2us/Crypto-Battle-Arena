from flask import Flask, render_template, request
import ccxt
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# ASCII Art for game theme
GAME_HEADER = """
🕹️ Crypto Battle Arena - Quick Report 🕹️
⚔️ สแกนนักสู้ทั้งหมดในสนามรบ! ⚔️
"""

# ---------------------------
# ฟังก์ชันสร้าง Price Bar
# ---------------------------
def price_bar(current_price, swing_high, swing_low):
    try:
        total_range = swing_high - swing_low
        if total_range == 0:
            return "[██████████] 100% 💪", 100.0
        normalized_price = (current_price - swing_low) / total_range
        filled = int(normalized_price * 10)
        filled = max(0, min(filled, 10))
        bar = f"{'█' * filled}{'░' * (10 - filled)}"
        percentage = normalized_price * 100
        status = "💪" if percentage > 70 else "⚠️" if percentage > 30 else "🩸"
        return f"{bar} {percentage:.1f}% {status}", percentage
    except Exception as e:
        logging.error(f"Error in price_bar: {str(e)}")
        return "N/A", 0.0

# ---------------------------
# ฟังก์ชันคำนวณ Price ATK
# ---------------------------
def price_atk(df):
    try:
        first_price = df["close"].iloc[0]
        last_price = df["close"].iloc[-1]
        change_percent = ((last_price - first_price) / first_price) * 100
        status = "🔥" if abs(change_percent) > 5 else "⚡" if abs(change_percent) > 2 else "🛡️"
        return f"{change_percent:.2f}% {status}"
    except Exception as e:
        logging.error(f"Error in price_atk: {str(e)}")
        return "N/A"

# ---------------------------
# ฟังก์ชันวัดเทรนด์
# ---------------------------
def detect_trend(df):
    try:
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
            return "⚔️ Bullish Power! 💥 นักสู้กำลังรุก!"
        elif last_ema20 < last_ema50 and last_macd < last_signal and last_rsi < 50:
            return "🛡️ Bearish Defense! 😓 นักสู้กำลังถอย!"
        else:
            return "🏳️ Neutral Zone! ⚖️ สงบศึกชั่วคราว"
    except Exception as e:
        logging.error(f"Error in detect_trend: {str(e)}")
        return "⚠️ Trend calculation failed"

# ---------------------------
# ฟังก์ชันดึงราคา OHLCV
# ---------------------------
def get_ohlcv(symbol, timeframe="1h", limit=200):
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        logging.error(f"Error fetching OHLCV for {symbol}: {str(e)}")
        return None

# ---------------------------
# ดึงทุกเหรียญ USDT
# ---------------------------
def get_all_usdt_symbols():
    try:
        exchange = ccxt.binance()
        tickers = exchange.fetch_tickers()
        usdt_symbols = [s for s in tickers if s.endswith("/USDT")]
        logging.info(f"Fetched {len(usdt_symbols)} USDT symbols")
        return usdt_symbols
    except Exception as e:
        logging.error(f"Error fetching USDT symbols: {str(e)}")
        return []

# ---------------------------
# สร้าง Battle Report
# ---------------------------
def create_battle_report(symbol, df):
    try:
        current_price = df["close"].iloc[-1]
        swing_high = df["high"].max()
        swing_low = df["low"].min()
        price_hp, percentage = price_bar(current_price, swing_high, swing_low)
        atk = price_atk(df)
        trend = detect_trend(df)
        
        return {
            "symbol": symbol,
            "trend": trend,
            "current_price": f"{current_price:.2f}",
            "price_hp": price_hp,
            "swing_high": f"{swing_high:.2f}",
            "swing_low": f"{swing_low:.2f}",
            "price_atk": atk
        }
    except Exception as e:
        logging.error(f"Error creating battle report for {symbol}: {str(e)}")
        return {
            "symbol": symbol,
            "trend": f"⚠️ Error: {str(e)}",
            "current_price": "N/A",
            "price_hp": "N/A",
            "swing_high": "N/A",
            "swing_low": "N/A",
            "price_atk": "N/A"
        }

# ---------------------------
# Flask Routes
# ---------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    timeframe = "1h"
    limit = 200
    error_message = None
    reports = []
    
    timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    
    if request.method == 'POST':
        timeframe = request.form.get('timeframe', "1h")
        limit_input = request.form.get('limit', "200")
        try:
            limit = int(limit_input)
            if limit < 1 or limit > 1000:
                limit = 200
                error_message = "จำนวนแท่งเทียนต้องอยู่ระหว่าง 1 ถึง 1000"
        except ValueError:
            limit = 200
            error_message = "กรุณากรอกจำนวนแท่งเทียนเป็นตัวเลข"
    
    symbols = get_all_usdt_symbols()
    if not symbols:
        error_message = "ไม่สามารถดึงรายการเหรียญ USDT ได้ กรุณาลองใหม่ภายหลัง"
    
    for symbol in symbols[:20]:  # Limit to 20 symbols for testing to avoid rate limits
        df = get_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if df is not None and not df.empty:
            report = create_battle_report(symbol, df)
            reports.append(report)
        else:
            reports.append({
                "symbol": symbol,
                "trend": "⚠️ ไม่สามารถดึงข้อมูล OHLCV ได้",
                "current_price": "N/A",
                "price_hp": "N/A",
                "swing_high": "N/A",
                "swing_low": "N/A",
                "price_atk": "N/A"
            })
    
    return render_template('index.html',
                         header=GAME_HEADER,
                         reports=reports,
                         timeframes=timeframes,
                         selected_timeframe=timeframe,
                         selected_limit=limit,
                         error_message=error_message)

# ---------------------------
# Main Program
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)