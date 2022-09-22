"""
https://bigdata-doctrine.tistory.com/3
"""
import datetime
import os
import time

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

url_base = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok='

KOSPI_CODE = 0
KOSDAK_CODE = 1
START_PAGE = 1

fields = ['quant', 'ask_buy', 'amount', 'market_sum', 'operating_profit', 
            'per', 'open_val', 'ask_sell', 'prev_quant', 'property_total', 
            'operating_profit_increasing_rate', 'roe', 'high_val', 
            'buy_total', 'frgn_rate', 'debt_total', 'net_income', 'roa', 
            'low_val', 'sell_total', 'listed_stock_cnt', 'sales', 'eps', 
            'pbr', 'sales_increasing_rate', 'dividend', 'reserve_ratio']

useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"


def crawl(code: str, page: str):
    time.sleep(1.5)
    try:
        url = f"{url_base}{code}&page={page}"
        data = {'menu': 'market_sum',
                'fieldIds':  fields,
                'returnUrl': url}
        
        res = requests.post('https://finance.naver.com/sise/field_submit.nhn', 
                            data = data,
                            headers={'User-agent': useragent})
        # page_soup = BeautifulSoup(res.text, 'lxml')
        # table_html = page_soup.select_one('div.box_type_l').select_one('table')
        df = pd.read_html(res.text)
        df = df[1]
        df = df.dropna(axis=0, how='all')
        df = _preprocess(df)
        return df
    except Exception as e:
        print(e)
        return None


def _preprocess(df: pd.DataFrame):
    df.drop(columns=['토론실'], inplace=True)
    df['배당률'] = 100 * df['보통주배당금'] / df['현재가']
    return df

def main(code):
    if not os.path.exists('tmp'):
        os.makedirs('tmp', exist_ok=False)
    
    today = datetime.datetime.today()
    filename = f'tmp/tmp_{today.year}{today.month:02d}{today.day:02d}.xlsx'
    
    if not os.path.exists(filename):
        res = requests.get(f"{url_base}{str(code)}&page={str(START_PAGE)}", 
                        headers={'User-agent':'Mozilla/5.0'})
        page_soup = BeautifulSoup(res.text, "lxml")
        
        # #가져올 수 있는 항목명들을 추출
        # ipt_html = page_soup.select_one('div.subcnt_sise_item_top')
        # global fields
        # fields = [item.get('value') for item in ipt_html.select('input')]
        
        total_page_num = page_soup.select_one('td.pgRR > a')
        total_page_num = int(total_page_num.get('href').split('=')[-1])
        
        result = []
        total_page_num = 2
        for page in range(START_PAGE, total_page_num + 1):
            dt = crawl(code, str(page))
            if dt is not None:
                result.append(dt)
        
        df = pd.concat(result, axis=0, ignore_index=True)
        df.to_excel(filename, sheet_name='result', index=False)
    else:
        print(f"The file already exists: {filename}")
        df = pd.read_excel(filename, sheet_name='result')
    # final output
    df = df[['N', '종목명', '현재가', '거래량', '매수총잔량', 
             '매도총잔량', '보통주배당금', 'PER', 'PBR', '배당률']]
    df['배당률'] = df['배당률'].round(2)
    df = df.astype({'N': 'int32'})
    df.to_excel("results.xlsx", index=False)
    
if __name__ == "__main__":
    main(KOSPI_CODE)
    

