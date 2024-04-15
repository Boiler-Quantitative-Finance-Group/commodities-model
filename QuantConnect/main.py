# region imports
from AlgorithmImports import *

# FFT
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack as ft
import os

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
        # TODO: Detrend the values for longer time frames
        # Pretend we detrended the data
        self.dtrend_close = deque(maxlen=self.fft_window_size)  # Store closing prices for FFT

    def OnData(self, slice: Slice) -> None:
        equity_data = slice["SOYB"]
        if equity_data:
            # Append close price to deque
            self.dtrend_close.append(equity_data.Close)
            
            if len(self.dtrend_close) == self.fft_window_size:
                # Perform FFT
                freq = ft.fftfreq(len(self.dtrend_close))
                spec = np.abs(ft.fft(self.dtrend_close))
                
                # Find indices of dominant frequencies
                num_dom_freq = 5  # Adjust as needed
                dominant_indices = np.argsort(spec)[::-1][:num_dom_freq]
                
                # Log dominant frequencies
                self.Log("Dominant frequencies indices: {}".format(dominant_indices))

                # TODO: Make a trade decision
                # TODO: Excecute the trade
