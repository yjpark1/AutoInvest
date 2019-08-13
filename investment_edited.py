import numpy as np
import pandas as pd

from database import DataBase
from score import StockScore
from finditem import EqualWeight, FilterItem
from portfolio import PortOptim
from evaluation import Evaluation


###
def noise_func(x, noise_factor=2):
    return np.random.randn(len(x)) * noise_factor

def make_base_signals(x,type='sin',scale_factor = 1,bias = 0):
    if type =='sin':
        output = scale_factor * np.sin(x) + bias
    else:
        output = scale_factor * np.cos(x) + bias
    return output

### making 20 stock flow
Stock_num = 20
Points = 100

stock_dict = {}
for year in range(2010,2019):

    for q in range(4):

        x = np.linspace(0, 40, Points)
        Flow_list =[]
        for i in range(Stock_num):

            tmp_scale = (i % 4) +1
            tmp_bias = i % 3

            if i % 2 == 0:
                tmp_base = make_base_signals(x,type='sin',scale_factor=tmp_scale,bias=3)
            else :
                tmp_base = make_base_signals(x, type='cos', scale_factor=tmp_scale, bias=3)

            signal = tmp_base + noise_func(x,noise_factor= tmp_bias+1)
            Flow_list.append(signal)
            print(i+1,"th flow is done")
        tmp_stock = np.array(Flow_list)
        period = str(year)+'_'+str(q)
        stock_dict[period]=tmp_stock

price = stock0

class Investment:
    # TODO: check architecture
    def __init__(self, period):
        self.period = period  # unit: month

    def select_item(self, factor):
        return

    def rebalance(self, price):
        '''
        update weights of stocks
        :param price: 이전분기 Stock flow weight
        :return: weight of portfolio
        '''
        Port = PortOptim()
        new_w, min_var = Port.get_weight(price)

        return new_w


    def returns_by_quarter(self, price_start, price_end, weight):
        # price_start = stock1[:,0]
        # price_end = stock1[:,-1]
        # weight = new_w
        price_ret = (price_end - price_start)/price_start
        weighted_ret = np.matmul(weight,price_ret)

        '''
        calculation for real return rate((after-before)/before)
        :param price_start: 분기 시작 가격
        :param price_end: 분기 종료 가격
        :param weight: reabalance weight
        :return:
        '''
        return weighted_ret

    def run_invest_simulation(self, y_start, y_end,):

        '''
        running training iteration
        :param y_start: 시작연도
        :param y_end: 종료연도
        :return:
        '''

        for y in range(y_start, y_end):
            # TODO: loop for quarter

        return
