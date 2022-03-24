import pymysql
import pandas as pd

import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation 
import time 
import matplotlib.font_manager as font_manager
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

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
class Dyp():
    def __init__(self,data,n):
        self.n= n
        self.indx = 0
        self.data = data
        self.yarray = [np.nan]*self.n
        
        

    def update(self,point): 
        if self.indx >= n:
            time.sleep(10)
        
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
        close = self.data.close.tolist()[-self.n:]
        fig, ax = plt.subplots(figsize=(12,8)) 
        self.line, = ax.plot(self.yarray,label='动态曲线',color='red') 
        ax.legend(loc='upper center', ncol=4, prop=font_manager.FontProperties(size=10))

        ax.set_xlim([0, self.n])
        ax.set_ylim([min(close)-10, max(close)+10]) 
        
        ax.set_ylabel("distance: m") 
        ax.set_xlabel("time") 
        
        plt.grid(True) 
        
        
        ani = animation.FuncAnimation(fig, self.update,frames=close,interval=1,blit=False) #interval更新频率，以ms计
        plt.legend(loc='upper center', ncol=4, prop=font_manager.FontProperties(size=10))
        plt.show()
        # plt.pause(10)

if __name__ == '__main__':
    data = datafmysql('root','123456','ml_system','ma2205')
    # print(data)
    n = 500
    # time.sleep(10)
    # print(n//100)
    p = Dyp(data,n)
    p.dynamic_plot()
