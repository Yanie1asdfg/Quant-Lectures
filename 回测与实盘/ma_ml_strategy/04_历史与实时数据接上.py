import pandas as pd
from pandas.core.indexes.base import ensure_index
from sqlalchemy import create_engine
import pymysql
from datetime import datetime,timedelta
import time
import joblib
from CreateFeatures import * 
import copy
from Dyp import *

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

# 获取参数数据
import json
with open("MA_PARAM.json",'r') as load_f:
    load_dict = json.load(load_f)

training_end_time = load_dict['training_end_time']
late_n_profit = load_dict['late_n_profit']
cut_point = load_dict['cut_point']
ss_path = load_dict["pre_processing_path"]
model_path = load_dict["model_path"]
print(load_dict)

# 从天勤获取数据
from tqsdk import TqApi, TqAuth,tafunc
api = TqApi(auth=TqAuth("sonnet", "q1234567890"))
klines = api.get_kline_serial("CZCE.MA205", 5*60,data_length=10000)
k = 0
while True:
    # api.wait_update()

    # 整理数据
    k_data = copy.deepcopy(klines)
    # 时间转换为右标注
    k_data['datetime'] = k_data['datetime'].apply(lambda x:tafunc.time_to_datetime(x)+timedelta(minutes=5))
    k_data = k_data.drop(['id'],axis=1)
    k_data['money'] = 0.0
    k_data = k_data[['datetime','open','high','low','close','volume','money','close_oi']]
    k_data.columns = ['date','open','high','low','close','volume','money','open_interest']
    # k_data['date_t'] = k_data['date'].apply(lambda x: x.date())
    # print(len(k_data['date_t'].unique()),'\n',k_data.info(),k_data)
    
    data = k_data.copy()

    # 过滤时间
    data = data[data.date>training_end_time]
    

    # 实盘中不需要计算收益label，但是后期需要画曲线，这时候就是需要的
    # 计算收益
    data['close_shift_n'] = data['close'].shift(-late_n_profit)
    data['return'] = data['close_shift_n']-data['close']
    data.loc[:,'label'] = 0
    data.loc[data['return']>=cut_point,'label'] = 1
    data.loc[data['return']<=-cut_point,'label'] = -1

    # 构建因子
    
    data1 = copy.deepcopy(data)
    
    data1 = feature1(data1,13)
    data1 = feature1(data1,21)
    data1 = feature1(data1,34)
    data1 = feature1(data1,55)
    data1 = feature1(data1,89)
    data1 = feature1(data1,144)
    data1 = feature1(data1,233)

    data1 = feature2(data1,10)
    data1 = feature2(data1,21)
    data1 = feature2(data1,55)
    data1 = feature2(data1,89)

    data1 = feature3(data1,3)
    data1 = feature3(data1,5)
    data1 = feature3(data1,8)
    data1 = feature3(data1,13)
    data1 = feature3(data1,21)
    data1 = feature3(data1,34)
    data1 = feature3(data1,55)

    data1 = feature4(data1,'date')

    data1 = feature5(data1,55)
    data1 = feature5(data1,70)
    data1 = feature5(data1,89)
    data1 = feature5(data1,144)

    data1 = feature6(data1,8)
    data1 = feature6(data1,13)
    data1 = feature6(data1,21)
    data1 = feature6(data1,34)
    data1 = feature6(data1,55)
    data1 = feature6(data1,89)
    
    data1 = feature8(data1,21)
    data1 = feature8(data1,34)
    data1 = feature8(data1,55)
    data1 = feature8(data1,89)
    
    data1 = feature9(data1,21)
    data1 = feature9(data1,34)
    data1 = feature9(data1,55)
    data1 = feature9(data1,89)
    
    data1 = feature10(data1,21)
    data1 = feature10(data1,34)
    data1 = feature10(data1,55)
    data1 = feature10(data1,89)
    
    data1 = feature11(data1,9)
    data1 = feature11(data1,14)
    
    data1 = feature12(data1,10)
    data1 = feature12(data1,30)
    
    data1 = feature13(data1,9)
    data1 = feature13(data1,21)
    data1 = feature13(data1,34)
    data1 = feature13(data1,55)
    # print(data1)
    # 对于close_shift_n，return填充0
    # data1['close_shift_n'].fillna(0,inplace=True)
    # data1['return'].fillna(0,inplace=True)
    col_list = [x for x in list(data1.columns) if 'feature' in x]
    data1.dropna(subset = col_list,how = "any",inplace=True)
    # print(data1)
    data1 = data1.reset_index(drop=True)

    print(data1)
    
    
    # 截取因子和特征矩阵
    
    X = data1[col_list]
    Y = data1['label']
    if X.isnull().sum().sum()!=0 or Y.isnull().sum()!=0:
        print('数据存在空值,重新处理...')
        print(X.isnull().sum().sum(),Y.isnull().sum())
        break
    
    
    # 找出分类型特征
    classf = [x for x in list(X.columns) if 'feature1_' in x or 'feature4' in x]
    # 找出连续型特征
    col = X.columns.tolist()
    for i in classf:
        col.remove(i)
    
    u = copy.deepcopy(X)
    
    
    

    
    # 加载无量纲模型
    ss = joblib.load(ss_path)
    u.loc[:,col] = ss.transform(X.loc[:,col])
    # 加载模型
    estimator = joblib.load(model_path)
    # # 预测值
    y_predict = estimator.predict(u)
    data1['predict'] = y_predict
    origin_col = [x for x in list(data1.columns) if 'feature' not in x]
    data = data1[origin_col]
    # 保存预测数据
    # now = datetime.now().strftime(format="%Y-%m-%d_%H%M")
    # predict_file = 'predict_' + now+ '.csv'
    # data1[origin_col].to_csv(predict_file)

    # 实施预测单个值
    # time_ = datetime.now()
    # last_time1 = data.date.iloc[-1]
    # last_time2 = data.date.iloc[-2]
    # print(time_,last_time1,last_time2)

    # 查看最近的预测效果
    data = data.copy()
    data = compute_profit(data,late_n_profit)
    print(data)
    data.reset_index(drop=True,inplace=True)
    len = len(data)
    print(data)
    # print(n)
    # 画图
    p = Dyp(data,len,'pos')
    p.dynamic_plot()
    time.sleep(1000)
    




    

# 取出end
# 然后插入
# 然后计算因子
# 然后数据处理
# 然后带入模型计算
