import scipy.optimize as sco
import numpy as np
import pandas as pd

def calc_return_rate(stock_price):
    return np.diff(stock_price) / stock_price[:, :-1]

def calculate_GMV(w,V):
    w = np.matrix(w)
    return (w*V*w.T)[0,0]

class PortOptim:
    def __init__(self, method):
        self.method = method

    def get_weight(self, price):
        weight = None
        if self.method == 'gmv':
            weight = self._get_wgt_gmv(price)
        elif self.method == 'equal':
            weight = self._get_wgt_equal(price)
        elif self.method == 'mdp':
            weight = self._get_wgt_mdp(price)
        else:
            raise NotImplementedError()

        return weight

    def _get_wgt_gmv(self, price):
        '''
        ref1 : http://showcase.imw.tuwien.ac.at/BWOpt/PF1_minvar.html
        ref2 : https://thefinancialintern.wordpress.com/2012/07/17/modern-portfolio-theory-developing-a-global-minimum-variance-portfolio-gmv-in-excel/
        '''
        stock = price
        stockR = calc_return_rate(stock)

        V_stockR = np.cov(stockR)
        M_stockR = np.mean(stockR, axis=1)

        number_stock = stock.shape[0]
        w0 = np.ones(number_stock) / number_stock

        # unconstrained portfolio (only sum(w) = 1 )
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
        bnds = tuple([(0, 1) for i in range(number_stock)])

        res = sco.minimize(calculate_GMV, w0, args=V_stockR,
                           method='SLSQP', constraints=cons, bounds=bnds)
        w_sol = res.x
        Mean_stock = w_sol * M_stockR
        Var_stock = res.fun

        return w_sol

    # def _get_wgt_gmv(self, price):
    #     return

    def _get_wgt_equal(self, price):
        return

    def _get_wgt_mdp(self, price):
        return



tmp_port = PortOptim('gmv')
tmp_port.get_weight(stock)



