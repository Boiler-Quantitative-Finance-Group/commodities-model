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
        self.SetStartDate(2023, 3, 1)
        self.SetCash(100000)
        equity = self.AddEquity("SOYB")
        option = self.AddOption("SOYB")
        self.symbol = option.Symbol
        option.SetFilter(-10, 10)
        option.SetFilter(timedelta(30), timedelta(60))
        option.SetFilter(-10, +10, 0, 180)

        # Initialize variables for FFT
        self.fft_window_size = 256  # Window size for FFT
        # Get historical data for detrending and FFT
        history = self.History("SOYB", self.fft_window_size, Resolution.Daily)
        # Extract closing prices from history
        close_prices = [float(bar.Close) for bar in history]
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
        forecast_periods = 5
        # Extend the spectrum for forecasting
        extended_spec = np.concatenate((spec, np.zeros(forecast_periods)))
        # Inverse FFT to get the forecasted data
        forecast = np.real(ft.ifft(extended_spec))
        self.Log("Forecast: {}".format(forecast))
        self.forecast = forecast[-forecast_periods:]

    def is_bullish_forecast(self, forecast, current_price):
        # Check if the forecast is bullish
        return forecast[0] > current_price

    def OnData(self, slice: Slice) -> None:
        equity_data = slice.OptionChains
        if equity_data is not None and self.symbol in equity_data:
            # Select the option chain
            chain = equity_data[self.symbol]
            if chain is not None:
                # Select ATM call and put options
                atm_call = [option for option in chain if option.Right == OptionRight.Call and option.Strike == option.UnderlyingLastPrice]
                atm_put = [option for option in chain if option.Right == OptionRight.Put and option.Strike == option.UnderlyingLastPrice]

                if len(atm_call) > 0 and len(atm_put) > 0:
                    # Buy ATM call option
                    self.Buy(atm_call[0].Symbol, 1)
                    # Sell OTM call option (higher strike price)
                    otm_call = [option for option in chain if option.Right == OptionRight.Call and option.Strike > option.UnderlyingLastPrice]
                    if len(otm_call) > 0:
                        self.Sell(otm_call[0].Symbol, 1)
                    # Buy ATM put option
                    self.Buy(atm_put[0].Symbol, 1)
                    # Sell OTM put option (lower strike price)
                    otm_put = [option for option in chain if option.Right == OptionRight.Put and option.Strike < option.UnderlyingLastPrice]
                    if len(otm_put) > 0:
                        self.Sell(otm_put[0].Symbol, 1)

                    # Close positions based on profit targets
                    for holding in self.Portfolio.Values:
                        if holding.Invested:
                            # Example: Close position if it has gained 5%
                            if holding.UnrealizedProfitPercent > 5:
                                self.Liquidate(holding.Symbol)
            else:
                self.Log("Option data not available for symbol {}".format(self.symbol))
