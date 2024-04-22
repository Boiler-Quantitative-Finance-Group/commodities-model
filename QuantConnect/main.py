# region imports
from AlgorithmImports import *

# FFT
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack as ft
import os
from collections import deque

# endregion

class AlertGreenHorse(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 3, 20)
        self.SetCash(100000)
        equity = self.AddEquity("SOYB")
        option = self.AddOption("SOYB")
        self.symbol = option.Symbol
        option.SetFilter(-10,10)
        option.SetFilter(timedelta(30), timedelta(60))
        option.SetFilter(-10, +10, 0, 180)
        
        # Initialize variables for FFT
        self.fft_window_size = 256  # Window size for FFT
        # Get historical data for detrending and FFT
        history = self.History("SOYB", self.fft_window_size, Resolution.Daily)
        # Extract closing prices from history
        close_prices = [float(bar["close"]) for bar in history]
        # Detrend the closing prices
        self.dtrend_close = np.diff(close_prices)
        # Perform FFT
        freq = ft.fftfreq(len(self.dtrend_close))
        spec = np.abs(ft.fft(self.dtrend_close))
        # Find indices of dominant frequencies
        num_dom_freq = 5  # Adjust as needed
        dominant_indices = np.argsort(spec)[::-1][:num_dom_freq]
        # Log dominant frequencies
        self.Log("Dominant frequencies indices: {}".format(dominant_indices))
        # Make a prediction
        # Forecasting up to 45 periods in advance
        forecast_periods = 25
        # Extend the spectrum for forecasting
        extended_spec = np.concatenate((spec, np.zeros(forecast_periods)))
        # Inverse FFT to get the forecasted data
        forecast = np.real(ft.ifft(extended_spec))
        self.Log("Forecast: {}".format(forecast))
        self.forecast = forecast[-forecast_periods:]

    def is_bullish_forecast(self, forecast, current_price):
        # Placeholder
        return forecast[-1] > current_price

    def OnData(self, slice: Slice) -> None:
        equity_data = slice["SOYB"]
        if equity_data:
            current_price = self.Securities["SOYB"].Price
            # If the forecast is bullish, create a bull spread
            if self.is_bullish_forecast(self.forecast, current_price):
                self.Buy("SOYB", 100)
                self.Sell("SOYB", 100, limit_price=current_price + 1)
            # If the forecast is bearish, create a bear spread
            elif not self.is_bullish_forecast(self.forecast, current_price):
                self.Sell("SOYB", 100)
                self.Buy("SOYB", 100, limit_price=current_price - 1)

            # TODO: Make a trade decision
            # TODO: Execute the trade
