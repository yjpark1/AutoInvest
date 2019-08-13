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
        self.direction = {"PSR": -1,
                          "PBR": -1,
                          "PER": -1,
                          "PCR": -1,
                          "NCAV": 1,
                          "GPA": 1,
                          "EVEBIT": -1,
                          "PEG": -1,
                          "JOHNPRICE": 1,
                          "DIV": 1,
                          "FSCORE": 1}

    def preprocess(self, scores):
        for col, d in self.direction.items():
            val_replace = scores[col].replace([-np.inf, np.inf], np.nan)

            scores = scores.replace({col: np.nan}, {col: val_replace.mean()})
            scores = scores.replace({col: -np.Infinity}, {col: val_replace.min()})
            scores = scores.replace({col: np.Infinity}, {col: val_replace.max()})

        return scores

    def factor_scale(self, scores):
        x = scores[scores.columns[2:]]
        scale = preprocessing.StandardScaler()
        scores_scaled = scale.fit_transform(x)

        scores_scaled = pd.DataFrame(scores_scaled)
        scores_scaled = scores_scaled.rename(columns={0: "PSR", 1: "PBR", 2: "PER", 3: "PCR", 4: "NCAV", 5: "GPA",
                                                      6: "EVEBIT", 7: "PEG", 8: "JOHNPRICE", 9: "DIV", 10: "FSCORE"})
        scores = pd.concat([scores[scores.columns[0:2]], scores_scaled], axis=1)

        return scores

    def align_derection(self, scores):
        for col, d in self.direction.items():
            scores[col] = d * scores[col]
        return scores

    def factor_aggregation(self, scores):
        scores['sum'] = scores[scores.columns[2:]].sum(axis=1)
        return scores

    def find_candidates(self, scores, top=20):
        return scores.nlargest(top, 'sum')


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
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()
        sales = stock_factor_year[stock_factor_year.Item == 6000901001][year].values.item() * 1000.

        value = price * numstocks / sales
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
    scores = finditem.factor_scale(scores)
    scores = finditem.factor_aggregation(scores)
    scores = finditem.find_candidates(scores, top=20)
