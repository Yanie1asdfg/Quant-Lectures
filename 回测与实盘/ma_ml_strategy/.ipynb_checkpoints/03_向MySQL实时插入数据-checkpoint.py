# 先读取
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import time
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
for i in range(100):
    tu = tuple(data.iloc[-i].tolist())
    print(tu)
    time.sleep(10)


    #引入模块
    # 链接数据库
    conn = pymysql.connect(host='localhost',port=3306,user='root',passwd='123456',db='ml_system')
    #创建游标
    cursor = conn.cursor()
    #插入数据
    cursor.execute("INSERT INTO ma2205_show (date, open, high, low, close, volume, money, open_interest) VALUES "+str(tu))
    #提交
    conn.commit()
    print('ok')
    # #关闭
    conn.close()
    cursor.close()

# def to_mysql(user,password,dbname,code,data,how):
    
#     """
#     :param 
#         user mysql 用户名
#         password mysql密码
#         dbname database名
#         code 表名
#         data 数据 
#     """
#     longstr = 'mysql+pymysql://'+user+':'+password+'@localhost:3306/'+dbname+'?charset=utf8mb4'
#     yconnect = create_engine(longstr)  #
#     pd.io.sql.to_sql(data,code, yconnect, schema=dbname , index = False, index_label=None,if_exists=how)

# to_mysql('root','123456','ml_system','ma2205',data.iloc[-1],'append')
# print('ok')
# 插入