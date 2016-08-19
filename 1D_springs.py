import numpy as np
import pandas as pd

# データの読み込み
node = pd.read_csv('node.csv')
spring = pd.read_csv('spring.csv')

print(node)
print(spring)

# 各節点にかかる力
force = np.array(node.ix[:,3])

# 各ばねのばね定数
k = spring.ix[:, 3]

# 剛性マトリクス
stmx = np.zeros((len(node.ix[:, 0]),len(node.ix[:, 0])))
size = node.ix[:,0].size
i = 0

for i in list(range(size)):
    if i == 0:
        stmx[0, 0] = k[0]
        stmx[0, 1] = k[0] * (-1)

    elif i == size - 1:
        stmx[i, i-1] = k[i-1] * (-1)
        stmx[i, i] = k[i-1]

    else:
        stmx[i, i-1] = k[i-1] * (-1)
        stmx[i, i] = k[i-1] + k[i]
        stmx[i, i+1] = k[i] * (-1)

# 支持条件を読み込んで、固定→計算から削除
# Kaaの抽出しかしてない→固定の支持条件しか計算できない
i = 0
fix = 1
for i in list(range(node.ix[:,2].size)):
    if node.ix[i,2] == 'fix':
        stmx = np.delete(stmx, i, 0)
        stmx = np.delete(stmx, i, 1)
        force = np.delete(force, i, 0)
        print('u', i + 1, '= 0.0')
        fix = fix + 1
    else:
        pass
    i = i + 1

# 連立方程式を解く
x = np.linalg.solve(stmx, force)

i = 0
for i in list(range(force.size)):
    print('u', i + fix,'=', x[i])
