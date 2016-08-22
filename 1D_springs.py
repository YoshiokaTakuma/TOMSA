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
# 現状だと一次元かつ、バネが順番に並んでいないと剛性マトリクスを正しく生成できない
stmx = np.zeros((len(node.ix[:, 0]),len(node.ix[:, 0])))
size = node.ix[:, 0].size
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
        
# 支持条件を読み込んで、Point_IDとEq_IDを結びつける
i = 0
free = []
fix = []
for i in list(range(node.ix[:,2].size)):
    if node.ix[i,2] == 'free':
        free.append(node.ix[i,0])
    else:
        pass

for i in list(range(node.ix[:,2].size)):
    if node.ix[i,2] == 'fix':
        fix.append(node.ix[i,0])
    else:
        pass

pid = free + fix    
eqid = list(range(1, len(pid) +1))
dic = dict(zip(pid, eqid))

eqlist = []
for i in list(range(1, len(pid) +1)):
    eqlist.append(dic[i])


node['Eq_ID'] = eqlist
node_s = node.sort_values(by='Eq_ID')
print(node_s)