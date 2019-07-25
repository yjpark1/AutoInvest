import numpy as np
import pandas as pd
from sklearn import preprocessing


class FindItem:
    def preprocess(self):
        raise NotImplementedError()

    def factor_scale(self):
        raise NotImplementedError()

    def align_derection(self):
        raise NotImplementedError()

    def factor_aggregation(self):
        raise NotImplementedError()

    def find_candidates(self):
        raise NotImplementedError()


class EqualWeight(FindItem):
    def __init__(self):
        super(EqualWeight, self).__init__()
        self.direction = {"PSR": 1,
                          "PBR": 1,
                          "PER": 1,
                          "PCR": 1,
                          "NCAV": 1,
                          "GPA": 1,
                          "EVEBIT": 1,
                          "PEG": 1,
                          "JOHNPRICE": 1,
                          "DIV": 1,
                          "FSCORE": 1}

    def preprocess(self, scores):
        for col, d in self.direction.items():
            scores = scores.replace({col: np.nan}, {col: scores[col].min()})
        return scores

    def factor_scale(self, scores):
        x = scores[scores.columns[2:]]
        scale = preprocessing.StandardScaler()
        scale.fit_transform(x)
        np.isnan(x.values).sum()
        

        return

    def align_derection(self, scores):
        for col, d in self.direction.items():
            scores[col] = d * scores[col]
        return scores

    def factor_aggregation(self):
        return

    def find_candidates(self):
        return


class FilterItem:
    """
    inputs
        factor: factors for a year
        beneish, altman: flags

    outputs
        filtered factors by beneish & altman scores
    """
    def __init__(self, factor, beneish=True, altman=True):
        self.factor = factor
        self.beneish=beneish
        self.altman = altman

    def calc_beneish_score(self):
        return

    def calc_altman_score(self):
        return

    def filtering(self):
        if self.beneish:
            flag_beneish = self._get_flag_beneish()

        if self.altman:
            flag_altman = self._get_flag_altman()

        flags = flag_beneish & flag_altman

        return filtered_factor

    def _beneish_DSRI(self):
        return

    def _beneish_GMI(self):
        return

    def _beneish_AQI(self):
        return

    def _beneish_SGI(self):
        return

    def _beneish_DEPI(self):
        return

    def _beneish_SGAI(self):
        return

    def _beneish_LVGI(self):
        return

    def _beneish_TATA(self):
        return

    def _altman_x1(self):
        return

    def _altman_x2(self):
        return

    def _altman_x3(self):
        return

    def _altman_x4(self):
        return

    def _altman_x5(self):
        return


if __name__ == "__main__":
    """
    import pickle
    with open("scores.pkl", "wb") as f:
        pickle.dump(scores, f)
    scores = pickle.load(open("scores.pkl", "rb"))
    """
    import pickle
    scores = pickle.load(open("scores.pkl", "rb"))

    finditem = EqualWeight()
    scores = finditem.align_derection(scores)
    scores = finditem.preprocess(scores)
