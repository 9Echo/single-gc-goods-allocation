from pulp import *
import numpy as np

prob = LpProblem('优化问题', LpMaximize)
volume = [10000, 34, 22, 22, 34]
one_weight = [1.067, 0.751, 1.488, 0.641, 0.815]
order_j = [50, 40, 40, 40, 30]
max_weight = 33
max_volume = 1.18
# 变量定义，注意最后的LpInteger，当设置该参数时，则该决策变量只能取整数
# 如果决策变量可以取小数，那就设置为LpContinuous
# 决策变量   车次*品种数的矩阵
x0 = np.ones((6, 5))
row = len(x0)
col = len(x0[0])
x = [[pulp.LpVariable(f'x{i}{j}', lowBound=0, cat=pulp.LpInteger) for j in range(col)] for i in range(row)]
# 需要优化的表达式
# prob += 600 * x1 + 800 * x2 + 500 * x3 + 400 * x4 + 300 * x5

prob += (max_weight - pulp.lpDot(one_weight, x[0])) + (max_weight - pulp.lpDot(one_weight, x[1])) + (
        max_weight - pulp.lpDot(one_weight, x[2])) + (max_weight - pulp.lpDot(one_weight, x[3])) + (
                max_weight - pulp.lpDot(one_weight, x[4])) + (
                max_weight - pulp.lpDot(one_weight, x[5]))
# 约束条件
for i in range(len(order_j)):
    temp = 0
    for j in range(6):
        temp += x[j][i]
    prob += temp == order_j[i]
for i in range(6):
    prob += pulp.lpDot(x[i], one_weight) <= max_weight
    prob += pulp.lpDot(x[i], volume) <= max_volume



# lp文件保存该优化问题的信息
# prob.writeLP("优化问题.lp")

# 执行计算
prob.solve()

# 如果成功得到了最优值，则会输出 Optimal
print(LpStatus[prob.status])

# 得到最优值时，各决策变量的取值，如果没有找到最优值，则输出None
for v in prob.variables():
    print(v.name, "=", v.varValue)

# 输出最优值，如果没有找到最优值，则输出None
print("min", value(prob.objective))
