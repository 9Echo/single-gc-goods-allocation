import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpathes

plt.xticks([])  #去掉x轴
plt.yticks([])  #去掉y轴
plt.axis('off')  #去掉坐标轴

fig,ax = plt.subplots()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

xy1 = np.array([0.2,0.2])
xy2 = np.array([0.2,0.8])
xy3 = np.array([0.8,0.2])
xy4 = np.array([0.8,0.8])
#圆形
circle = mpathes.Circle(xy1,0.05)
ax.add_patch(circle)
#长方形
rect = mpathes.Rectangle(xy2,0.2,0.1,color='r')
ax.add_patch(rect)
#六边形
polygon = mpathes.RegularPolygon(xy3,6,0.1,color='g')
ax.add_patch(polygon)
#椭圆形
ellipse = mpathes.Ellipse(xy4,0.4,0.2,color='y')
ax.add_patch(ellipse)

plt.axis('equal')
plt.grid()
plt.show()