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
        
        <Altman Z score>
        Z = 1.2 x1 + 1.4 x2 + 3.3 x3 + 0.6 x4 + 1.0 x5
        https://en.wikipedia.org/wiki/Altman_Z-score
        http://blog.naver.com/PostView.nhn?blogId=oneidjack&logNo=30038175471&parentCategoryNo=&categoryNo=9&viewDate=&isShowPopularPosts=true&from=search

        <Beneish M score>
        M-Score = −4.84 + 0.92 × DSRI + 0.528 × GMI + 0.404 × AQI + 0.892 × SGI + 0.115 × DEPI −0.172 × SGAI + 4.679 × TATA − 0.327 × LVGI
        http://blog.naver.com/PostView.nhn?blogId=jaeminyx&logNo=221107815370&parentCategoryNo=&categoryNo=&viewDate=&isShowPopularPosts=false&from=postView

    outputs
        filtered factors by beneish & altman scores
    """
    def __init__(self, factor, price, beneish=True, altman=True):
        self.factor = factor
        self.price = price
        self.beneish=beneish
        self.altman = altman
        self.stock_symbols = self.factor[['Symbol', 'Symbol Name']].drop_duplicates()        
        self.beneish_beta = [-4.84, 0.92, 0.528, 0.404, 0.892, 
                             0.115, -0.172, 4.679, -0.327]  # with bias 
        self.altman_beta = [1.2, 1.4, 3.3, 0.6, 1.0]  # without bias

    def filtering(self, year):
        if self.beneish:
            tbl_beneish = self.get_beneish_table(year)
            thresh = tbl_beneish['beneish'].quantile(q=0.05)
            flag_beneish = tbl_beneish['beneish'] > thresh
        else:
            flag_beneish = pd.Series([True for _ in range(len(self.stock_symbols))])

        if self.altman:
            tbl_altman = self.get_altman_table(year)
            thresh = tbl_altman['altman'].quantile(q=0.05)
            flag_altman = tbl_altman['altman'] > thresh
        else:
            flag_altman = pd.Series([True for _ in range(len(self.stock_symbols))])

        flags = flag_beneish.values & flag_altman.values
        return flags

    def get_beneish_table(self, year):
        scores = []
        for i, symbol in enumerate(self.stock_symbols.Symbol):
            score = self.calc_beneish_score_for_stock(symbol, year)
            scores.append(score)
        scores = np.array(scores)
        scores = pd.DataFrame(scores)
        scores_symbol = pd.concat([self.stock_symbols.reset_index(drop=True), scores], axis=1)
        scores_symbol = scores_symbol.rename(columns={0: "beneish"})
        return scores_symbol

    def get_altman_table(self, year):
        scores = []
        for i, symbol in enumerate(self.stock_symbols.Symbol):
            score = self.calc_altman_score_for_stock(symbol, year)
            scores.append(score)
        scores = np.array(scores)
        scores = pd.DataFrame(scores)
        scores_symbol = pd.concat([self.stock_symbols.reset_index(drop=True), scores], axis=1)
        scores_symbol = scores_symbol.rename(columns={0: "altman"})
        return scores_symbol

    def calc_beneish_score_for_stock(self, stock_symbol, year):
        stock_factor = self.factor[self.factor.Symbol == stock_symbol]

        scores = []
        scores.append(1)
        scores.append(self._beneish_DSRI(stock_factor, year))
        scores.append(self._beneish_GMI(stock_factor, year))
        scores.append(self._beneish_AQI(stock_factor, year))
        scores.append(self._beneish_SGI(stock_factor, year))
        scores.append(self._beneish_DEPI(stock_factor, year))
        scores.append(self._beneish_SGAI(stock_factor, year))
        scores.append(self._beneish_TATA(stock_factor, year))
        scores.append(self._beneish_LVGI(stock_factor, year))
        
        out = 0
        for s, b in zip(scores, self.beneish_beta):
            out += (s * b)

        return out

    def calc_altman_score_for_stock(self, stock_symbol, year):
        stock_symbol_name = self.stock_symbols[self.stock_symbols.Symbol == stock_symbol]['Symbol Name'].values[0]
        stock_factor = self.factor[self.factor.Symbol == stock_symbol]

        try:
            stock_price = self.price[['Date', stock_symbol + '_' + stock_symbol_name]]
        except KeyError:
            candidates = [x for x in self.price.columns.values if stock_symbol in x]
            if len(candidates) > 1:
                raise RuntimeError()
            elif len(candidates) == 0:
                return np.nan
            else:
                stock_price = self.price[['Date', candidates[0]]]

        scores = []
        scores.append(self._altman_x1(stock_factor, year))
        scores.append(self._altman_x2(stock_factor, year))
        scores.append(self._altman_x3(stock_factor, year))        
        scores.append(self._altman_x4(stock_factor, stock_price, year))
        scores.append(self._altman_x5(stock_factor, year))
        
        out = 0
        for s, b in zip(scores, self.altman_beta):
            out += (s * b)
        
        return out

    def _beneish_DSRI(self, stock_factor, year):
        Values = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            매출채권 = stock_factor_year[stock_factor_year.Item == 6000901031][year - i].values.item()
            매출 = stock_factor_year[stock_factor_year.Item == 6000904001][year - i].values.item()
            try:
                v = 매출채권 / 매출
            except ZeroDivisionError:
                v = 0
            Values.append(v)

        try:
            out = Values[0] / Values[1]
        except (TypeError, ZeroDivisionError):
            out = 0
        return out

    def _beneish_GMI(self, stock_factor, year):
        Values = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            매출원가 = stock_factor_year[stock_factor_year.Item == 6000905001][year - i].values.item()
            매출 = stock_factor_year[stock_factor_year.Item == 6000904001][year - i].values.item()
            try:
                v = (매출 - 매출원가) / 매출
            except ZeroDivisionError:
                v = 0
            Values.append(v)

        try:
            out = Values[0] / Values[1]
        except (TypeError, ZeroDivisionError):
            out = 0
        return out

        
    def _beneish_AQI(self, stock_factor, year):
        Values = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            유동자산 = stock_factor_year[stock_factor_year.Item == 6000901002][year - i].values.item()
            유형자산 = stock_factor_year[stock_factor_year.Item == 6000901017][year - i].values.item()
            증권 = stock_factor_year[stock_factor_year.Item == 6000901011][year - i].values.item()
            총자산 = stock_factor_year[stock_factor_year.Item == 6000901001][year - i].values.item()
            try:
                v = 1 - ((유동자산 + 유형자산 + 증권) / 총자산)
            except ZeroDivisionError:
                v = 0
            Values.append(v)

        try:
            out = Values[0] / Values[1]
        except (TypeError, ZeroDivisionError):
            out = 0
        return out

    def _beneish_SGI(self, stock_factor, year):
        Values = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            매출 = stock_factor_year[stock_factor_year.Item == 6000904001][year - i].values.item()
            Values.append(매출)

        try:
            out = Values[0] / Values[1]
        except (TypeError, ZeroDivisionError):
            out = 0
        return out

    def _beneish_DEPI(self, stock_factor, year):
        Values = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            감가상각비 = stock_factor_year[stock_factor_year.Item == 6000904025][year - i].values.item()
            유형자산 = stock_factor_year[stock_factor_year.Item == 6000901017][year - i].values.item()
            try:
                v = 감가상각비 / (유형자산 + 감가상각비)
            except ZeroDivisionError:
                v = 0
            Values.append(v)

        try:
            out = Values[0] / Values[1]
        except (TypeError, ZeroDivisionError):
            out = 0
        return out

    def _beneish_SGAI(self, stock_factor, year):
        Values = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            판매관리비 = stock_factor_year[stock_factor_year.Item == 6000904017][year - i].values.item()
            매출 = stock_factor_year[stock_factor_year.Item == 6000904001][year - i].values.item()
            try:
                v = 판매관리비 / 매출
            except ZeroDivisionError:
                v = 0
            Values.append(v)

        try:
            out = Values[0] / Values[1]
        except (TypeError, ZeroDivisionError):
            out = 0
        return out

    def _beneish_LVGI(self, stock_factor, year):
        Values = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            유동부채 = stock_factor_year[stock_factor_year.Item == 6000902003][year - i].values.item()
            비유동부채 = stock_factor_year[stock_factor_year.Item == 6000902011][year - i].values.item()
            총자산 = stock_factor_year[stock_factor_year.Item == 6000901001][year - i].values.item()
            try:
                v = (유동부채 + 비유동부채) / 총자산
            except ZeroDivisionError:
                v = 0
            Values.append(v)

        try:
            out = Values[0] / Values[1]
        except (TypeError, ZeroDivisionError):
            out = 0
        return out

    def _beneish_TATA(self, stock_factor, year):
        Values = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            영업이익 = stock_factor_year[stock_factor_year.Item == 6000906001][year - i].values.item()
            영업현금흐름 = stock_factor_year[stock_factor_year.Item == 6000909001][year - i].values.item()
            총자산 = stock_factor_year[stock_factor_year.Item == 6000901001][year - i].values.item()
            try:
                v = (영업이익 - 영업현금흐름) / 총자산
            except ZeroDivisionError:
                v = 0
            Values.append(v)

        try:
            out = Values[0] / Values[1]
        except (TypeError, ZeroDivisionError):
            out = 0
        return out

    def _altman_x1(self, stock_factor, year):
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        유동자산 = stock_factor_year[stock_factor_year.Item == 6000901002][year].values.item()
        유동부채 = stock_factor_year[stock_factor_year.Item == 6000902003][year].values.item()
        총자산 = stock_factor_year[stock_factor_year.Item == 6000901001][year].values.item()
        out = (유동자산 - 유동부채) / 총자산
        return out

    def _altman_x2(self, stock_factor, year):
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        이익잉여금 = stock_factor_year[stock_factor_year.Item == 6000903016][year].values.item()
        총자산 = stock_factor_year[stock_factor_year.Item == 6000901001][year].values.item()
        out = 이익잉여금 / 총자산
        return out

    def _altman_x3(self, stock_factor, year):
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        영업이익 = stock_factor_year[stock_factor_year.Item == 6000906001][year].values.item()
        총자산 = stock_factor_year[stock_factor_year.Item == 6000901001][year].values.item()
        out = 영업이익 / 총자산
        return out

    def _altman_x4(self, stock_factor, stock_price, year):
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()
        부채총액 = stock_factor_year[stock_factor_year.Item == 6000902001][year].values.item()
        out = price * numstocks / 부채총액
        return out

    def _altman_x5(self, stock_factor, year):
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        매출액 = stock_factor_year[stock_factor_year.Item == 6000904001][year].values.item()
        총자산 = stock_factor_year[stock_factor_year.Item == 6000901001][year].values.item()
        out = 매출액 / 총자산
        return out


if __name__ == "__main__":
    """
    import pickle
    with open("scores.pkl", "wb") as f:
        pickle.dump(scores, f)
    scores = pickle.load(open("scores.pkl", "rb"))
    """
    import pickle
    data = pickle.load(open('data.pkl', 'rb'))
    filterstocks = FilterItem(factor=data['factor'], price=data['price'])
    flag = filterstocks.filtering(year=2012)

    scores = pickle.load(open("scores.pkl", "rb"))
    scores = scores[flag]
    finditem = EqualWeight()
    scores = finditem.align_derection(scores)
    scores = finditem.preprocess(scores)
    scores = finditem.factor_scale(scores)
    scores = finditem.factor_aggregation(scores)
    scores = finditem.find_candidates(scores, top=20)
