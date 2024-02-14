import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack as ft

from alpaca.data import StockHistoricalDataClient, TimeFrame
from alpaca.data.requests import StockQuotesRequest, StockBarsRequest

#idk what any of this shit does
ALPACA_API_KEY_ID = 'API_KEY'
ALPACA_API_SECRET_KEY = 'SECRET_KEY'

# Instantiate a data client
data_client = StockHistoricalDataClient(ALPACA_API_KEY_ID, ALPACA_API_SECRET_KEY)

# Set the start time
start_time = pd.to_datetime("2023-02-14").tz_localize('America/New_York')

# It's generally best to explicitly provide an end time but will default to 'now' if not
request_params = StockBarsRequest(
    symbol_or_symbols=['SOYB'],
    timeframe=TimeFrame.Day,
    start=start_time
    )

bars_df = data_client.get_stock_bars(request_params).df.tz_convert('America/New_York', level=1)

#making data frame of stock prices into 2-dim list
stock_data = bars_df.values.tolist()

#detrending the data for open and close prices
dtrend_open, dtrend_close = [], []

for i in range(len(stock_data) - 1):
    dtrend_open.append(float(stock_data[i][0]) - float(stock_data[i + 1][0]))
    dtrend_close.append(float(stock_data[i][3]) - float(stock_data[i + 1][3]))

freq = ft.fftfreq(len(dtrend_open))
spec = np.abs(ft.fft(dtrend_open))

# Find indices of dominant frequencies
num_dom_freq = 5  # Adjust as needed
dominant_indices = np.argsort(spec)[::-1][:num_dom_freq]

# Extract dominant frequencies
dominant_freq = freq[dominant_indices]

print("Dominant frequencies:", dominant_freq)

# Forecasting up to 45 periods in advance
forecast_periods = 45

# Extend the spectrum for forecasting
extended_spec = np.concatenate((spec, np.zeros(forecast_periods)))

# Inverse FFT to get the forecasted data
forecast = np.real(ft.ifft(extended_spec))

# Plotting the original and forecasted data
plt.plot(dtrend_open, label='Original Data')
plt.plot(range(len(dtrend_open), len(dtrend_open) + forecast_periods), forecast[-forecast_periods:], label='Forecasted Data')
plt.legend()
plt.show()


