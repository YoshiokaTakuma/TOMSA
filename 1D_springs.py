import numpy as np
import pandas as pd

# データの読み込み
node = pd.read_csv('node.csv')
spring = pd.read_csv('spring.csv')

print('節点の情報')
print(node, '\n')
print('ばねの情報')
print(spring, '\n')

# よく使う定数と配列の定義
martix_size = node.ix[:, 0].size
spring_number = spring.ix[:, 0].size
k = spring.ix[:, 'constant']

# 支持条件を読み込んで、方程式IDと節点の順番を結びつけて辞書に登録
free = []
for i in list(range(martix_size)):
    if node.ix[i,2] == 'free':
        free.append(node.ix[i,0])

fix = []
for i in list(range(martix_size)):
    if node.ix[i,2] == 'fix':
        fix.append(node.ix[i,0])

point_order = free + fix    
eq_id = list(range(1, len(point_order) +1))
dic = dict(zip(point_order, eq_id))


# 剛体マトリクスの生成
# 節点数の大きさの０行列
matrix = np.zeros((martix_size, martix_size))

# バネ定数を方程式IDの該当箇所に加算
for spring_id in list(range(spring_number)):
    for point_id in list(range(martix_size)):
        element_matrix = np.zeros((martix_size, martix_size))
        if spring.ix[spring_id, 'Point1'] == point_id+1:
            for i in list(range(1, 3)):
                for j in list(range(1, 3)):
                    if i == j:
                        element_matrix[dic[spring.ix[spring_id, i]]-1, dic[spring.ix[spring_id, j]]-1] = k[spring_id]
                    else:
                        element_matrix[dic[spring.ix[spring_id, i]]-1, dic[spring.ix[spring_id, j]]-1] = -k[spring_id]
        matrix = matrix + element_matrix

print('変形後の全体剛性マトリクス')
print(matrix, '\n') 

# マトリクスのうち、必要な部分を抽出
part_matrix = matrix[0:len(free), 0:len(free)]
print('抽出後のマトリクス')
print(part_matrix, '\n')

# 支持条件='free'の力ベクトルを抽出
force = []
for i in list(range(martix_size)):
    if node.ix[i, 'support'] == 'free':
        force.append(node.ix[i, 'force'])
force = np.array(force)


# 連立方程式を解く
x = np.linalg.solve(part_matrix, force)

# 結果出力
print('結果（変位）')
count_fix = 0
for i in list(range(martix_size)):
    if node.ix[i, 'support'] == 'fix':
        count_fix = count_fix + 1
        print('u', node.ix[i,'Point_ID'], '= 0.0')        
    elif node.ix[i, 'support'] == 'free':
        print('u', node.ix[i,'Point_ID'], '=', x[i - count_fix])
