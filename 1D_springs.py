import numpy as np
import pandas as pd

# データの読み込み
node = pd.read_csv('node.csv')
spring = pd.read_csv('spring.csv')
print(spring, '\n')

# 各ばねのばね定数
k = spring.ix[:, 'constant']


# 剛性マトリクス
# 現状だと一次元かつ、バネが順番に並んでいないと剛性マトリクスを正しく生成できない
stmx = np.zeros((len(node.ix[:, 0]),len(node.ix[:, 0])))
size = node.ix[:, 0].size

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
free = []
fix = []
for i in list(range(node.ix[:, 'support'].size)):
    if node.ix[i,2] == 'free':
        free.append(node.ix[i,0])
    else:
        pass

for i in list(range(node.ix[:, 'support'].size)):
    if node.ix[i,2] == 'fix':
        fix.append(node.ix[i,0])
    else:
        pass

pid = free + fix    
eqid = list(range(1, len(pid) +1))
dic = dict(zip(pid, eqid))

# nodeにEq_IDを追加して、Eq_ID順にソート
eqlist = []
for i in list(range(1, len(pid) +1)):
    eqlist.append(dic[i])
    
node['Eq_ID'] = eqlist
node_s = node.sort_values(by='Eq_ID')
# ソートしたデータフレームのindex番号を付け直す
node_s = node_s.reset_index(drop=True)
print(node_s, '\n')


# マトリックスの列を、ソートしたPoint_ID順に新しい行列に入れていく
arr = np.empty((3,0), int)
for i in list(range(node_s.ix[:, 0].size)):
    arr = np.hstack((arr, stmx[:, node_s.ix[i, 'Point_ID']-1].reshape(3, 1)))   

# 上で作った行列の行をさらに、PointID順にまた新しい行列にいれていく
arr2 = np.empty((0,3), int)
for i in list(range(node_s.ix[:, 0].size)):
    arr2 = np.vstack((arr2, arr[node_s.ix[i, 'Point_ID']-1, :]))
    
print('変形後の全体剛性マトリクス')
print(arr2, '\n') 

# マトリクスのうち、必要な部分を抽出
arr3 = arr2[0:len(free), 0:len(free)]
print('抽出後のマトリクス')
print(arr3, '\n')

# マトリクスに合わせて、力ベクトルを取得
force = np.array(node_s.ix[0:len(free)-1,'force'])

# 連立方程式を解く
x = np.linalg.solve(arr3, force)

for i in list(range(len(free),len(free) + len(fix))):
    print('u', node_s.ix[i,'Point_ID'], '= 0.0')
for i in list(range(force.size)):
    print('u', node_s.ix[i,'Point_ID'], '=', x[i])