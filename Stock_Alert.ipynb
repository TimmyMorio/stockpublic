!pip install yfinance ta

import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ta.momentum import RSIIndicator

# Email configuration
EMAIL_USER = 'timshurmelev@mail.ru'
EMAIL_PASSWORD = 'tgjcSvQNwTUpT5XAfZnk'

# Function to send a single email
def send_email(subject, body, to_email):
    from_email = EMAIL_USER
    password = EMAIL_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.mail.ru', 587) as server:
            server.starttls()
            server.login(from_email, password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
        print(f"Email sent to: {to_email} - {subject}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to calculate support and resistance levels
def calculate_levels(data, window=90):
    data['Support'] = data['Low'].rolling(window=window).min()
    data['Resistance'] = data['High'].rolling(window=window).max()
    return data

# Function to check trading signals
def check_trading_signals(stock_list, window=90, threshold=0.01, stop_loss=0.07, take_profit=0.25):
    result = []
    failed_tickers = []

    for stock in stock_list:
        try:
            data = yf.download(stock, period='1y', interval='1d', auto_adjust=False)

            if data.empty or data.isnull().values.any():
                print(f"No or invalid data for {stock}. Skipping...")
                failed_tickers.append(stock)
                continue

            data = calculate_levels(data, window)
            close_prices = data['Close'].squeeze()

            rsi_indicator = RSIIndicator(close=close_prices, window=14)
            data['RSI'] = rsi_indicator.rsi()

            last_close = close_prices.iloc[-1].item()
            last_support = data['Support'].iloc[-1].item()
            last_resistance = data['Resistance'].iloc[-1].item()
            last_rsi = data['RSI'].iloc[-1].item()
            volume_avg = data['Volume'].rolling(20).mean().iloc[-1].item()
            last_volume = data['Volume'].iloc[-1].item()

            # BUY signal: near support, RSI between 30 and 70, volume above average
            if (last_close <= last_support * (1 + threshold)) and (30 < last_rsi < 70) and (last_volume > volume_avg):
                result.append({'Stock': stock, 'Type': 'BUY', 'Close': last_close, 'Support': last_support, 'RSI': last_rsi})

            # SELL signal: near resistance, RSI below 70
            if (last_close >= last_resistance * (1 - threshold)) and (last_rsi < 70):
                result.append({'Stock': stock, 'Type': 'SELL', 'Close': last_close, 'Resistance': last_resistance, 'RSI': last_rsi})

            # STOP LOSS signal: price drops below stop loss threshold
            if (last_close <= last_support * (1 - stop_loss)):
                result.append({'Stock': stock, 'Type': 'STOP LOSS', 'Close': last_close, 'Support': last_support, 'RSI': last_rsi})

            # TAKE PROFIT signal: price increases above take profit threshold (25%)
            if (last_close >= last_support * (1 + take_profit)):
                result.append({'Stock': stock, 'Type': 'TAKE PROFIT', 'Close': last_close, 'Support': last_support, 'RSI': last_rsi})

        except Exception as e:
            print(f"Unexpected error for {stock}: {e}")
            failed_tickers.append(stock)

    return pd.DataFrame(result), failed_tickers

# Define stock list
stock_list = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'AMD', 'NFLX', 'PYPL',
    'SQ', 'SHOP', 'SNOW', 'INTC', 'CSCO', 'ORCL', 'IBM', 'JPM', 'BAC', 'WFC',
    'GS', 'MS', 'V', 'MA', 'AXP', 'BRK-B', 'JNJ', 'PFE', 'MRK', 'ABBV', 'UNH',
    'ABT', 'BMY', 'XOM', 'CVX', 'COP', 'SLB', 'WMT', 'COST', 'TGT', 'HD', 'LOW',
    'MCD', 'SBUX', 'KO', 'PEP', 'F', 'GM', 'NIO', 'LI', 'XPEV', 'BABA', 'TSM',
    'TCEHY', 'JD', 'PLTR', 'AI', 'RIVN', 'LCID', 'BLNK', 'CHPT',
    'CRSP', 'EDIT', 'NTLA', 'MRNA', 'NVAX', 'DDOG', 'OKTA', 'ZS', 'MDB', 'U',
    'SE', 'MELI', 'PDD', 'LLY', 'GILD', 'REGN', 'VRTX', 'ISRG',
    'ENPH', 'SEDG', 'PLUG', 'FSLR', 'BE', 'TTWO', 'EA', 'DIS',
    'AFRM', 'SOFI', 'NU', 'SPCE', 'RKLB', 'C', 'USB', 'PNC', 'SCHW'
]

# Run the check
results, failed_tickers = check_trading_signals(stock_list)

# Prepare email bodies
buy_sell_signals = results[results['Type'].isin(['BUY', 'SELL'])]
tp_sl_signals = results[results['Type'].isin(['TAKE PROFIT', 'STOP LOSS'])]

# Email for BUY and SELL signals
if not buy_sell_signals.empty:
    email_body_buy_sell = "BUY and SELL Trading Signals:\n\n"
    for idx, row in buy_sell_signals.iterrows():
        email_body_buy_sell += f"{row['Stock']}: {row['Type']} at {row['Close']:.2f}, RSI: {row['RSI']:.2f}\n"
    send_email("BUY/SELL Trading Signals", email_body_buy_sell, EMAIL_USER)
else:
    send_email("BUY/SELL Trading Signals", "No BUY or SELL signals today.", EMAIL_USER)

# Email for TAKE PROFIT and STOP LOSS signals
if not tp_sl_signals.empty:
    email_body_tp_sl = "TAKE PROFIT and STOP LOSS Signals:\n\n"
    for idx, row in tp_sl_signals.iterrows():
        email_body_tp_sl += f"{row['Stock']}: {row['Type']} at {row['Close']:.2f}, RSI: {row['RSI']:.2f}\n"
    send_email("TAKE PROFIT/STOP LOSS Signals", email_body_tp_sl, EMAIL_USER)
else:
    send_email("TAKE PROFIT/STOP LOSS Signals", "No TAKE PROFIT or STOP LOSS signals today.", EMAIL_USER)

# Show results
print("\nTrading Signals:")
print(results)

# Show failed tickers
if failed_tickers:
    print("\nFailed tickers:")
    for ticker in failed_tickers:
        print(ticker)
