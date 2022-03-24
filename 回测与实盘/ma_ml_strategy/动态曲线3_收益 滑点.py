
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation 
import time 
import matplotlib.font_manager as font_manager
from Dyp import Dyp
from datetime import datetime
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 200)
pd.set_option('expand_frame_repr', False)

slippage = 2
# 读取数据
data0 = pd.read_csv('predict0.csv',index_col=0)
# 计算收益
data = data0.copy()
data = data[data.date>'2021-12-04']
data.reset_index(drop=True,inplace=True)
# print(data)
data['pos1'] = np.nan
data['pos2'] = np.nan
for i in data.index:
    if i+5>=len(data):
        break
    if data.loc[i,'predict'] == -1:
        data.loc[i+5,'pos1'] = -(data.loc[i+5,'close']-data.loc[i,'close'])
    elif data.loc[i,'predict'] == 1:
        data.loc[i+5,'pos2'] = data.loc[i+5,'close']-data.loc[i,'close']
    if i>1:
        data.loc[i,'pos'] = data.loc[:i,'pos1'].sum() + data.loc[:i,'pos2'].sum() 

print(data)      
# 画图
p = Dyp(data,2000,'pos')
p.dynamic_plot()
