import time
import akshare as ak
from datetime import datetime
import pandas as pd
s1 = ""
t1 = []
df = pd.DataFrame()
while True:
    data = ak.futures_zh_spot(
            subscribe_list="RB2110",
            market="CF",   # market="CF"; market="CF": 商品期货, market="FF": 金融期货
            adjust=False)  #adjust=False; adjust=True: 返回合约、交易所和最小变动单位的实时数据, 返回数据会变慢

    date = datetime.now().date().strftime("%Y%m%d")
    time = data.iloc[-1].to_dict()['time']
    time = datetime.strptime(str(date)+time,'%Y%m%d%H%M%S')
    current_price = data.iloc[-1].to_dict()['current_price']#[['symbol','time','open','high','low','current_price']]
    print(time,current_price)
    # if df.empty==False:
    #     if df.iloc[-1].to_dict()['price']!=current_price:
    #         df = df.append({'date':time,'price':current_price},ignore_index=True)
    #         print(df)
    # else:
    #     df = df.append({'date':time,'price':current_price},ignore_index=True)
    #     print(df)


