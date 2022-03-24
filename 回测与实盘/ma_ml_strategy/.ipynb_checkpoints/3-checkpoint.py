import os
path = r'E:\repo\ml_bt'
all_path = [os.path.join(path,x) for x in os.listdir(path)]
# print(all_path)

# 将全部的数据存入字典
import pandas as pd 
start_end_dic = {}
for e in all_path:
    data = pd.read_csv(e,index_col=0)
    grag_volume= data.describe([0.1,0.25,0.3,0.4,0.5]).T.loc['volume','50%']
    grag_open_interest = data.describe([0.1,0.25,0.3,0.4,0.5]).T.loc['open_interest','40%']
    grag_open_interest2 = data.describe([0.1,0.25,0.3,0.4,0.5]).T.loc['open_interest','50%']
#     print(e,grag_volume,grag_open_interest,grag_open_interest2)
    data1 = data.copy()
    for i in data1.index:
        if data1.loc[i,'open_interest']>30000:
            start1 = i
            break
    for i in data1.index[::-1]:
        if 'MA2201' in e:
            end1 = len(data1)
            break
        if data1.loc[i,'open_interest']<60000 and data1.loc[i-1,'open_interest']>60000:
            end1 = i
            break
    # print(start1,end1)
    data2 = data1.iloc[start1:end1,:]
    start_end_dic[e] = (start1,end1,data)
#     print(data2,len(data))
# print(start_end_dic)

start = start_end_dic[all_path[-2]][0]
end = start_end_dic[all_path[-2]][1]
data = start_end_dic[all_path[-2]][2]

data['close_shift(-5)'] = data['close'].shift(-5)
# data['return'] =0.5 + 0.5*np.sign(data_cleaned['Close0_shift(-1)']-data_cleaned['Close0'])
data['return'] = data['close_shift(-5)']-data['close']
from CreateFeatures import * 
import copy
datar = copy.deepcopy(data)
datar = feature1(datar,13)
datar = feature1(datar,21)
datar = feature1(datar,34)
datar = feature1(datar,55)
datar = feature1(datar,89)
datar = feature1(datar,144)
datar = feature1(datar,233)

datar = feature2(datar)

datar = feature3(datar,3)
datar = feature3(datar,5)
datar = feature3(datar,8)
datar = feature3(datar,13)
datar = feature3(datar,21)
datar = feature3(datar,34)
datar = feature3(datar,55)

datar = feature4(datar,'date')

datar = feature5(datar,8)
datar = feature5(datar,13)
datar = feature5(datar,21)
datar = feature5(datar,34)
datar = feature5(datar,55)
datar = feature5(datar,89)
print(datar)
