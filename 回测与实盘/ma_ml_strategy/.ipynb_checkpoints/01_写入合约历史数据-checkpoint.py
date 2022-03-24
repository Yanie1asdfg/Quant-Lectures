'''
是用wind的数据还是天勤，why?
    1.原始数据你直接用聚宽的下载下来
    2.最好用天勤的数据，以后移植到其他电脑上均可以用
    3.然后将天勤的数据接上保存在mysql之中
'''
import os
import pandas as pd
from sqlalchemy import create_engine

path = r'E:\repo\ml_bt\MA'
filename = os.path.join(path,'MA2205.csv')
print(filename)
df = pd.read_csv(filename,index_col=0)
df['date'] = pd.to_datetime(df['date'])
print(df)
print(type(df.loc[0,'date']))

# 存入数据库
# 存入数据库  
def to_mysql(user,password,dbname,code,data,how):
    
    """
    :param 
        user mysql 用户名
        password mysql密码
        dbname database名
        code 表名
        data 数据 
    """
    longstr = 'mysql+pymysql://'+user+':'+password+'@localhost:3306/'+dbname+'?charset=utf8mb4'
    yconnect = create_engine(longstr)  #
    pd.io.sql.to_sql(data,code, yconnect, schema=dbname , index = False, index_label=None,if_exists=how)

to_mysql('root','123456','ml_system','ma2205',df,'replace')
print('wok')