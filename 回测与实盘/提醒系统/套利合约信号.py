

code_list = [("CZCE.MA205","CZCE.MA209"),("CZCE.SA202","CZCE.SA205"),\
            ("CZCE.SA205","CZCE.SA209"),("CZCE.SR203","CZCE.SR205"),\
            ("DCE.c2205","DCE.cs2205") ]
from tqsdk import TqApi, TqAuth,tafunc
from datetime import datetime,timedelta
import time
import copy
import numpy as np
import requests
import json
import pandas as pd

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
api = TqApi(auth=TqAuth("sonnet", "q1234567890"))
code_list0 = [x[0] for x in code_list]
code_list1 = [x[1] for x in code_list]
klines_n = api.get_kline_serial(code_list0,15*60,data_length=2000)
klines_f = api.get_kline_serial(code_list1,15*60,data_length=2000)
while True:
    t = datetime.now()
    if t.minute%5!=0 or t.second>=1 or (t.microsecond>1000): #t.minute%15!=0
        continue
    api.wait_update()
    k_data_n = copy.deepcopy(klines_n)
    k_data_n['datetime'] = k_data_n['datetime'].apply(lambda x:tafunc.time_to_datetime(x)+timedelta(minutes=15))
    k_data_n = k_data_n.dropna()
    
    k_data_f = copy.deepcopy(klines_f)
    k_data_f['datetime'] = k_data_f['datetime'].apply(lambda x:tafunc.time_to_datetime(x)+timedelta(minutes=15))
    k_data_f = k_data_f.dropna()
    print('近月:',code_list0)
    print('远月:',code_list1)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    for i in range(len(code_list0)):
        # open = 'open' + str(i) if i>=1 else 'open'
        # high = 'high' + str(i) if i>=1 else 'high'
        # low = 'low' + str(i) if i>=1 else 'low'
        close = 'close' + str(i) if i>=1 else 'close'
        data = k_data_n[['datetime',close]].copy()
        data1 = k_data_f[['datetime',close]].copy()
        data.columns = ['datetime',code_list0[i]]
        data1.columns = ['datetime',code_list1[i]]
        result = pd.merge(data, data1, on='datetime')
        result['spd'] = result[code_list0[i]]-result[code_list1[i]]
        rsi = RSI(np.array(result.spd),9)
        result['rsi'] = rsi
        print(code_list0[i],code_list1[i],round(rsi[-3],2),round(rsi[-2],2),round(rsi[-1],2))
        if t.minute%5!=0:
            continue
        if rsi[-2]<20 and rsi[-1]>20:
            reminders=[]
            msg = '>'+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+'\n'+\
                code_list0[i]+' '+code_list1[i]+' '+'↑'*3+'20'
            send_msg(reminders, msg)
            print(msg)
        elif rsi[-2]>80 and rsi[-1]<80:
            reminders=[]
            msg = '>'+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+'\n'+\
                code_list0[i]+' '+code_list1[i]+' '+'↓'*3+'80'
            send_msg(reminders, msg)
            print(msg)
        elif rsi[-2]<50 and rsi[-1]>50:
            reminders=[]
            msg = '>'+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+'\n'+\
                code_list0[i]+' '+code_list1[i]+' '+'↑'*3+'50'
            send_msg(reminders, msg)
            print(msg)
        elif rsi[-2]>50 and rsi[-1]<50:
            reminders=[]
            msg = '>'+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+'\n'+\
                code_list0[i]+' '+code_list1[i]+' '+'↓'*3+'50'
            send_msg(reminders, msg)
            print(msg)
    