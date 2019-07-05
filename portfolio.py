import scipy.optimize as sco
import numpy as np


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
        return

    def _get_wgt_equal(self, price):
        return

    def _get_wgt_mdp(self, price):
        return
