import numpy as np
import pandas as pd

from database import DataBase
from score import StockScore
from finditem import EqualWeight, FilterItem
from portfolio import PortOptim
from evaluation import Evaluation


class Investment:
    # TODO: check architecture
    def __init__(self, period):
        self.period = period  # unit: month

    def select_item(self, factor):
        return

    def rebalance(self, price):
        return

    def returns_by_quarter(self, price_start, price_end, weight):
        return

    def run_invest_simulation(self, y_start, y_end):

        for y in range(y_start, y_end):
            # TODO: loop for quarter

        return
