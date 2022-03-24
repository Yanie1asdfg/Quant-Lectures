import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import numpy as np

POINTS = 100
sin_list = [0]* POINTS
indx = 0

fig, ax = plt.subplots()
ax.set_ylim([-2, 2])  # 设置x区间
ax.set_xlim([0, POINTS]) # 设置y区间
ax.set_autoscale_on(False)  #用于设置是否在绘图命令上应用自动缩放。
ax.set_xticks(range(0, 100, 10)) # 设置刻度 不包括右端
ax.set_yticks(range(-2, 3, 1))
ax.grid(True)

line_sin, = ax.plot(range(POINTS), sin_list, label='Sin() output', color='cornflowerblue')


def sin_output(ax):
    global indx, sin_list, line_sin
    if indx == 20:
        indx = 0
    indx += 1
 
    sin_list = sin_list[1:] + [np.sin((indx / 10) * np.pi)]
    line_sin.set_ydata(sin_list)
    ax.draw_artist(line_sin) #连续多帧图像的显示建议使用draw_artist()方法
    ax.figure.canvas.draw()  #figure.canvas.draw()用来重新绘制整张图表
 
# Create a new timer object. Set the interval to 100 milliseconds
# (1000 is default) and tell the timer what function should be called.
timer = fig.canvas.new_timer(interval=500)
timer.add_callback(sin_output, ax)
timer.start()

plt.show()