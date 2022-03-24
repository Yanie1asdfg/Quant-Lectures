'''
1.获取tq数据
'''

code_list = ["CZCE.MA205","CZCE.MA209","SHFE.ag2206",\
             "DCE.c2205","DCE.cs2203","DCE.jd2205",\
             "CZCE.SR205","CZCE.RM205","DCE.m2205"]
# 
# 从天勤获取数据
from tqsdk import TqApi, TqAuth,tafunc
from datetime import datetime,timedelta
import time
import copy
import numpy as np
import requests
import json
api = TqApi(auth=TqAuth("sonnet", "q1234567890"))
klines = api.get_kline_serial(code_list,15*60,data_length=2000)
def to_60min(df_15min):

    """
    将1分钟数据转为60min数据
    """
    # 1.转换为30min数据
    # df30 = df_1min.resample('30min',closed='right',label='right').agg({'open':'first',\
    #                         'high':'max',\
    #                         'low':'min',\
    #                         'close':'last',\
    #                         'volume':'sum',\
    #                         'money':'sum'}).dropna()
    # if df_15min.shape[0]%2!=0:
        # raise Exception("wrong lenth")
    # 使用groupby构造60min K线
    idx = list(range(0,len(df_15min)//4+1))*4
    idx.sort()
    idx = idx[:len(df_15min)]
    idx.reverse()
    # print(idx,len(idx))
    df_15min['idx'] = idx
    
    # df30 = df_15min.reset_index()
    df60 = df_15min.groupby(by='idx').agg({'datetime':'last',\
                            'open':'first',\
                            'high':'max',\
                            'low':'min',\
                            'close':'last'})
    # df60.set_index('index',inplace=True)
    # df60 = df60[['open','high','low','close','volume','money']]
    return df60
def RSI(price, periods):
    rsi = []
    up_avg = 0.0
    down_avg = 0.0
    for i in range(periods):
        if i > 0:
            if price[i] >= price[i - 1]:
                up_avg += price[i] - price[i - 1]
            else:
                down_avg += price[i - 1] - price[i]
        rsi.append(-1)
    
    up_avg = up_avg / periods
    down_avg = down_avg / periods
    rs = up_avg / down_avg
    rsi[periods - 1] = 100 - 100 / (1 + rs)
    
    for i in range(periods, len(price)):
        up = 0.0
        down = 0.0
        if price[i] >= price[i - 1]:
            up = price[i] - price[i - 1]
            down = 0.0
        else:
            up = 0.0
            down = price[i - 1] - price[i]
        
        up_avg = (up_avg * (periods - 1) + up) / periods
        down_avg = (down_avg * (periods - 1) + down) / periods
        rs = up_avg / down_avg
        rsi.append(100 - 100 / (1 + rs))
    
    return rsi
def send_msg(reminders, msg):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=532b4c7e3712ddff1c0f6883b3704e6deba53ae2733f7618e04f3823cb3097f0'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "text", # 发送消息类型为文本
        "at": {
                "atMobiles": reminders,
                "isAtAll": False,                  # 不@所有人，如果要@所有人写True并且将上面atMobiles注释掉
                },
        "text": {
                "content": msg, # 消息正文
                }
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r.text
while True:
    t = datetime.now()
    if t.second>=1 or (t.microsecond>1000): #t.minute%15!=0
        continue
    print(datetime.now())
    api.wait_update()
    
    k_data = copy.deepcopy(klines)
    k_data['datetime'] = k_data['datetime'].apply(lambda x:tafunc.time_to_datetime(x)+timedelta(minutes=15))
    k_data = k_data.dropna()
    
    
    for i in range(len(code_list)):
        open = 'open' + str(i) if i>=1 else 'open'
        high = 'high' + str(i) if i>=1 else 'high'
        low = 'low' + str(i) if i>=1 else 'low'
        close = 'close' + str(i) if i>=1 else 'close'
        # print(code_list[i])
        data = k_data[['datetime',open,high,low,close]].copy()
        data.columns = ['datetime','open','high','low','close']
        # data = to_60min(data)
        rsi = RSI(np.array(data.close),9)
        print(code_list[i],round(rsi[-3],2),round(rsi[-2],2),round(rsi[-1],2))
        # print(data.iloc[-3:])
        if t.minute%15!=0:
            continue
        if rsi[-2]<20 and rsi[-1]>20:
            reminders=[]
            msg = '>'+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+'\n'+code_list[i]+' '+'↑'*3
            send_msg(reminders, msg)
            print(msg)
        elif rsi[-2]>80 and rsi[-1]<80:
            reminders=[]
            msg = '>'+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+'\n'+code_list[i]+' '+'↓'*3
            send_msg(reminders, msg)
            print(msg)
        
    # time.sleep(20)