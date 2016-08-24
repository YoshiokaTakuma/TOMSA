import numpy as np
import pandas as pd
import math

# データの読み込み
node = pd.read_csv('node.csv')
spring = pd.read_csv('spring.csv')

print('節点の情報')
print(node, '\n')


# よく使う定数と配列の定義
matrix_size = node.ix[:, 0].size
spring_number = spring.ix[:, 0].size
k = spring.ix[:, 'constant']

# ばねの角度の計算
spring_deg = []
for i in list(range(spring_number)):
    x1 = node.ix[spring.ix[i,1]-1, 1]
    x2 = node.ix[spring.ix[i,2]-1, 1]
    y1 = node.ix[spring.ix[i,1]-1, 2]
    y2 = node.ix[spring.ix[i,2]-1, 2]
    
    rad = (y2 - y1)/(x2 - x1)
    spring_deg.append(np.rad2deg(np.arctan(rad)))
spring['degree'] = spring_deg

print('ばねの情報')
print(spring, '\n')

# 支持条件を読み込んで、方程式IDと節点の順番を結びつけて辞書に登録
free = []
for i in list(range(matrix_size)):
    if node.ix[i,3] == 'free':
        free.append(str(node.ix[i,0]) + 'x')
        free.append(str(node.ix[i,0]) + 'y')

fix = []
for i in list(range(matrix_size)):
    if node.ix[i,3] == 'fix':
        free.append(str(node.ix[i,0]) + 'x')
        free.append(str(node.ix[i,0]) + 'y')

point_order = free + fix    
eq_id = list(range(1, len(point_order) +1))
dic = dict(zip(point_order, eq_id))
print(dic)

# 剛体マトリクスの生成



# 節点数の大きさの０行列
matrix = np.zeros((matrix_size * 2, matrix_size * 2))

# 基本部材→座標変換部材→対応箇所に加算して全体剛性マトリクスの作成
for spring_id in list(range(spring_number)):
    # 座標変換マトリクスの作成
    sin = np.around(np.sin(np.deg2rad(spring.ix[spring_id, 'degree'])), decimals=3)
    cos = np.around(np.cos(np.deg2rad(spring.ix[spring_id, 'degree'])), decimals=3)
    trans = np.array([[cos, sin, 0, 0],
                      [-1 * sin, cos, 0, 0],
                      [0, 0, cos, sin],
                      [0, 0, -1 * sin, cos]])
    inv_trans = np.linalg.inv(trans)
    
    for point_id in list(range(matrix_size)):
        
        # 基本部材マトリクスの作成
        local = np.zeros((4, 4))
        if spring.ix[spring_id, 'Point1'] == point_id+1:
            for i in [0, 2]:
                for j in [0, 2]:
                    if i == j:
                        local[i, j] = k[spring_id]
                    else:
                        local[i, j] = -k[spring_id]
            # 座標変換部材マトリクスの作成
            element_matrix = inv_trans.dot(local).dot(trans)
            print(element_matrix, '\n')

