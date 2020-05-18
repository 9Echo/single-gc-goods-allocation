import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpathes
from model_config import ModelConfig
from  app.main.services.loading_sequence_service import  loading


def draw_hexagon(side, turtle, product_type, item_id, T):
   """
   画一个六边形

   :param side: 边长
   :param turtle: 海龟绘图对象
   :param product_type: 品种
   :param item_id: 物资代码
   :param T: 判断是否为实体
   :return:
   """
   turtle.right(60)
   if T == "T":
      for n in range(6):
         turtle.fd(side)
         turtle.left(60)
   else:
      for n in range(6):
         for k in range(5):
            turtle.fd(side / 10)
            turtle.pu()
            turtle.fd(side / 10)
            turtle.pd()
         turtle.left(60)
   turtle.seth(0)
   turtle.pu()
   turtle.fd(side / 3)
   turtle.write(product_type)
   turtle.write(" " * 10 + item_id)
   turtle.bk(side / 3)
   turtle.seth(0)


def draw_circle(r, turtle, product_type, item_id, T):
   """
   画一个圆形

   :param r: 圆的半径
   :param turtle: 海龟绘图对象
   :param product_type: 品种
   :param item_id: 物资代码
   :param T: 是否为实体
   :return:
   """
   turtle.seth(-90)
   if T == "T":
      turtle.circle(r)
   else:
      for i in range(36):
         turtle.circle(r, 5)
         turtle.pu()
         turtle.circle(r, 5)
         turtle.pd()
   turtle.seth(0)
   turtle.pu()
   turtle.fd(r / 5)
   turtle.write(product_type)
   turtle.write(" " * 15 + item_id)
   turtle.bk(r / 5)
   turtle.seth(0)


def draw_rectangle(side, turtle, product_type, item_id, T):
   """
   画一个矩形
   :param side: 边长
   :param turtle: 海龟绘图对象
   :param product_type: 品种
   :param item_id: 物资代码
   :param T: 是否为实体
   :return:
   """
   turtle.seth(-90)
   if T == "T":
      turtle.fd(side / 2)
      for i in range(3):
         turtle.left(90)
         turtle.fd(side)
      turtle.left(90)
      turtle.fd(side / 2)
   else:
      for i in range(2):
         turtle.fd(side / 8)
         turtle.pu()
         turtle.fd(side / 8)
         turtle.pd()
      for j in range(3):
         turtle.left(90)
         for q in range(4):
            turtle.fd(side / 8)
            turtle.pu()
            turtle.fd(side / 8)
            turtle.pd()
      turtle.left(90)
      for i in range(2):
         turtle.fd(side / 8)
         turtle.pu()
         turtle.fd(side / 8)
         turtle.pd()
   turtle.seth(0)
   turtle.pu()
   turtle.fd(side / 7)
   turtle.write(product_type)
   turtle.write(" " * 15 + item_id)
   turtle.bk(side / 7)
   turtle.seth(0)


def distance(dis, turtle):
   """
   显示剩余距离的
   :param dis: 剩余距离
   :param turtle: 海龟绘图对象
   :return:
   """
   if dis > 45:
      dis2 = dis / 2
   else:
      dis2 = dis
   turtle.left(60)
   turtle.fd(10)
   turtle.bk(10)
   turtle.seth(-60)
   turtle.fd(10)
   turtle.bk(10)
   turtle.seth(0)
   turtle.fd(dis2 / 5)
   turtle.write(dis * 2)
   turtle.fd(dis2 * 4 / 5)
   turtle.seth(120)
   turtle.fd(10)
   turtle.bk(10)
   turtle.seth(-120)
   turtle.fd(10)
   turtle.seth(0)


def draw_car(car_width, car_height, turtle):
   """
   画一个车厢
   :param car_width: 车宽
   :param car_height: 车侧栏高
   :param turtle: 海龟绘图对象
   :return:
   """
   turtle.setup(1000, 1000, 200, 200)
   turtle.speed(10000)
   turtle.penup()
   turtle.goto(-car_width / 2, car_height / 2)
   turtle.pendown()
   turtle.pensize(2)
   turtle.right(90)
   turtle.fd(car_height)
   turtle.left(90)
   turtle.fd(car_width)
   turtle.left(90)
   turtle.fd(car_height)


def draw_product(car_dict, turtle, io):
   """
   根据传入的车层信息绘制截面图
   :param car_dict: 车层信息 type：dict
   :param turtle: 海龟绘图对象
   :param io: 判断绘制内/外 部分
   :return:
   """
   # 按比例缩小画图原为2400 缩小一倍
   car_width = 1200
   car_height = 750
   draw_car(car_width, car_height, turtle)
   height_now = 0
   for i in car_dict:
      # 得到每一层的信息的字典
      info = car_dict[i]
      # 层高
      floor_height = info["height_" + io]
      # 层宽
      floor_left_width = info["left_width_" + io]
      # 该层的货物
      floor_goods = info["goods_" + io]
      # 记录图中画的高度
      draw_height = 0
      # 遍历这一层的所有货物
      for j in floor_goods:
         # 获得截面形状
         shape = j[8]
         # 件数
         quantity = int(j[3])
         # 宽
         width = j[1].split("*")[1] if j[1].split("*")[0] > j[1].split("*")[1] else j[1].split("*")[0]
         if shape == "六边形":
            draw = math.sqrt(3) / 2 * float(width)
         elif shape in ["圆形", "矩形"]:
            draw = float(width)
         if draw_height == 0:
            draw_height = draw
            # 起始位置的坐标
            start_x = -car_width / 2
            start_y = (-car_height / 2 + float(draw_height) / 4 + float(height_now) / 2)
            # 将画笔移到初始点
            turtle.penup()
            turtle.pensize(1)
            turtle.goto(start_x, start_y)
            turtle.speed(100)
            turtle.pendown()
            turtle.seth(0)
         else:
            now_height = draw
            diff = now_height - draw_height
            draw_height = now_height
            turtle.pu()
            turtle.seth(90)
            turtle.fd(diff / 4)
            turtle.seth(0)
            turtle.pd()
         if shape == "六边形":
            side = float(width) / 4
            for k in range(quantity):
               draw_hexagon(side, turtle, j[0], j[2], j[9])
               turtle.pu()
               turtle.fd(2 * side)
               turtle.pd()
         elif shape == "圆形":
            r = float(width) / 4
            for k in range(quantity):
               draw_circle(r, turtle, j[0], j[2], j[9])
               turtle.pu()
               turtle.fd(2 * r)
               turtle.pd()
         elif shape == "矩形":
            side = float(width) / 2
            for k in range(quantity):
               draw_rectangle(side, turtle, j[0], j[2], j[9])
               turtle.pu()
               turtle.fd(side)
               turtle.pd()
      distance(floor_left_width / 2, turtle)
      height_now += floor_height
   t.done()
   # ts = t.getscreen()
   # ts.getcanvas().postscript(file='abc.eps')
   # turtle.done()
