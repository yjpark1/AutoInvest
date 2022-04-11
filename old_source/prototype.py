"""
[References]
https://ai-creator.tistory.com/51
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
}

def get_stock_code():
    # 해당 링크는 한국거래소에서 상장법인목록을 엑셀로 다운로드하는 링크입니다.
    # 다운로드와 동시에 Pandas에 excel 파일이 load가 되는 구조입니다.
    stock_code = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
    # stock_code.head()

    # 필요한 것은 "회사명"과 "종목코드" 이므로 필요없는 column들은 제외
    stock_code = stock_code[['회사명', '종목코드', '업종', '주요제품', '상장일', '지역']]

    # 한글 컬럼명을 영어로 변경
    stock_code = stock_code.rename(columns={'회사명': 'company', '종목코드': 'code',
                                            '업종': 'category', '주요제품': 'product',
                                            '상장일': 'date', '지역': 'location'})
    # stock_code.head()

    # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
    stock_code.code = stock_code.code.map('{:06d}'.format)
    return stock_code


def get_last_pagenum_daily_price(code):
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    res = requests.get(url, headers=header)
    soup = bs(res.text, "html.parser")
    elements = soup.select('table.Nnavi>tr>td.pgRR>a')
    urllast = elements[0]['href']
    last_page_num = urllast.split("&page=")[1]
    return last_page_num


def get_daily_price_given_page(code, page):
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    url = '{url}&page={page}'.format(url=url, page=page)
    res = requests.get(url, headers=header)
    df = pd.read_html(res.text, header=0)[0]
    return df


def prerprocessing(df):
    # df.dropna()를 이용해 결측값 있는 행 제거
    df = df.dropna()

    # 한글로 된 컬럼명을 영어로 바꿔줌
    df = df.rename(columns={'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})
    # 데이터의 타입을 int형으로 바꿔줌
    df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)

    # 컬럼명 'date'의 타입을 date로 바꿔줌
    df['date'] = pd.to_datetime(df['date'])

    # 일자(date)를 기준으로 오름차순 정렬
    df = df.sort_values(by=['date'], ascending=True)
    return df


if __name__ == "__main__":
    stock_code = get_stock_code()

    import psycopg2 as pg

    # case 1
    with pg.connect(database="price", user="postgres", password="0682",
                    host='211.221.145.67', port='5432') as connection:
        sql = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname='public';"
        df1 = pd.read_sql(sql, connection)

    # case 2
    with pg.connect(database="price", user="postgres", password="0682",
                    host='211.221.145.67', port='5432') as connection:
        df.to_sql('school', connection, if_exists='replace', index=False)

    # case 3
    with pg.connect(database="price", user="postgres", password="0682",
                    host='211.221.145.67', port='5432') as connection:
        cur = connection.cursor()
        # Create a table at Postgresql public schema with school name
        cur.execute("""
            DROP TABLE IF EXISTS school;
            CREATE TABLE school (
                region varchar(100),
                student_cnt numeric,
                math_score numeric
            )
        """)
        connection.commit()


    from sqlalchemy import create_engine
    # engine = create_engine('postgresql+psycopg2://postgres:0682@211.221.145.67:5432/price')
    engine = create_engine('postgresql://postgres:0682@211.221.145.67:5432/price')
    engine = create_engine('postgresql://postgres:0682@211.221.145.67:5432/price')
    df1 = pd.read_sql_table('school', engine)

    df = get_daily_price_given_page(code='051910', page=1)
    df.to_sql('school', engine, if_exists='replace', index=False)

    df1 = pd.read_sql_table('school', engine)


    # LG화학의 일별 시세 url 가져오기
    company = 'LG화학'
    code = stock_code[stock_code.company == company].code.values[0].strip() ## strip() : 공백제거
    lastpagenum = get_last_pagenum_daily_price(code)

    df = pd.DataFrame()
    for page in range(1, int(lastpagenum)):
        url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
        url = '{url}&page={page}'.format(url=url, page=page)
        print(url)
        df_ = get_daily_price_given_page(code, page)
        df = df.append(df_, ignore_index=True)
        break
    df = prerprocessing(df)
    