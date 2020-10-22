'''
接着创建一个名为CandlestickItem()的类，其继承于pyqtgraph的GraphicsObject类。
通过QPicture和QPainter进行绘图操作实现K线图的绘制
'''
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# K线图绘制类
class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data  # data里面必须有以下字段: 时间, 开盘价, 收盘价, 最低价, 最高价
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture() # 实例化一个绘图设备
        p = QPainter(self.picture) # 在picture上实例化QPainter用于绘图
        p.setPen(pg.mkPen('w')) # 设置画笔颜色
        w = (self.data[1][0] - self.data[0][0]) / 3
        for (t, open, close, min, max) in self.data:
            # print(t, open, close, min, max)
            if max > min:
                p.drawLine(QPointF(t, min), QPointF(t, max)) # 绘制线条
            if open > close: # 开盘价大于收盘价
                p.setBrush(pg.mkBrush('g')) # 设置画刷颜色为绿
            else:
                p.setBrush(pg.mkBrush('r')) # 设置画刷颜色为红
            
            # 前两个参数为矩形的左上角X，Y坐标，后两个参数为宽和高（长度包含起点，所以实际长度减1）
            p.drawRect(QRectF(t - w, open, w*2 , close - open)) # 绘制箱子
            
        p.end()
    
    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
        
    def boundingRect(self):
        return QRectF(self.picture.boundingRect())

    