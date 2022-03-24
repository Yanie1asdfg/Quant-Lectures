import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation 
import time 
import matplotlib.font_manager as font_manager
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def compute_profit(data,n):
    data['date'] = data['date'].astype('str')
    data.reset_index(drop=True,inplace=True)
    data['pos1'] = np.nan
    data['pos2'] = np.nan
    for i in data.index:
        if i+n>=len(data):
            break
        if data.loc[i,'predict'] == -1:
            data.loc[i+n,'pos1'] = -(data.loc[i+n,'close']-data.loc[i,'close'])
        elif data.loc[i,'predict'] == 1:
            data.loc[i+n,'pos2'] = data.loc[i+n,'close']-data.loc[i,'close']
        if i>1:
            data.loc[i,'pos'] = data.loc[:i,'pos1'].sum() + data.loc[:i,'pos2'].sum() 
    data['pos'].fillna(method='ffill',inplace=True)
    data = data.loc[pd.isnull(data['pos'])==False,:]
    return data

class Dyp():
    def __init__(self,data,n,label):
        self.n= n
        self.indx = 0
        self.data = data
        self.yarray = [np.nan]*self.n
        self.label = label
        self.xticks = [x for x in range(0,len(data),250)]
        self.xlabels = [data.loc[x,'date'][:10] for x in self.xticks]
        
        
        

    def update(self,point): 
        # 画完之后，停顿10s
        if self.indx >= self.n:
            time.sleep(100)
        
        self.yarray[self.indx] = point

        #绘图
        self.line.set_ydata(self.yarray) 
        # time.sleep(np.random.rand()/10) 
        #颜色设置 
        plt.setp(self.line, 'color', 'r', 'linewidth', 2.0) 
        self.indx += 1
        return self.line   
    def dynamic_plot(self):
        # 截取数据
        close = self.data[self.label].tolist()[-self.n:]
        fig, ax = plt.subplots(figsize=(12,8)) 
        self.line, = ax.plot(self.yarray,label='动态曲线',color='red') 
        ax.legend(loc='upper center', ncol=4, prop=font_manager.FontProperties(size=10))

        ax.set_xlim([0, self.n])
        ax.set_ylim([min(close)-10, max(close)+10]) 
        
        ax.set_ylabel("盈利: 点数") 
        ax.set_xlabel("日期") 
        # ax.xaxis.set_major_locator(self.all_month)          #设置主刻度
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m')) 
        ax.set_xticks(self.xticks)
        ax.set_xticklabels(self.xlabels, rotation=30, fontsize='small')
        plt.grid(True) 

        
        ani = animation.FuncAnimation(fig, self.update,frames=close,interval=1,blit=False) #interval更新频率，以ms计
        plt.legend(loc='upper center', ncol=4, prop=font_manager.FontProperties(size=10))
        plt.show()
        # plt.pause(10)




# alldays =  mdates.DayLocator()                #主刻度为每天

