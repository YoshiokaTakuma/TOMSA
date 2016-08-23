import numpy as np
import pandas as pd

# データの読み込み
node = pd.read_csv('node.csv')
spring = pd.read_csv('spring.csv')
size = node.ix[:, 0].size

# SpringのデータをPoint1順にソート
# Point1_ID < Point2_ID に統一
P1 = []
P2 = []
for i in list(range(spring.ix[:, 0].size)):
    if spring.ix[i, 'Point1'] > spring.ix[i, 'Point2']:
        P1.append(spring.ix[i, 'Point2'])
        P2.append(spring.ix[i, 'Point1'])
    else:
        P1.append(spring.ix[i, 'Point1'])
        P2.append(spring.ix[i, 'Point2'])

spring2 = spring.drop(['Point1', 'Point2'], axis=1)

spring2['Point1'] = P1
spring2['Point2'] = P2
spring2 = spring2[['Spring_No','Point1', 'Point2', 'constant']]

spring2 = spring2.sort_values(by = ['Point1', 'Point2'])
# ソートしたデータフレームのindex番号を付け直す
spring2 = spring2.reset_index(drop=True)


# 各ばねのばね定数
k = spring2.ix[:, 'constant']

# 剛体マトリクスの生成
# 節点数の大きさの０行列
stmx = np.zeros((size, size))

# 部材剛性マトリクスを生成→全体マトリクスに足していく
# 部材剛性マトリクスをnずつずらして行くので、一直線のみに使える
for n in list(range(len(spring2.ix[:, 0]))):
    ele = np.zeros((size, size))
    for i in list(range(2)):
        for j in list(range(2)):
            if i == j:
                ele[i + n, j + n] = k[n]
            else:
                ele[i +n , j + n] = -k[n]
    stmx = stmx + ele

# 支持条件を読み込んで、Point_IDとEq_IDを結びつける
free = []
for i in list(range(size)):
    if node.ix[i,2] == 'free':
        free.append(node.ix[i,0])
    else:
        pass

fix = []
for i in list(range(size)):
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

print('節点の情報')
print(node_s, '\n')
print('ばねの情報')
print(spring2, '\n')


# マトリックスの列を、ソートしたPoint_ID順に新しい行列に入れていく
arr = np.empty((size, 0), int)
for i in list(range(size)):
    arr = np.hstack((arr, stmx[:, node_s.ix[i, 'Point_ID']-1].reshape(node_s.ix[:, 0].size, 1)))   

# 上で作った行列の行をさらに、PointID順にまた新しい行列にいれていく
arr2 = np.empty((0, size), int)
for i in list(range(size)):
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