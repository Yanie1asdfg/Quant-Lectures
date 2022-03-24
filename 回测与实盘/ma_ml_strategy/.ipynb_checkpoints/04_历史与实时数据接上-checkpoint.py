import pandas as pd
from pandas.core.indexes.base import ensure_index
from sqlalchemy import create_engine
import pymysql
from datetime import datetime,timedelta
import time
import joblib
from CreateFeatures import * 
import copy
# 从数据库读取单个表的数据
def datafmysql(user,password,dbname,table_name):
    connection = pymysql.connect(host='localhost',
                                user=user,
                                password=password,
                                db=dbname,
                                charset='utf8',
                                cursorclass=pymysql.cursors.DictCursor)
    try:
        sql_query = 'SELECT * FROM '+'`'+table_name+'`'
    except:
        return
    # 从mysql中读取表
    df1 = pd.read_sql(sql_query, con=connection)
    return df1
data = datafmysql('root','123456','ml_system','ma2205')
end = data.date.iloc[-1]
# data = data[data.date<datetime(2021,12,21)]

end = data.date.iloc[-1]
# print(end,data)

# 从天勤获取数据
from tqsdk import TqApi, TqAuth,tafunc
api = TqApi(auth=TqAuth("sonnet", "q1234567890"))
klines = api.get_kline_serial("CZCE.MA205", 5*60,data_length=12*8)

while True:
    if datetime.now().second>5:
        continue
    api.wait_update()
    k_data = copy.deepcopy(klines)
    k_data['datetime'] = k_data['datetime'].apply(lambda x:tafunc.time_to_datetime(x)+timedelta(minutes=5))
    k_data = k_data.drop(['id'],axis=1)
    k_data['money'] = 0
    k_data = k_data[['datetime','open','high','low','close','volume','money','close_oi']]
    k_data.columns = ['date','open','high','low','close','volume','money','open_interest']
    # if api.is_changing(klines.iloc[-1], "datetime")
    # if datetime.now().minute/1==0 and datetime.now().second<5:
    # print("最后一根K线收盘价", klines[klines.date>end])
    de = k_data[k_data.date>end]
    df = pd.concat([data,de],axis=0,ignore_index=True)
    # print(df.iloc[-3:,:6])
    end_time = df.date.iloc[-1]
    data_t = df.iloc[:-1,:]
    # 构建因子
    data1 = copy.deepcopy(data_t)
    data1 = feature1(data1,13)
    data1 = feature1(data1,21)
    data1 = feature1(data1,34)
    data1 = feature1(data1,55)
    data1 = feature1(data1,89)
    data1 = feature1(data1,144)
    data1 = feature1(data1,233)

    data1 = feature2(data1)

    data1 = feature3(data1,3)
    data1 = feature3(data1,5)
    data1 = feature3(data1,8)
    data1 = feature3(data1,13)
    data1 = feature3(data1,21)
    data1 = feature3(data1,34)
    data1 = feature3(data1,55)

    data1 = feature4(data1,'date')

    data1 = feature5(data1,8)
    data1 = feature5(data1,13)
    data1 = feature5(data1,21)
    data1 = feature5(data1,34)
    data1 = feature5(data1,55)
    data1 = feature5(data1,89)

    data1 = feature6(data1,8)
    data1 = feature6(data1,13)
    data1 = feature6(data1,21)
    data1 = feature6(data1,34)
    data1 = feature6(data1,55)
    data1 = feature6(data1,89)
    data1 = data1[data1.index>1000]
    data1 = data1.reset_index(drop=True)

    # 截取因子和特征矩阵
    col_list = [x for x in list(data1.columns) if 'feature' in x]
    X = data1[col_list]

    # 找出分类型特征
    classf = [x for x in list(X.columns) if 'feature1' in x or 'feature4' in x]
    # 找出连续型特征
    col = X.columns.tolist()
    for i in classf:
        col.remove(i)
    u = copy.deepcopy(X)
    # 加载无量纲模型
    ss = joblib.load("./ss.pkl")
    u.loc[:,col] = ss.transform(X.loc[:,col])
    # 加载模型
    estimator = joblib.load("./test.pkl")
    # # 预测值
    y_predict = estimator.predict(u)
    if datetime.now().minute%5==0:
        print(datetime.now(),end_time,y_predict[-1])




    

# 取出end
# 然后插入
# 然后计算因子
# 然后数据处理
# 然后带入模型计算