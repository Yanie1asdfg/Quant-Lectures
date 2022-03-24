import pandas as pd
import talib
import numpy as np
from datetime import datetime
import math 


def feature1(data,ma):
    '''
    ++分类型++
    上穿下穿均线
    此根K线open小于等于均值，close大于等于均值，标记为1
    此根K线open大于等于均值，close小于等于均值，标记为-1
    其余为0
    '''
    data['ma'] = data['close'].rolling(ma).mean()
    label = 'feature1_'+str(ma)
    data.loc[(data.open<=data.ma)&(data.close>=data.ma),label]=1
    data.loc[(data.open>=data.ma)&(data.close<=data.ma),label]=-1
    data.loc[(data[label]!=1)&(data[label]!=-1),label]=0  #&(data.ma.isnull()==False)
    data = data.drop(['ma'],axis=1)
    return data

def feature2(data,n):
    '''
    ++连续型++
    dif 为快线
    dea 为慢线
    macd 为柱状值
    data[label] = (data['DIF']-data['DEA'])/n
    '''
    macd_tmp = talib.MACDEXT(data.close, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1, signalperiod=9, signalmatype=1)     
    DIF = macd_tmp[0]                                           #返回的数据分别为短期慢线DIF、长期快线DEA及MACD
    DEA = macd_tmp[1]
    MACD = macd_tmp[2]*2
    data['DIF'] = DIF
    data['DEA'] = DEA
    label = 'feature2_'+str(n)
    data[label] = (data['DIF']-data['DEA'])/n
    data = data.drop(['DIF'],axis=1)
    data = data.drop(['DEA'],axis=1)
    return data

def feature3(data,n):
    """
    ++连续型++
    几日收益率 rate of change
    """
    label = 'feature3_'+str(n)
    data[label] = (data['close']-data['close'].shift(n))/data['close'].shift(n)
    return data

def feature4(data,column):
    """
    ++分类型++
    :param column:字符串时间列名
    返回当前星期几
    """
    label = 'feature4'
    data['datetime'] = pd.to_datetime(data[column], format='%Y-%m-%d %H:%M:%S')
    data[label] = (data['datetime'].dt.dayofweek+1)
    data = data.drop(['datetime'],axis=1)
    return data

def feature5(data,n):
    """
    ++连续型++
    角度对应{(最近close-前n close)/n} 的sin值
    tan(角度) 范围太大不合适
    sin(角度) 更合理
    """
    label = 'feature5_'+str(n)
    # 计算出的已经是tan值
    data['ratio'+str(n)] = (data['close']-data['close'].shift(n))/n   
    # data['c_tan'+str(n)] = data['ratio'+str(n)].apply(lambda x:math.tan(x))
    data[label] = data['ratio'+str(n)].apply(lambda x:math.sin(math.atan(x)))
    data = data.drop(['ratio'+str(n)],axis=1)
    return data

def feature6(data,n):
    """
    ++连续型++
    角度对应{(最近close-前n close)/n**2} 的sin值
    tan(角度) 范围太大不合适
    sin(角度) 更合理
    """
    label = 'feature6_'+str(n)
    data['ratio'+str(n)] = (data['close']-data['close'].shift(n))/(n**2)
    # data['c_tan'+str(n)] = data['ratio'+str(n)].apply(lambda x:math.tan(x))
    data[label] = data['ratio'+str(n)].apply(lambda x:math.sin(math.atan(x)))
    data = data.drop(['ratio'+str(n)],axis=1)
    return data

def feature7(data,n):# 废
    """
    ++连续型++
    :Formula: HH(n)-C(t)/HH(n)-LL(n),  包括当前天
    (前n个high的最大值-当前close)/(前n个high的最大值-前n个low的最小值)
    *** 废弃因子，无法实现单峰和双峰
    """
    label = 'feature7_'+str(n)
    data['HH(n)'] = data.high.rolling(n).max()
    data['LL(n)'] = data.low.rolling(n).min()
    data[label] = (data['HH(n)']-data['close'])/(data['HH(n)']-data['LL(n)'])
    data = data.drop(['HH(n)','LL(n)'],axis=1)
    return data 

