import numpy as np
import pandas as pd

path_factors = 'dataset/dataset_total.xlsx'
path_price = 'dataset/dataset_price_daily.xlsx'


class DataBase:
    def __init__(self, type='both'):
        self.type = type
        self.factor_kospi = None
        self.factor_kosdaq = None
        self.factor = None
        self.price = None

    def load_database_full(self):
        self.factor_kospi = pd.read_excel(path_factors, sheet_name='kospi_factor')
        self.factor_kosdaq = pd.read_excel(path_factors, sheet_name='kosdaq_factor')
        self.price = pd.read_excel(path_price, sheet_name='Sheet3')

    def get_database_full(self):
        self.factor = self.factor_kospi.append(self.factor_kosdaq)
        return {'price': self.price, 'factor': self.factor}

    def unload_database(self):
        self.fator_kospi = None
        self.fator_kosdaq = None
        self.price = None
        self.factor = None

    def load_factor_by_year(self, year):
        if self.type == 'both':
            if self.factor_kospi is None:
                self.factor_kospi = pd.read_excel(path_factors, sheet_name='kospi_factor')
            if self.factor_kosdaq is None:
                self.factor_kosdaq = pd.read_excel(path_factors, sheet_name='kosdaq_factor')

            factor_kospi = self.factor_kospi[['Symbol', 'Symbol Name', 'Item', 'Item Name', year]]
            factor_kosdaq = self.factor_kosdaq[['Symbol', 'Symbol Name', 'Item', 'Item Name', year]]
            factors = factor_kospi.append(factor_kosdaq)

        elif self.type == 'kospi':
            if self.factor_kospi is None:
                self.factor_kospi = pd.read_excel(path_factors, sheet_name='kospi_factor')

            factors = self.factor_kospi[['Symbol', 'Symbol Name', 'Item', 'Item Name', year]]

        elif self.type == 'kosdaq':
            if self.factor_kosdaq is None:
                self.factor_kosdaq = pd.read_excel(path_factors, sheet_name='kosdaq_factor')

            factors = self.factor_kosdaq[['Symbol', 'Symbol Name', 'Item', 'Item Name', year]]

        else:
            raise NotImplementedError()
        return factors

    def load_price_by_year(self, year):
        if self.price is None:
            self.price = pd.read_excel(path_price, sheet_name='Sheet3')

        price = self.price[self.price.Date.between(str(year) + '0101', str(year) + '1231')]
        return price


if __name__ == '__main__':
    test = DataBase(type='both')
    a = test.load_factor_by_year(year=2012)
    b = test.load_price_by_year(year=2012)
    test.load_database_full()
