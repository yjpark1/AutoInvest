'''
<Definition of scores>
https://drive.google.com/file/d/1bzvdNNCqHSb6L-LZsB1zzl9qulXENUJX/view?usp=sharing
'''

import numpy as np
import pandas as pd


class StockScore:
    def __init__(self, factor, price):
        self.factor = factor
        self.price = price

    def make_score_table(self, year):
        stock_symbols = self.factor[['Symbol', 'Symbol Name']].drop_duplicates()

        scores = []
        for symbol in stock_symbols.Symbol:
            score = self.score_for_stock(symbol, year)
            scores.append(score)
        scores = np.array(scores)
        scores = pd.DataFrame(scores)
        scores_symbol = pd.concat([stock_symbols.reset_index(drop=True), scores], axis=1)
        scores_symbol.head()
        scores.rename(columns={0: "PSR", 1: "PBR", 2: "PER", 3: "PCR", 4: "NCAV", 5: "GPA",
                               6: "EVEBIT", 7: "PEG", 8: "JOHNPRICE", 9: "DIV", 10: "FSCORE"})

        return scores

    def score_for_stock(self, stock_symbol, year):
        stock_symbol_name = self.factor[self.factor.Symbol == stock_symbol]['Symbol Name'][0]
        stock_factor = self.factor[self.factor.Symbol == stock_symbol]
        stock_price = self.price[['Date', stock_symbol+'_'+stock_symbol_name]]

        scores = []
        scores.append(self._calc_factor_psr(stock_factor, stock_price, year))
        scores.append(self._calc_factor_pbr(stock_factor, stock_price, year))
        scores.append(self._calc_factor_per(stock_factor, stock_price, year))
        scores.append(self._calc_factor_pcr(stock_factor, stock_price, year))
        scores.append(self._calc_factor_ncav(stock_factor, stock_price, year))
        scores.append(self._calc_factor_gpa(stock_factor, stock_price, year))
        scores.append(self._calc_factor_peg(stock_factor, stock_price, year))
        scores.append(self._calc_factor_johnprice(stock_factor, stock_price, year))
        scores.append(self._calc_factor_div(stock_factor, stock_price, year))
        scores.append(self._quality_factor(stock_factor, year))

        scores = np.array(scores)

        return scores

    def _calc_factor_psr(self, stock_factor, stock_price, year):
        """
        1. PSR(주가 매출액배수)=시가총액(주가*수정발행주식수)/매출액[6000901001]
            -> 해석: 낮을수록 회사 규모에 비해 주가가 싸다.
            Ref) Kenneth Fisher, Super Stock, 1984
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()
        sales = stock_factor_year[stock_factor_year.Item == 6000901001][year].values.item() * 1000.

        value = price * numstocks / sales
        return value

    def _calc_factor_pbr(self, stock_factor, stock_price, year):
        """
        2. PBR(주가 순자산배수)=시가총액(주가*수정발생주식수)/자기자본(부채 및 자본총계[6000903030] - 총부채[6000902001])
            -> 해석: 낮을수록 회사 자본에 비해 주가가 싸다
            Ref) Fama, french, The cross-section Expected stock return , 1992
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()
        liabilities_and_capital = stock_factor_year[stock_factor_year.Item == 6000903030][year].values.item() * 1000.
        indebtedness = stock_factor_year[stock_factor_year.Item == 6000902001][year].values.item() * 1000.

        value = price * numstocks / (liabilities_and_capital - indebtedness)

        return value
    
    def _calc_factor_per(self, stock_factor, stock_price, year):
        """
        3. PER(주가 순이익 배수)= 시가총액(주가*수정발생주식수)/당기 순이익[6000908001]
            -> 해석: 낮을수록 회사 순이익에 비해 주가가 싸게 거래 된다.
            Ref) S. jeremy, Stocks for the long run, McGraw-Hill, 장기투자바이블
            2007,2008
            Josef Lakonishock외, Contraian Investment, Extrapolation and Risk, 1994
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()
        netprofit = stock_factor_year[stock_factor_year.Item == 6000908001][year].values.item() * 1000.

        value = price * numstocks / netprofit

        return value
    
    def _calc_factor_pcr(self, stock_factor, stock_price, year):
        """
        4. PCR(주가 현금 흐름배수)= 시가총액(주가*수정발생주식수)/영업활동 현금흐름[6000909001]
            -> 해석: 낮으면 영업활동을 통한 현금 흐름 보다 주가가 싸게 거래 된다.
            Ref) Josef Lakonishock외, Contraian Investment, Extrapolation and Risk, 1994
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()
        cashflow = stock_factor_year[stock_factor_year.Item == 6000909001][year].values.item() * 1000.

        value = price * numstocks / cashflow

        return value
    
    def _calc_factor_ncav(self, stock_factor, stock_price, year):
        """
        5. NCAV (Net Current Asset Value)= (유동자산[6000901002]-총부채[6000902001])/시가총액(주가*수정발생주식수)
            -> 해석: 현재의 현금을 가지로 총 부채를 상환하더라도 현재 시가 총액보다 비싸다.
            Ref) Benjamin Graham, Security analysis
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()
        currentassets = stock_factor_year[stock_factor_year.Item == 6000901002][year].values.item() * 1000.
        indebtedness = stock_factor_year[stock_factor_year.Item == 6000902001][year].values.item() * 1000.

        value = (currentassets - indebtedness) / (price * numstocks)

        return value
    
    def _calc_factor_gpa(self, stock_factor, stock_price, year):
        """
        6. 시가총액/ 매출 총이익률= 시가총액/(GP(매출액-매출원가)/A(총자산))GP/A / 시가총액
            = 시가총액(주가*수정발생주식수)/ (매출액[6000904001]-매출원가[6000905001])
            -> 해석: 매출원가이익률이 높은 회사(즉, 원가대비 이익률이 좋은 회사)가 싸게거래된다.
            Ref) Robert Novy-Marx, The other side od value: the gross profit ablity premium, 2013
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()
        sales = stock_factor_year[stock_factor_year.Item == 6000904001][year].values.item() * 1000.
        salescost = stock_factor_year[stock_factor_year.Item == 6000905001][year].values.item() * 1000.

        value = price * numstocks / (sales - salescost)

        return value
    
    def _calc_factor_evebit(self, stock_factor, stock_price, year):
        """
        7. EV/EBIT= EV(시가총액(주가*수정발생주식수))+ 부채[6000902001]-현금 및 현금성 자산[6000901030]- 비영업자산[6000901010 + 6000901034 +
            6000901009 + 6000901033+6000991006+6000901014+6000901037+6000901054 + 6000991007+6000901040+6000991010 )/EBITDA(영업이익
            [6000906001]+감가상각비[6000904023])
            ->해석: 감가 상각비를 포함한 순 영업이익으로 전체 회사를 인수 했을 때 몇 년 만에 회수가 가능한가? (즉, 원금 대비 회수 년수)
            Ref) Joel Greenblatt, 주식시장을 이기는 작은 책
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()

        x1 = stock_factor_year[stock_factor_year.Item == 6000902001][year].values.item() * 1000.
        x2 = stock_factor_year[stock_factor_year.Item == 6000901030][year].values.item() * 1000.
        x3 = stock_factor_year[stock_factor_year.Item == 6000901010][year].values.item() * 1000.
        x4 = stock_factor_year[stock_factor_year.Item == 6000901034][year].values.item() * 1000.
        x5 = stock_factor_year[stock_factor_year.Item == 6000901009][year].values.item() * 1000.
        x6 = stock_factor_year[stock_factor_year.Item == 6000901033][year].values.item() * 1000.
        x7 = stock_factor_year[stock_factor_year.Item == 6000991006][year].values.item() * 1000.
        x8 = stock_factor_year[stock_factor_year.Item == 6000901014][year].values.item() * 1000.
        x9 = stock_factor_year[stock_factor_year.Item == 6000901037][year].values.item() * 1000.
        x10 = stock_factor_year[stock_factor_year.Item == 6000901054][year].values.item() * 1000.
        x11 = stock_factor_year[stock_factor_year.Item == 6000991007][year].values.item() * 1000.
        x12 = stock_factor_year[stock_factor_year.Item == 6000901040][year].values.item() * 1000.
        x13 = stock_factor_year[stock_factor_year.Item == 6000991010][year].values.item() * 1000.
        x14 = stock_factor_year[stock_factor_year.Item == 6000906001][year].values.item() * 1000.
        x15 = stock_factor_year[stock_factor_year.Item == 6000904023][year].values.item() * 1000.

        EV = (price * numstocks) + x1 - x2 - (x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13)
        EBIT = x14 + x15
        value = EV / EBIT

        return value
    
    def _calc_factor_peg(self, stock_factor, stock_price, year):
        """
        8. PEG =PER/G(groth rate, 직전 5년간 기하 평균 BPS증가률[6000208027; 단 5년 평균기하 수익률로 환산 필요]
            Ref)피터린치, 위대한 기업에 투자하라
        """
        per = self._calc_factor_per(stock_factor, stock_price, year)

        g_geometric = 1.
        for i in range(5):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            g = stock_factor_year[stock_factor_year.Item == 6000208027][year - i].values.item()
            try:
                g_geometric *= (1 + (g * 0.01))
            except TypeError:
                break
        g_geometric = g_geometric ** (1/(i+1))

        value = per / g_geometric

        return value
        
    def _calc_factor_johnprice(self, stock_factor, stock_price, year):
        """
        9. 주가대비 non- growth assumed intrinsic value 괴리율 = ROE(6000312001)/PBR
            Ref) 존프라이스, 워렌버핏처럼 가치 평가 활용하는 법
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]

        pbr = self._calc_factor_pbr(stock_factor, stock_price, year)
        roe = stock_factor_year[stock_factor_year.Item == 6000312001][year].values.item()

        value = roe / pbr

        return value
            
    def _calc_factor_div(self, stock_factor, stock_price, year):
        """
        10. 배당률= 배당급 지급[6000909041]/시가총액(주가*수정발생주식수)
            : 배당급 지급은 외부로 돈이 빠져 나간 것이므로 재무재표에서 (-)로 표시됩니다. 이것을 (+)형태로 바꿔야 됩니다.
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        stock_price_year = stock_price[stock_price.Date == '{}-12-31'.format(year)]

        price = stock_price_year.iloc[0, 1]
        numstocks = stock_factor_year[stock_factor_year.Item == 'S430002205'][year].values.item()
        div = stock_factor_year[stock_factor_year.Item == 6000909041][year].values.item() * -1000.

        value = div / (price * numstocks)

        return value

    def _quality_factor(self, stock_factor, year):
        """
        Quality Factor.
        피오트로스키 F score factor.
            각 회사의 재무제표에 각 항목이 있으면 1점, 없으면 0점(총 0~9점 까지)
            매년 마다 이 F-factor를 군집하여, 0점 군부터 ~ 9점 군 까지의 10개군을 수익률(Return)과 통계처리
            Ref) Joseph pitroski, Value investing: the use of historical finacial statement
                information to separate winners from loseres, 2000
        """
        fscore = 0
        fscore += self._quality_factor_1(stock_factor, year)
        fscore += self._quality_factor_2(stock_factor, year)
        fscore += self._quality_factor_3(stock_factor, year)
        fscore += self._quality_factor_4(stock_factor, year)
        fscore += self._quality_factor_5(stock_factor, year)
        fscore += self._quality_factor_6(stock_factor, year)
        fscore += self._quality_factor_7(stock_factor, year)
        fscore += self._quality_factor_8(stock_factor, year)
        fscore += self._quality_factor_9(stock_factor, year)

        return fscore

    def _quality_factor_1(self, stock_factor, year):
        """
        1. 당기순이익[6000908001]: 0 이상
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        netprofit = stock_factor_year[stock_factor_year.Item == 6000908001][year].values.item()

        if netprofit > 0:
            value = 1.
        else:
            value = 0.

        return value

    def _quality_factor_2(self, stock_factor, year):
        """
        2. 영업현금흐름[6000909001]: 0 이상
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        salescashflow = stock_factor_year[stock_factor_year.Item == 6000909001][year].values.item()

        if salescashflow > 0:
            value = 1.
        else:
            value = 0.

        return value

    def _quality_factor_3(self, stock_factor, year):
        """
        3. ROA[6000306001] : 전년대비(t-1) 증가
        """
        ROAs = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            roa = stock_factor_year[stock_factor_year.Item == 6000306001][year-i].values.item()
            ROAs.append(roa)

        if ROAs[0] > ROAs[1]:
            value = 1.
        else:
            value = 0.

        return value

    def _quality_factor_4(self, stock_factor, year):
        """
        4. 전년 영업 현금 흐름 : 순이익[6000908001] 보다 높음
        """
        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - 1]]
        cashflow = stock_factor_year[stock_factor_year.Item == 6000909001][year-1].values.item()

        stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year]]
        netprofit = stock_factor_year[stock_factor_year.Item == 6000908001][year].values.item()

        if cashflow > netprofit:
            value = 1.
        else:
            value = 0.

        return value

    def _quality_factor_5(self, stock_factor, year):
        """
        5. 부채 비율[6000102001]: 전년 대비 감소
        """
        debt_ratios = []
        for i in range(2):
            stock_factor_year = stock_factor[
                ['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            debt_ratio = stock_factor_year[stock_factor_year.Item == 6000102001][year - i].values.item()
            debt_ratios.append(debt_ratio)

        if debt_ratios[0] > debt_ratios[1]:
            value = 1.
        else:
            value = 0.

        return value

    def _quality_factor_6(self, stock_factor, year):
        """
        6. 유동 비율(유동자산/유동부채 *100(%)= [6000901002]/[6000902003]*100): 전년 대비 증가
        """
        liquid_ratios = []
        for i in range(2):
            stock_factor_year = stock_factor[
                ['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year - i]]
            liquid_asset = stock_factor_year[stock_factor_year.Item == 6000901002][year - i].values.item()
            liquid_debt = stock_factor_year[stock_factor_year.Item == 6000902003][year - i].values.item()
            liquid_ratio = liquid_asset / liquid_debt
            liquid_ratios.append(liquid_ratio)

        if liquid_ratios[0] > liquid_ratios[1]:
            value = 1.
        else:
            value = 0.

        return value

    def _quality_factor_7(self, stock_factor, year):
        """
        7. 신규 주식 발행(유상증자 포함):없음
        """
        num_stocks = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year-i]]
            num_stock = stock_factor_year[stock_factor_year.Item == 'S430002205'][year - i].values.item()
            num_stocks.append(num_stock)

        if num_stocks[0] == num_stocks[1]:
            value = 1.
        else:
            value = 0.

        return value

    def _quality_factor_8(self, stock_factor, year):
        """
        8. 매출총이익률(매출 총이익/ 매출액)[6000904007/6000901001]: 전년대비 증가
        """
        Ratios = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year-i]]
            gross_profit = stock_factor_year[stock_factor_year.Item == 6000904007][year - i].values.item()
            sales = stock_factor_year[stock_factor_year.Item == 6000901001][year - i].values.item()
            ratio = gross_profit / sales
            Ratios.append(ratio)

        if Ratios[0] > Ratios[1]:
            value = 1.
        else:
            value = 0.

        return value

    def _quality_factor_9(self, stock_factor, year):
        """
        9. 자산 회전율(매출/자산)[6000401001]: 전년대비 증가
        """
        asset_trunovers = []
        for i in range(2):
            stock_factor_year = stock_factor[['Symbol', 'Symbol Name', 'Kind', 'Item', 'Item Name', 'Frequency', year-i]]
            asset_trunover = stock_factor_year[stock_factor_year.Item == 6000401001][year - i].values.item()
            asset_trunovers.append(asset_trunover)

        if asset_trunovers[0] > asset_trunovers[1]:
            value = 1.
        else:
            value = 0.

        return value


if __name__ == '__main__':
    from database import DataBase
    db = DataBase(type='both')
    db.load_database_full()
    # db.factor = db.factor_kospi.append(db.factor_kosdaq)
    data = db.get_database_full()
    db.unload_database()  # check out DataBase class

    score = StockScore(factor=data['factor'], price=data['price'])
    score.make_score_table(year=2001)

