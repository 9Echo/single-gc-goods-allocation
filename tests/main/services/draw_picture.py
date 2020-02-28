import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpathes
from model_config import ModelConfig
from  app.main.services.loading_sequence_service import  loading




def get_data():
    return loading()

if __name__ == '__main__':
   result=get_data()
   print(result)

   fig, ax = plt.subplots()
   ax.spines['top'].set_visible(False)
   ax.spines['right'].set_visible(False)
   ax.spines['bottom'].set_visible(False)
   ax.spines['left'].set_visible(False)

   xy1 = np.array([0.2, 0.2])
   xy2 = np.array([0.305, 0.1])
   xy3 = np.array([0.6, 0.2])
   # 圆形
   circle = mpathes.Circle(xy1, 0.1)
   ax.add_patch(circle)
   # 长方形
   rect = mpathes.Rectangle(xy2, 0.2, 0.2, color='g')
   ax.add_patch(rect)
   # 六边形
   polygon = mpathes.RegularPolygon(xy3, 6, 0.1, color='g')
   ax.add_patch(polygon)

   plt.axis('equal')
   plt.grid()
   plt.xticks([])  # 去掉x轴
   plt.yticks([])  # 去掉y轴
   plt.axis('off')  # 去掉坐标轴
   plt.show()




