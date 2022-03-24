
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation 
import time 
import matplotlib.font_manager as font_manager
from Dyp import *
from datetime import datetime
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# pd.set_option('max_colwidth', 200)
# pd.set_option('expand_frame_repr', False)
# 读取数据
data0 = pd.read_csv('predict0.csv',index_col=0)
# 计算收益
data = data0.copy()
data = data[data.date>'2021-12-04']


print(data.columns.tolist())
data = compute_profit(data,5)

data.reset_index(drop=True,inplace=True)
len = len(data)
print(data)
# print(n)
# 画图
p = Dyp(data,len,'pos')
p.dynamic_plot()
# print(p.xticks,p.xlabels)