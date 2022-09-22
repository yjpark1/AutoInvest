"""
https://github.com/sharebook-kr/pykrx
"""
from pykrx import stock

df1 = stock.get_market_fundamental("20210108")
df1.head()


df1 = stock.get_market_fundamental("20210104", "20210108", "005930") 
df1.head()