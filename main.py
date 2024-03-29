import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from matplotlib import pyplot as plt
import mplfinance as mpf
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
from scipy import stats


engine = create_engine('postgresql+psycopg2://postgres:0682@211.221.145.67:5432/price')  # winhome
# engine = create_engine('postgresql://yjpark:password@localhost:5432/stocks')  # mac

dtypes = {'Code': str, 'Name': str,
          'Open': np.int64, 'High': np.int64, 'Low': np.int64, 'Close': np.int64,
          'Volume': np.int64, 'Amount': np.int64, 'Changes': np.int64,
          'ChangeCode': str, 'ChagesRatio': np.float64, 'Marcap': np.int64,
          'Stocks': np.int64, 'MarketId': str, 'Market': str, 'Dept': str,
          'Rank': np.int64}


def query_get_code(code: str, date_from: str = None, date_to: str = None) -> str:
    query_format = f'''
    SELECT * FROM price_kor 
    WHERE "Code"=\'{code}\''''
    if date_from is not None:
        query_format += f"and \"Date\" >= '{date_from}'"
    if date_to is not None:
        query_format += f"and \"Date\" < '{date_to}'"
    query_format += ";"
    print(query_format)
    return query_format


def get_data_from_query(q: str):
    d = pd.read_sql(q, engine)
    d = d.set_index('Date', drop=False)
    print(d.head())
    return d


def plot_candle(ax, prices):
    prices_ = prices[['Date', 'Open', 'High', 'Low', 'Close']]
    prices_['Date'] = prices_['Date'].map(mdates.date2num)
    candlestick_ohlc(ax, prices_.values, width=0.6,
                     colorup='red', colordown='blue')
    # allow grid
    ax.grid(True)
    # Setting labels
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    # Formatting Date
    date_format = mdates.DateFormatter('%d-%m-%Y')
    ax.xaxis.set_major_formatter(date_format)
    return ax


def test_normality(x):
    test = stats.shapiro(x)
    print("null hypothesis that the data was drawn from a normal distribution.")
    print("p-value:", test.pvalue)
    return test


def ttest_lastprice(x):
    test = stats.ttest_1samp(x, x[-1], alternative='greater')
    print("null hypothesis that the expected value (mean) of a sample of independent observations a is greater thean the given population mean.")
    print("p-value:", test.pvalue)
    return test


def plot_stock_daily_price(prices: pd.DataFrame):
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5),
                             gridspec_kw={'width_ratios': [2, 1]},
                             tight_layout=True)
    axes[0] = plot_candle(axes[0], prices)
    fig.autofmt_xdate()
    axes[1].hist(prices['Close'])
    axes[1].axvline(x=prices['Close'][-1], color='tab:red', ls='--')
    plt.show()
    plt.close()


def get_evaluate_all_stocks(date_from: str):
    q = f"""
    SELECT DISTINCT("Code") FROM price_kor
    WHERE "Date" >= '{date_from}';
    """
    code = pd.read_sql(q, engine)
    
    eval_results = []
    for i, c in code.iterrows():
        code = c['Code']
        q = query_get_code(code, date_from)
        prices = get_data_from_query(q)
        # test
        try:
            test_shapiro = test_normality(prices['Close'])
            test_ttest = ttest_lastprice(prices['Close'])
        except ValueError as e:
            print(e)
        else:
            # append
            record = {
                'code': code,
                'name': prices['Name'][0],
                'percentile': (prices['Close'] <= prices['Close'][-1]).mean(),
                'ttest': test_ttest.pvalue,
                'shapiro': test_shapiro.pvalue,
            }
            eval_results.append(record)
    re = pd.DataFrame().from_records(eval_results)
    return re
    

if __name__ == "__main__":
    from scipy import stats
    """
    q = query_get_code(code='005930', date_from='2021-01-01',
                       date_to='2021-01-30')
    prices = get_data_from_query(q)
    plot_stock_daily_price(prices)
    """
    date_from = '2019-01-01'
    re = get_evaluate_all_stocks(date_from)
    re.to_csv('test.csv', index=False, encoding='euc-kr')
    

    
    
