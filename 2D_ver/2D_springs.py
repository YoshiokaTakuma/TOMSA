import numpy as np
import pandas as pd

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
    
    slope = (y2 - y1)/(x2 - x1)
    spring_deg.append(np.rad2deg(np.arctan(slope)))
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
        fix.append(str(node.ix[i,0]) + 'x')
        fix.append(str(node.ix[i,0]) + 'y')

point_order = free + fix    
eq_id = list(range(1, len(point_order) +1))
dic = dict(zip(point_order, eq_id))
# 結果表示のため逆引き辞書を作成
rev_dic = {v:k for k, v in dic.items()}


print('座標変換部材マトリクス')
# ここから剛体マトリクスの生成
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
            # 座標変換部材マトリクスへ変換
            trans_local = np.linalg.inv(trans).dot(local).dot(trans)
            print(trans_local, '\n')
            
            # 全体マトリクスの対応座標に加算していく
            # 座標変換部材マトリクスを全体マトリクスの大きさに拡張
            element_matrix = np.zeros((matrix_size * 2, matrix_size * 2))
            for i in list(range(4)):
                for j in list(range(4)):
                    if trans_local[i, j] != 0:
                        
                        # 座標変換部材マトリクスの０ではない要素を読み込み、辞書keyと関連付ける
                        # もっと賢いやり方があるはず!!!
                        if i == 0:
                            column = str(int(spring.ix[spring_id, 'Point1'])) + 'x'
                        elif i == 1:
                            column = str(int(spring.ix[spring_id, 'Point1'])) + 'y'
                        elif i == 2:
                            column = str(int(spring.ix[spring_id, 'Point2'])) + 'x'
                        elif i == 3:
                            column = str(int(spring.ix[spring_id, 'Point2'])) + 'y'

                        if j == 0:
                            row = str(int(spring.ix[spring_id, 'Point1'])) + 'x'
                        elif j == 1:
                            row = str(int(spring.ix[spring_id, 'Point1'])) + 'y'
                        elif j == 2:
                            row = str(int(spring.ix[spring_id, 'Point2'])) + 'x'
                        elif j == 3:
                            row = str(int(spring.ix[spring_id, 'Point2'])) + 'y'
                        
                        # 関連付けた辞書keyの位置に、読み込んだ要素を代入
                        element_matrix[dic[column]-1, dic[row]-1] = trans_local[i, j]
            
            # 全体マトリクスへ加算
            matrix = matrix + element_matrix

print('変形後の全体剛性マトリクス')
print(matrix, '\n') 

# マトリクスのうち、必要な部分を抽出
part_matrix = matrix[0:len(free), 0:len(free)]
print('抽出後のマトリクス')
print(part_matrix, '\n')

# 支持条件='free'の力ベクトルを抽出
force = []
for i in list(range(matrix_size)):
    if node.ix[i, 'support'] == 'free':
        force.append(node.ix[i, 'forceX'])
        force.append(node.ix[i, 'forceY'])
force = np.array(force)

# 逆行列がゼロになってしまうので、行と列どちらもすべて０の場合に削除
# この方法で正しいのか？？
count_del_eqid = []
for i in reversed(list(range(len(free)))):
    if np.all(part_matrix[:, i] == 0) and np.all(part_matrix[i, :] == 0):
        part_matrix = np.delete(part_matrix, i, 0)
        part_matrix = np.delete(part_matrix, i, 1)
        force = np.delete(force, i, 0)
        count_del_eqid.append(i)
count_del_eqid.reverse()

# 連立方程式を解く
x = np.linalg.solve(part_matrix, force)


# 結果出力
print('結果（変位）')

for i in fix:
    print('u' + str(i) + ' = 0.0')

i = 0
for j in free:
    if dic[j]-1 in count_del_eqid:
        print('u' + str(j) + ' = 0.0')
    else:
        print('u' + str(j) + ' = ' + str(x[i]))
        i = i + 1
        