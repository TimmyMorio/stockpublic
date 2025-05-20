import yfinance as yf
import pandas as pd
from alpaca_trade_api.rest import REST
from ta.momentum import RSIIndicator
import numpy as np

# Alpaca API credentials 
ALPACA_API_KEY = 'PKX5F9TMALNB58HNNU59'
ALPACA_SECRET_KEY = 'BbX1mN2QBQAydduIX0lKXQthEscg4OmXkdISKsS6'
BASE_URL = 'https://paper-api.alpaca.markets/v2'

# Инициализация клиента Alpaca
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')

# Фиксированная сумма на каждую сделку
fixed_amount = 20  

# Функция для расчета уровней поддержки и сопротивления
def calculate_levels(data, window=90):
    data['Support'] = data['Low'].rolling(window=window).min()
    data['Resistance'] = data['High'].rolling(window=window).max()
    return data

# Проверка открытых позиций
def has_position(symbol):
    try:
        position = api.get_position(symbol)
        qty = float(position.qty)
        return qty > 0
    except:
        return False

# Проверка на наличие открытых ордеров
def has_open_order(symbol):
    open_orders = api.list_orders(status='open', symbols=[symbol])
    return len(open_orders) > 0

# Функция для проверки торговых сигналов и выполнения сделок
def check_trading_signals_and_execute(stock_list, window=90, threshold=0.01, stop_loss=0.07, take_profit=0.25):
    result = []
    failed_tickers = []

    for stock in stock_list:
        try:
            # Загрузка исторических данных
            data = yf.download(stock, period='1y', interval='1d', auto_adjust=False, group_by='ticker')

            if data.empty or data.isnull().values.any():
                print(f"No or invalid data for {stock}. Skipping...")
                failed_tickers.append(stock)
                continue

            # Если данные имеют многоуровневые колонки — преобразуем их
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(1)

            # Диагностика: проверка формы данных после преобразования
            print(f"\n--- Diagnosing {stock} ---")
            for col in data.columns:
                print(f"Column: {col}, Shape: {data[col].shape}")

            # Расчет уровней поддержки и сопротивления
            data = calculate_levels(data, window)

            # Расчет индикатора RSI
            close_prices = data['Close']
            rsi_indicator = RSIIndicator(close=close_prices, window=14)
            data['RSI'] = rsi_indicator.rsi()

            # Получение последних значений
            last_close = float(close_prices.iloc[-1])
            last_support = float(data['Support'].iloc[-1])
            last_resistance = float(data['Resistance'].iloc[-1])
            last_rsi = float(data['RSI'].iloc[-1])
            volume_avg = float(data['Volume'].rolling(20).mean().iloc[-1])
            last_volume = float(data['Volume'].iloc[-1])

            # BUY signal
            if (last_close <= last_support * (1 + threshold)) and (last_rsi > 30) and (last_volume > volume_avg):
                if not has_position(stock) and not has_open_order(stock):  # Проверка позиции и открытого ордера
                    qty = round(fixed_amount / last_close, 4)  # Дробное количество акций
                    result.append({'Stock': stock, 'Type': 'BUY', 'Close': last_close, 'Qty': qty})
                    print(f"BUY Signal for {stock} at {last_close}, Qty: {qty}")
                    api.submit_order(
                        symbol=stock,
                        notional=fixed_amount,  # Покупаем на $20
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                else:
                    print(f"Skipping BUY for {stock} — Position held or order pending.")

            # SELL signal — продаем все купленные акции
            if pd.notnull(last_resistance) and (last_close >= last_resistance * (1 - threshold)) and (last_rsi < 70):
                if has_position(stock) and not has_open_order(stock):
                    position = api.get_position(stock)
                    qty = int(float(position.qty))  # Продаем всё, что есть
                    result.append({'Stock': stock, 'Type': 'SELL', 'Close': last_close, 'Qty': qty})
                    print(f"SELL Signal for {stock} at {last_close}, Qty: {qty}")
                    api.submit_order(
                        symbol=stock,
                        qty=qty,
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )
                else:
                    print(f"Skipping SELL for {stock} — No position held or order pending.")

            # STOP LOSS signal — продаем все, если цена упала ниже стоп-лосса
            if pd.notnull(last_support) and (last_close <= last_support * (1 - stop_loss)):
                if has_position(stock) and not has_open_order(stock):
                    position = api.get_position(stock)
                    qty = int(float(position.qty))  # Продаем всё
                    result.append({'Stock': stock, 'Type': 'STOP LOSS', 'Close': last_close, 'Qty': qty})
                    print(f"STOP LOSS Triggered for {stock} at {last_close}, Qty: {qty}")
                    api.submit_order(
                        symbol=stock,
                        qty=qty,
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )
                else:
                    print(f"Skipping TAKE PROFIT for {stock} — No position held or order pending.")

            # TAKE PROFIT signal — продаем всё, если цена выросла на take_profit
            if pd.notnull(last_support) and (last_close >= last_support * (1 + take_profit)):
                if has_position(stock) and not has_open_order(stock):
                    position = api.get_position(stock)
                    qty = int(float(position.qty))  # Продаем всё
                    result.append({'Stock': stock, 'Type': 'TAKE PROFIT', 'Close': last_close, 'Qty': qty})
                    print(f"TAKE PROFIT Triggered for {stock} at {last_close}, Qty: {qty}")
                    api.submit_order(
                        symbol=stock,
                        qty=qty,
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )
                else:
                    print(f"Skipping TAKE PROFIT for {stock} — No position held or order pending.")

        except Exception as e:
            print(f"Error for {stock}: {e}")
            failed_tickers.append(stock)

    return pd.DataFrame(result), failed_tickers

# Список акций для проверки
stock_list = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'JNJ', 'V', 'PG', 'JPM',
    'UNH', 'MA', 'HD', 'BAC', 'DIS', 'VZ', 'NFLX', 'ADBE', 'CRM', 'INTC', 'PFE',
    'KO', 'PEP', 'CSCO', 'XOM', 'T', 'MRK', 'WMT', 'BA', 'MCD', 'NKE', 'IBM',
    'GE', 'ORCL', 'ABT', 'CVX', 'MDT', 'HON', 'ACN', 'AVGO', 'QCOM', 'TXN',
    'LLY', 'DHR', 'LIN', 'BMY', 'PM', 'MMM', 'AMGN', 'AMT', 'SPGI', 'NEE',
    'LOW', 'MS', 'GS', 'NOW', 'INTU', 'BLK', 'RTX', 'SCHW', 'TMO', 'UNP',
    'AXP', 'ISRG', 'PLD', 'BKNG', 'ADP', 'ZTS', 'MDLZ', 'SYK', 'COST', 'LMT',
    'USB', 'GILD', 'CB', 'C', 'DE', 'PYPL', 'UPS', 'TMUS', 'AMAT',
    'CVS', 'CI', 'TGT', 'BDX', 'MO', 'DUK', 'SO', 'CCI', 'NSC', 'CL', 'GM',
    'MMM', 'F', 'HUM', 'CAT', 'EL', 'WM', 'PNC', 'COP', 'MMC', 'TJX', 'SHW',
    'APD', 'ICE', 'GS', 'SPG', 'EW', 'ITW', 'D', 'SRE', 'ETN', 'FIS',
    'ADSK', 'EMR', 'HCA', 'MCO', 'AON', 'KLAC', 'ADP', 'VRTX', 'MPC', 'PSA',
    'BK', 'AEP', 'ADI', 'ECL', 'CTSH', 'ROP', 'NOC', 'EXC', 'PGR', 'MSCI',
    'SLB', 'ILMN', 'APTV', 'CDNS', 'MNST', 'EBAY', 'SNPS', 'ORLY',
    'MAR', 'KMB', 'AFL', 'WBA', 'LRCX', 'IDXX', 'TRV', 'STZ', 'CTAS', 'AZO',
    'MCHP', 'PAYX', 'WELL', 'SYY', 'ALL', 'PRU', 'CMG', 'TEL', 'HPQ', 'SPGI',
    'FTNT', 'DLR', 'VLO', 'RMD', 'WEC', 'EOG', 'PPG', 'NEM', 'ES', 'PEG',
    'ED', 'XEL', 'AEE', 'DTE', 'CMS', 'WMB', 'OKE', 'KMI', 'ET', 'MPLX', 'EPD',
    'PAA', 'ENB', 'TRP', 'KHC', 'GIS', 'K', 'SJM', 'HSY', 'CPB', 'CAG', 'MDLZ',
    'HRL', 'MKC', 'TSN', 'LVS', 'WYNN', 'MGM', 'HST', 'MAR', 'HLT', 'RCL',
    'NCLH', 'CCL', 'AAL', 'DAL', 'UAL', 'LUV', 'ALGT', 'SKYW', 'CPA', 'CNI',
    'CP', 'UNP', 'CSX', 'NSC', 'SPY', 'VOO', 'IVV', 'VTI', 'QQQ', 'DIA', 'IWM',
    'IJH', 'IJR', 'AGG', 'LQD', 'HYG', 'SHY', 'IEF', 'TLT', 'BND', 'TIP', 'MUB',
    'VWO', 'EFA', 'IEFA', 'EEM', 'ACWI', 'VXUS', 'VEU', 'VSS', 'SCZ', 'GWX',
    'DGS', 'DEM', 'DVY', 'VYM', 'HDV', 'SDY', 'VIG', 'SCHD', 'SPHD', 'SPYD',
    'SPLV', 'USMV', 'MTUM', 'QUAL', 'VLUE', 'IWF', 'IWD', 'IWB', 'IWR', 'IWS',
    'IWP', 'IWO', 'IWN', 'IWV', 'IUSG', 'IUSV', 'IUSB', 'IAGG', 'SHV', 'SHY',
    'IEI', 'IEF', 'TLT', 'GOVT', 'MBB', 'FLOT', 'SHYG', 'HYG', 'JNK', 'SJNK',
    'EMB', 'VWOB', 'IGOV', 'BWX', 'LQD', 'VCIT', 'VCSH', 'VCLT', 'BKLN',
    'SRLN', 'HYD', 'BAB', 'MUB', 'TFI', 'SHM', 'ITM', 'MLN', 'SUB', 'PZA',
    'PZT', 'PVI', 'SHYD', 'HYMB', 'VTEB', 'BND', 'AGG', 'SCHZ', 'BIV', 'BSV',
    'BLV', 'BNDX'
]

# Запуск проверки торговых сигналов и выполнения сделок
results, failed_tickers = check_trading_signals_and_execute(stock_list)

# Вывод результатов
print("\nTrading Signals:")
print(results)

if failed_tickers:
    print("\nFailed tickers:")
    for ticker in failed_tickers:
        print(ticker)
