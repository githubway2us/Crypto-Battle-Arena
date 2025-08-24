# Crypto Battle Arena

[![Flask Web App](https://img.shields.io/badge/Flask-Web%20App-blue)](https://flask.palletsprojects.com/) [![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

**Crypto Battle Arena** is a Flask-based web application that fetches real-time cryptocurrency trading data from Binance for all USDT trading pairs. It presents market analysis in a game-themed format, displaying battle reports for each coin with metrics such as price, trend (bullish, bearish, or neutral), and percentage changes, styled as "Price HP" and "Price ATK." Reports are shown in a responsive 4-cards-per-row grid with an animated loading status bar during data fetching.

## Features

- **All USDT Pairs**: Fetches all USDT trading pairs from Binance (limited to 20 for testing to avoid API rate limits).
- **Customizable Parameters**: Users can select the timeframe (e.g., 1m, 5m, 1h, 1d) and number of candlesticks (1–1000) via a web form.
- **Battle Report Metrics**:
  - **Price HP**: Visualizes the current price relative to swing high/low as a progress bar.
  - **Price ATK**: Displays the percentage price change with status indicators (🔥, ⚡, 🛡️).
  - **Trend Detection**: Uses EMA (20, 50), MACD, and RSI to determine bullish, bearish, or neutral trends.
- **Responsive Grid Layout**: Displays reports as cards in a 4-column CSS Grid, adjusting to 3, 2, or 1 column(s) on smaller screens.
- **Loading Status Bar**: Shows an animated green progress bar during form submission to indicate data fetching.
- **Error Handling**: Robust logging for Binance API issues and user-friendly error messages for invalid inputs.
- **Game-Themed UI**: Features emoji-based visuals and color-coded trends (green for bullish, red for bearish, yellow for neutral).

## Prerequisites

- **Python 3.8+**
- **Dependencies**:
  - `flask`: Web framework for the application.
  - `ccxt`: Library for Binance API interaction.
  - `pandas`: For data processing and analysis.
- **Internet Connection**: Required for Binance API calls.
- **Browser**: Modern browser (e.g., Chrome, Firefox) for the web interface.

Install dependencies using:
```bash
pip install flask ccxt pandas
