import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine


engine = create_engine('postgresql+psycopg2://postgres:0682@211.221.145.67:5432/price')  # window home
# engine = create_engine('postgresql://yjpark:password@localhost:5432/stocks')  # mac 

dtypes={'Code':str, 'Name':str, 
        'Open':np.int64, 'High':np.int64, 'Low':np.int64, 'Close':np.int64, 
        'Volume':np.int64, 'Amount':np.int64, 'Changes':np.int64, 
        'ChangeCode':str, 'ChagesRatio':np.float64, 'Marcap':np.int64, 
        'Stocks':np.int64, 'MarketId':str, 'Market':str, 'Dept':str,
        'Rank':np.int64}

dir_data = '../marcap/data/'

if __name__ == "__main__":
    for i, p in enumerate(sorted(os.listdir(dir_data))):
        file_path = dir_data + p
        df = pd.read_csv(file_path, dtype=dtypes, parse_dates=['Date'])
        if i == 0:
            df.to_sql('price_kor', engine, if_exists='replace', index=False)
        else:
            df.to_sql('price_kor', engine, if_exists='append', index=False)
        print(p)