def feature8(data,ma):
    """
    ++连续型++
    :Formula: [C(t)-MA(n)]/MA(n)
    """
    label = 'feature8_'+str(ma)
    data['ma'] = data['close'].rolling(ma).mean()
    data[label] = (data['close']-data['ma'])/data['ma']
    data = data.drop(['ma'],axis=1)
    return data

def feature9(data,ma):
    """
    ++连续型++
    :Formula: abs[C(t)-MA(n)]/MA(n)
    """
    label = 'feature9_'+str(ma)
    data['ma'] = data['close'].rolling(ma).mean()
    data[label] = abs(data['close']-data['ma'])/data['ma']
    data = data.drop(['ma'],axis=1)
    return data

def feature10(data,ma):
    """
    ++连续型++
    :Formula: abs[C(t)-MA(n)]/sqrt(MA(n))
    """
    label = 'feature10_'+str(ma)
    data['ma'] = data['close'].rolling(ma).mean()
    data[label] = abs(data['close']-data['ma'])/data['ma'].apply(np.sqrt)
    data = data.drop(['ma'],axis=1)
    return data

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

def feature11(data,period):
    """
    ++连续型++
    计算RSI的值
    """
    label = 'feature11_'+str(period)
    close = np.array(data.close)
    rsi = RSI(close,period)
    data[label] = rsi
    return data

def feature12(data,n):
    """
    ++连续型++
    计算当前成交量/前N周期成交量均值的倍数
    """
    label = 'feature12_'+str(n)
    data['volume_mean'] = data['volume'].rolling(n).mean()
    data[label] = data['volume']/data['volume_mean']
    data = data.drop(['volume_mean'],axis=1)
    return data

def feature13(data,n):
    """
    ++连续型++
    计算当前n周期的波动率std
    """
    label = 'feature13_'+str(n)
    data[label] = data['close'].rolling(n).std()
    return data



def bmad(factor):
    # 去0值
    med = np.median(factor)
    factor = np.where(factor==0,med,factor)
    return factor
def mad(factor,n):
    # 去极值
    med = np.median(factor)
    mad = np.median(abs(factor-med))
    high = med + n * 1.4826 * mad
    low = med - n * 1.4826 * mad
    print(med,mad,high,low)
    factor = np.where(factor>high,high,factor)
    factor = np.where(factor<low,low,factor)
    return factor
def feature19(data):
    
    """
    :Formula: C(t)-C(t-1)/C(t-1) * V(t)
    1.对volume去0值 
    2.直接用volume，log_volume太小
    3.对最终特征去极值 
    """
    data['volume'] = bmad(data.volume)
    # data['log_volume'] = data['volume'].apply(lambda x:math.log(x))
    data['feature6'] = (data['close']-data['close'].shift(1))/data['close'].shift(1) * data['volume']
    data.feature6 = data.feature6.fillna(np.mean(data.feature6))
    data['feature6'] = mad(data['feature6'],5)*3
    return data

def feature17(data):
    """
    :Formula:  DIFF : EMA(CLOSE,SHORT) - EMA(CLOSE,LONG);
               DEA  : EMA(DIFF,M);
               MACD : 2*(DIFF-DEA);
               feature7: MACD/(abs(DEA)+2000)
    """
    macd_tmp = talib.MACDEXT(data.close, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1, signalperiod=9, signalmatype=1)
    diff = macd_tmp[0]
    mindiff = diff.min()
    dea = macd_tmp[1]
    macd = macd_tmp[2]
    data['feature7'] = macd/(abs(diff)+2000)
    data.feature7 = data.feature7.fillna(np.mean(data.feature7))
    data['feature7'] = mad(data['feature7'],1)*1000
    return data
    

if __name__ == '__main__':
    import os
    path = r'E:\repo\ml_bt'
    all_path = [os.path.join(path,x) for x in os.listdir(path)]
    data = pd.read_csv(all_path[-2],index_col=0)
    data = feature5(data,8)
    data = feature5(data,13)
    data = feature5(data,21)
    data = feature5(data,34)
    data = feature5(data,55)
    data = feature5(data,89)
    # data.describe().T
    print(data.describe())
