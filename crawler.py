"""_reference_
<financial statements>
https://github.com/FinanceData/OpenDartReader
https://github.com/josw123/dart-fss
https://opendart.fss.or.kr/mng/apiUsageStatusView.do

<price>
https://financedata.github.io/posts/finance-data-reader-users-guide.html
"""

import pandas as pd
import dart_fss as dart

if __name__ == "__main__":
    apikey = "b0085c3bf72a46f361373c8d4b721ee734b4b948"
    # import OpenDartReader
    # dart = OpenDartReader(apikey) 
    # a = dart.finstate_all('005930', 2018)
    # a_ = pd.DataFrame(a)
    # a.to_csv("test_1.csv", index=False)
    
    dart.set_api_key(api_key=apikey)

    # DART 에 공시된 회사 리스트 불러오기
    corp_list = dart.get_corp_list()

    a = dart.corp.CorpList()
    a1 = a.find_by_stock_code("009530")
    b = a.find_by_corp_name('삼성전자', exactly=True)[0]
    c = b.extract_fs(bgn_de='20120101')
    # 삼성전자 검색
    samsung = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]

    # 2012년부터 연간 연결재무제표 불러오기
    fs = samsung.extract_fs(bgn_de='20120101')

    # 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
    fs.save()
        