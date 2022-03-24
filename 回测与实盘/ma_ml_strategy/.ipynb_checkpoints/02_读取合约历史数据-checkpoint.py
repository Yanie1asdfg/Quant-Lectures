import pandas as pd
from sqlalchemy import create_engine
import pymysql
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
print(data)