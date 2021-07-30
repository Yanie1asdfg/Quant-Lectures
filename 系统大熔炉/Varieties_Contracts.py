from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
from sqlalchemy import create_engine 
from datetime import datetime
import re
import pymysql
import os
import PIL.Image as Image
import matplotlib.pyplot as plt

class Varieties_Contracts():
    def __init__(self):
        self.spider_data = []
        self.abitrage_dic = {}
        self.goods_dict = {}
        self.sort_ab = {}

    # 获取单个html文本
    def askURL(self,url):
        head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.63"}
        req = urllib.request.Request(url = url,headers=head)
        html = ""
        try:
            response = urllib.request.urlopen(req)
            html = response.read().decode('utf8')
            return html
        except urllib.error.URLError as e:
            if hasattr(e,'code'):
                print(e.code)
            if hasattr(e,'reason'):
                print(e.reason)

    # 从东方财富获取单个品种合约数据
    def spider_single_data(self,exchange,num):
        '''
        exchange:交易所代码
        num:合约代码
        '''
        url = 'http://futsse.eastmoney.com/list/variety/'+exchange+'/'+str(num)+'?cb=aaa_callback&orderBy=zdf&sort=desc&pageSize=20&pageIndex=0&callbackName=aaa_callback&blockName=callback&_=1622774643144'
        html = self.askURL(url)
        bs = BeautifulSoup(html,"html.parser")
        # 提取字段中的数据
        if len(bs.text)<=100:
            print(str(exchange)+' '+str(num)+' 下没有数据....')
            return 0,0,0
        elif len(bs.text)>100:
            list_all=[]
            oper_s=bs.text
            i_num=0
            while(True):
                x=oper_s.find('{"qrspj"',i_num)

                if(not x==-1):
                    i_num=x+1
                    list_all.append(x)
                else:
                    break
            data_list = []
            for a in list_all:
                res = re.search("{.*?}",bs.text[a:])  #万能的.*?
                unit= eval(res.group(0))
                data_list.append(unit)
            # 转为dataframe 表格
            data = pd.DataFrame(data_list)
            # 保留关键列
            data = data[["utime",'dm','uid','name','p','o','h','l','zjsj','vol']]
            data.columns = ['date','code','excode','name','new_p','open','high','low','pre_close','volume']
            data['date'] = data['date'].apply(lambda x : datetime.utcfromtimestamp(x).strftime('%Y-%m-%d'))
            # 数据以代码排序
            data = data.sort_values(by='code',ascending = True,ignore_index = True)
            # code  SHFE|cu   name 沪铜
            code = ''.join(re.findall(r'[A-Za-z|]', data.loc[0,'excode']))
            name = ''.join(re.findall(u"[\u4e00-\u9fa5]+", data.loc[0,'name']))
            if exchange == "115" and num==5:
                name = ''.join(re.findall(r'[A-Za-z|]', data.loc[0,'name']))
            if exchange == "114" and num==20:
                name = ''.join(re.findall(r'[A-Za-z|]', data.loc[0,'name']))
            # 将code改为 SHFE_cu
            code = code.replace('|','_')
            # 获取主力合约的一行
            dominant =data[(data.code.str.contains('M|m')==True)&(data.name.str.contains('主力')==True)&(data.name.str.contains('次')==False)]
            dominant2 =data[(data.name.str.contains('次主力')==True)]
            # if len(dominant)==0 or len==True:
            #     return
            # 主力合约的new_p 与 开盘价
            new_p = dominant.new_p.values[0]
            open_ = dominant.open.values[0]
            # 找次主力
            new_p2 = dominant2.new_p.values[0]
            open_2 = dominant2.open.values[0]
            # 主力、次主力合约必须要有数据
            if data.new_p.all()=='-':
                print(str(exchange)+' '+str(num)+' '+name+' 完全没有数据........')
                return 0,0,0
            if new_p == '-' or open_ == '-' or new_p2 == '-' or open_2 == '-':
                print(name+' 主力存在空数据...')
                return 0,0,0
            data.loc[(data.new_p ==new_p) & (data.open ==open_) & (data.name.str.contains('主力')==False) ,'dominant']=1
            data.loc[(data.new_p ==new_p2) & (data.open ==open_2) & (data.name.str.contains('次主力')==False) ,'dominant']=2
            # 删除含有'-'的数据
            # 中文转码
            data.name=data.name.str.encode(encoding = 'raw_unicode_escape')
            data = data[(data.new_p!='-')&(data.open!='-')]
            print(str(exchange)+' ',num,name)
            return code,name,data

    # 存入数据库  
    def to_mysql(self,code,name,data):
        yconnect = create_engine('mysql+pymysql://root:0000@localhost:3306/db_eastmoney?charset=utf8mb4')  #
        pd.io.sql.to_sql(data,code.lower(), yconnect, schema='db_eastmoney' , index = False, index_label=None,if_exists='replace')
        print('    '+name+' '+code+' '+'已经写入mysql')

    # 获取所有品种合约数据存入mysql
    def spider_datas(self):
        exchange = ['113','114','115'] #'113','114',
        for k in exchange:
            for i in range(30):
                code,name,data = self.spider_single_data(k,i)
                # if code!=0:
                #     self.to_mysql(code,name,data)

    # 从MySQL获取某个database的表名
    def contlist_from_mysql(self,dbname):
        # 从数据库中取数据
        import pymysql.cursors 
        dbname = dbname  #'db_eastmoney'
        connection = pymysql.connect(host='localhost',
                                    user='root',
                                    password='0000',
                                    db=dbname,
                                    charset='utf8',
                                    cursorclass=pymysql.cursors.DictCursor)
        results =[]
        try:
            with connection.cursor() as cursor:
                sql = '''SHOW TABLES'''
                cursor.execute(sql)
                result = cursor.fetchall() 
                for i in range(len(result)):
                    results.append(result[i]['Tables_in_'+dbname])
        finally:
            connection.close()
        return results

    # 从数据库读取单个数据
    def datafmysql(self,table_name,conn):
        sql_query = 'SELECT * FROM '+table_name
        # 从mysql中读取表
        df1 = pd.read_sql(sql_query, con=conn)
        # 中文转码
        df1.name = df1.name.apply(lambda x:eval(repr(x).replace('\\\\', '\\')))
        # TA特殊处理
        if 'PTA' in df1.loc[0,'name']:
            # 提取字母
            name = ''.join(re.findall(r'[A-Za-z]', df1.loc[0,'name']))  
        else:
            # 提取中文
            name = ''.join(re.findall(u"[\u4e00-\u9fa5]+", df1.loc[0,'name']))
            
        # 提取字母  code  AP 
        code = ''.join(re.findall(r'[A-Za-z]', df1.loc[0,'code']))
        # 去掉主力和次主力的行 带有- 的行
        df1 = df1[(df1.name.str.contains('主力')==False) & (df1.new_p!='-')]
        # 转换类型
        df1['new_p'] = df1['new_p'].astype('float64')
        df1['volume'] = df1['volume'].astype('int64')
        df1['money'] = df1['new_p']*df1['volume']
        
        if len(df1)>=2:
            date = df1.date.tolist()[0]
            const_price = {}
            const_price['现货'] = self.goods_dict[name]
            const_price.update(dict(zip(df1.code,df1.new_p)))
            self.abitrage_dic[name] = {'date':date,'合约价格':const_price,'主力':df1.loc[df1.dominant==1,'code'].values[0],'次主力':df1.loc[df1.dominant==2,'code'].values[0]}

    # 从数据库读取所有data
    def get_all_data(self,dbname,dic):
        
        code_dic = {value.lower() for key,value in dic.items()}
        results = vc.contlist_from_mysql(dbname)
        #将大写变小写，取出表名
        tablenames = []
        for i in results:
            index = i.index('_')
            for a in code_dic:
                if i[index+1:]==a:
                    tablenames.append(i)
        # 获取现货
        self.get_goods_price()
        conn = pymysql.connect(host = "localhost",port=3306,user='root',passwd='0000',db=dbname,charset="utf8")
        for i in tablenames:
            self.datafmysql(i,conn)
        conn.close()  #使用完后记得关掉
        # print(self.abitrage_dic)
        
    # 获取现货价格
    def get_goods_price(self):
        df = pd.read_csv(r'现货价格.csv',encoding='gb2312')
        self.goods_dict = df.iloc[-1].to_dict()
        return self.goods_dict

    # 生成图片并保存
    def all_plot(self):
        key_list = self.abitrage_dic.keys()
        num_list = [len(i['合约价格']) for i in list(self.abitrage_dic.values())]
        t = max(num_list)
        self.sort_ab = dict(zip(key_list,num_list))
        self.sort_ab = dict(sorted(self.sort_ab.items(),key=lambda x:x[1]))
        import matplotlib.pyplot as plt
        import os
        plt.rcParams['font.sans-serif']=['Simhei'] #用来正常显示中文标签
        plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
        path = r'C:\Users\17218\Desktop\images\image'
        for key,value in self.sort_ab.items():
            date = self.abitrage_dic[key]['date']
            ft_name = key
            names = list(self.abitrage_dic[key]['合约价格'].keys())
            values = list(self.abitrage_dic[key]['合约价格'].values())
            n = value
            fig=plt.figure(figsize=(n+1,5))
            plt.ylim((min(values)-100,max(values)+100))
            plt.bar(names, values,color='cyan')
            plt.scatter(names, values,color='red')
            plt.plot(names, values)
            for a,b in self.abitrage_dic[key]['合约价格'].items():
                plt.text(a, b+0.5, '%.1f' % b, ha='center',weight = "light",va= 'bottom',fontsize=15)
                plt.title(ft_name+' '+date,fontsize=40)
                plt.xticks(fontproperties='Fangsong',fontsize = 16,weight='bold')
            # plt.xlabel("期现",fontproperties = 'Simhei',fontsize = 18)#设置x坐标标注，字体为18号
            # plt.ylabel("价格",fontproperties = 'Simhei',fontsize = 18)
            
            # import matplotlib
            # matplotlib.use('Agg')
            plt.savefig(os.path.join(path,ft_name,date+".png"),bbox_inches = 'tight')
            print(ft_name,'图片已生成......')

    # 合成图片
    def syn_images(self,date):
        IMAGES_PATH = r'C:\Users\17218\Desktop\images\image'  # 图片集地址
        IMAGES_FORMAT = ['.PNG']  # 图片格式
        IMAGE_SAVE_PATH = r'C:\Users\17218\Desktop\images\final'  # 图片转换后的地址
        IMAGE_SAVE_PATH = os.path.join(IMAGE_SAVE_PATH,date+'.png')
        imagelist = [os.path.join(IMAGES_PATH,x,date+'.png') for x in self.sort_ab.keys()]
        images_size = []
        for i in imagelist:
            img=Image.open(i)
            img1 = img.load()
            images_size.append(img.size[0])
        print('各个图片size',images_size)
        s = [images_size[0]+images_size[1]+images_size[2]+images_size[3],images_size[4]+images_size[5]+images_size[6],images_size[7]+images_size[8],images_size[9]+images_size[10]]
        IMAGE_COLUMN = 3
        IMAGE_ROW = 4
        IMAGE_c_SIZE = max(images_size)*2+500
        IMAGE_r_SIZE = 400
        self.image_compose(IMAGE_ROW,IMAGE_COLUMN,IMAGE_c_SIZE,IMAGE_r_SIZE,imagelist,images_size,IMAGE_SAVE_PATH)
        print('图片已合成......')
    
    # 定义图像拼接函数
    def image_compose(self,IMAGE_ROW,IMAGE_COLUMN,IMAGE_c_SIZE,IMAGE_r_SIZE,imagelist,images_size,IMAGE_SAVE_PATH):
        to_image = Image.new('RGB', (IMAGE_c_SIZE, IMAGE_ROW * IMAGE_r_SIZE+400),'white')  # 创建一个新图
        print('大画布图片size',to_image.size)
        # 循环遍历，把每张图片按顺序粘贴到对应位置上
        e = 0
        for y in range(1, IMAGE_ROW + 1):
            x_pos = 40
            while e<len(images_size) and x_pos+images_size[e]<IMAGE_c_SIZE-100:
                from_image = Image.open(imagelist[e]).resize((images_size[e], int(images_size[e]/100-6)*20+380), Image.ANTIALIAS)             
                to_image.paste(from_image, (x_pos, (40+5*y)*y+(y - 1) * IMAGE_r_SIZE))
                x_pos = x_pos+images_size[e]+20
                e = e+1
        return to_image.save(IMAGE_SAVE_PATH)  # 保存新图



if __name__ == '__main__':
    vc = Varieties_Contracts()
    # vc.spider_datas()   # 将东方财富数据写入mysql

    dbname = 'db_eastmoney'
    dict1 = {'白糖':'SR','豆粕':'M','玉米':'C','玉米淀粉':'CS','苹果':'AP','菜粕':'RM','纯碱':'SA','玻璃':'FG','甲醇':'MA','棉花':'CF','尿素':'UR'} 
    vc.get_all_data(dbname,dict1)  #从数据库读取所有data 获取现货
    vc.all_plot()    # 生成图片并保存

    date = '2021-07-30'
    vc.syn_images(date)