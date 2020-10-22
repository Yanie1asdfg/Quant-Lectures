from PyQt5.QtWidgets import *
# from pyqtgraph.Qt import QtGui, QtCore
import sys
import pyqtgraph as pg
import pandas as pd
import numpy as np
from datetime import datetime
from CandlestickItem import *

class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A股股票历史走势K线图")
        self.main_widget = QWidget() # 创建一个主部件
        self.main_layout = QGridLayout() # 创建一个网格布局
        self.main_widget.setLayout(self.main_layout) # 设置主部件的布局为网格
        self.setCentralWidget(self.main_widget) # 设置窗口默认部件

        self.main_btn = QPushButton("打开主图") # 创建一个按钮部件
        self.tag_btn = QPushButton("打开附图") # 创建一个按钮部件

        self.k_widget = QWidget() # 实例化一个widget部件作为K线图部件
        self.k_layout = QGridLayout() # 实例化一个网格布局层
        self.k_widget.setLayout(self.k_layout) # 设置K线图部件的布局层
        self.k_plt = pg.GraphicsLayoutWidget() # 实例化一个绘图部件
        # self.k_plt2 = pg.PlotWidget() # 实例化一个绘图部件
        # label = pg.LabelItem(justify='right')
        # self.k_plt.addItem(label)
        self.k_layout.addWidget(self.k_plt) # 添加绘图部件到K线图部件的网格布局层
        # self.k_layout.addWidget(self.k_plt2)
        self.p1 = self.k_plt.addPlot()
        # self.k_plt.addItem(self.p1)
        # print(type(self.k_plt),type(self.p1))

        #读取数据
        self.data = pd.read_csv('1.csv')
        self.t_data = pd.read_csv('2.csv')
        print(len(self.data),len(self.t_data))

        # 清除空值
        self.data = self.data.dropna()
        self.t_data = self.t_data.dropna()

        # 重设索引
        self.data.reset_index(drop=True,inplace=True)
        self.t_data.reset_index(drop=True,inplace=True)
        print(len(self.data),len(self.t_data))

        # tag 保留开始时间，结束时间
        self.t_data = self.t_data[['starttime',"endtime"]]
        # print(type(self.t_data.iloc[0,0]))

        #开始时间与结束时间组成的字典
        starttime = self.t_data['starttime'].tolist()
        endtime = self.t_data['endtime'].tolist()
        timedict1 = dict(zip(endtime,starttime))

        # 原数据 时间和 open 组成字典
        date = self.data['Date'].tolist()
        openp = self.data['Open'].tolist()
        self.op = openp
        timedict2 = dict(zip(date,openp))
        # print(timedict2)

        # 加入starttime endtime 开始的坐标  开始时间的open 
        for i in self.data.index:
            if self.data.loc[i,'Date'] in endtime:
                self.data.loc[i,'endtime'] = self.data.loc[i,'Date']
                st = timedict1[self.data.loc[i,'Date']]
                self.data.loc[i,'starttime'] = st
                try:
                    self.data.loc[i,'startnum'] = date.index(st)
                except:
                    continue
                if st in date:
                    self.data.loc[i,'start_open'] = timedict2[st]

        # 检查startnum的坐标
        # print(self.data.tail(100))

        # 将缺失值填补为-5
        self.data = self.data.fillna(-5)

        # self.data1 = self.data.dropna()
        # print(self.data1)
        
        # 
        self.data_list = []
        self.tag_list = []
        for d, row in self.data.iterrows():
            # 将时间转换为数字
            # date_time = datetime.strptime(dates, '%Y-%m-%d %H:%M:%S')
            # t = date2num(date_time)
            open, high, low, close,endtime,starttime,startnum, start_open= row[1:9]
            # 制成K线图的元组
            datas = (d, open, close, low, high)
            if start_open != -5 and startnum != -5 and endtime !=starttime:
                tags = ([startnum,d],[start_open,open])
                self.tag_list.append(tags)
                # print(tags)
                # print(datas)

            
            
            self.data_list.append(datas)
            # if d == 5000:
                # break

        self.data.set_index('Date',inplace = True)
        self.data.index = pd.to_datetime(self.data.index, format = '%Y-%m-%d %H:%M:%S')

        self.axis_dict = dict(enumerate(self.data.index))
        print('==')
        # self.axis_1 = [(i, self.data.index.tolist()[i]) for i in range(0, len(self.data.index), 3)]
        
        # print(self.axis_1)
        print(self.data.head(10))
        self.main_layout.addWidget(self.main_btn,0,0,1,1)
        self.main_layout.addWidget(self.k_widget,0,1,7,5)

        self.main_btn.clicked.connect(self.plot_k_line) # 绑定 查询 按钮点击信号
        # self.tag_btn.clicked.connect(self.tag_slot) # 绑定 确定 按钮点击信号

    # 画 K 线
    def plot_k_line(self):
        # 从 0 开始将时间的索引放入字典 {0: '2017-12-20', 1: '2017-12-21'...
        # self.axis_dict = dict(enumerate(self.data.index))
        # axis_1 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 3)]  # 获取日期值
        # print(axis_1)
        # print('==')
        # axis_2 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 5)]
        # axis_3 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 8)]
        # axis_4 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 10)]
        # axis_5 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 30)]
        # stringaxis = pg.AxisItem(orientation='bottom')  # 创建一个刻度项
        # # stringaxis.setTicks([axis_5, axis_4, axis_3, axis_2, axis_1, self.axis_dict.items()])  # 设置X轴刻度值
        # self.k_plt.getAxis("bottom").setTicks([self.axis_dict.items()])
        
        self.p1.clear() # 清空绘图部件中的项
        item = CandlestickItem(self.data_list)  # 生成蜡烛图数据

        self.p1.addItem(item)
        
        self.p1.showGrid(x=True, y=True)
        # self.p1.setYRange(y_min,y_max)
        self.p1.setLabel(axis='left', text='指数')  # 设置Y轴标签
        self.p1.setLabel(axis='bottom', text='日期')  # 设置X轴标签
        print('==')
        for e in range(len(self.tag_list)):
            self.p1.plot(self.tag_list[e][0],self.tag_list[e][1], pen=(0,0,200),size=10, symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")

        print(type(self.op[0]))
        max1 = max(self.op[400:700])
        print(max)
        min1 = min(self.op[400:700])
        self.p1.setRange(xRange=(400,700),yRange=(min1-0.001,max1+0.001)) #,yRange=(self.data_list[400][3]-0.01,self.data_list[700][4]+0.01)
        # self.p1.setAutoVisible(y=True)
        self.p1.getAxis("bottom").setTicks([self.axis_dict.items()])

        print('+++++')

        self.label = pg.TextItem()  # 创建一个文本项
        self.p1.addItem(self.label)  # 在图形部件中添加文本项
        self.vLine = pg.InfiniteLine(angle=90, movable=False, )  # 创建一个垂直线条
        self.hLine = pg.InfiniteLine(angle=0, movable=False, )  # 创建一个水平线条
        self.p1.addItem(self.vLine, ignoreBounds=True)  # 在图形部件中添加垂直线条
        self.p1.addItem(self.hLine, ignoreBounds=True)  # 在图形部件中添加水平线条 

        self.vb = self.p1.vb
        self.move_slot = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.print_slot)


    # 响应鼠标移动绘制十字光标
    def print_slot(self, event=None):
        if event is None:
            print("事件为空")
        else:
            pos = event[0]  # 获取事件的鼠标位置
            try:
                # 如果鼠标位置在绘图部件中
                if self.p1.sceneBoundingRect().contains(pos):
                    mousePoint = self.vb.mapSceneToView(pos)  # 转换鼠标坐标
                    index = int(mousePoint.x())  # 鼠标所处的X轴坐标
                    pos_y = int(mousePoint.y())  # 鼠标所处的Y轴坐标
                    if -1 < index < len(self.data.index):
                        # 在label中写入HTML
                        self.label.setHtml(
                            "<p style='color:white'><strong>日期：{0}</strong></p><p style='color:white'>开盘：{1}</p><p style='color:white'>收盘：{2}</p><p style='color:white'>最高价：<span style='color:red;'>{3}</span></p><p style='color:white'>最低价：<span style='color:green;'>{4}</span></p><p style='color:white'>第n个：<span style='color:green;'>{5}</span></p>".format(
                                self.axis_dict[index], self.data['Open'][index], self.data['Close'][index],
                                self.data['High'][index], self.data['Low'][index],index))
                        self.label.setPos(mousePoint.x(), mousePoint.y())  # 设置label的位置
                    # 设置垂直线条和水平线条的位置组成十字光标
                    self.vLine.setPos(mousePoint.x())
                    self.hLine.setPos(mousePoint.y())
            except Exception as e:
                print(traceback.print_exc())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUi()
    ex.show()
    sys.exit(app.exec_())