# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import os
import io
# import StringIO
from io import StringIO
from flask import Flask, render_template

app = Flask(__name__)
app.debug = True

@app.route('/')
def twoDmatrix():

    # データの読み込み
    node = pd.read_csv('node.csv')
    spring = pd.read_csv('spring.csv')

    # よく使う定数と配列の定義
    node_number = node.ix[:, 0]
    matrix_size = len(node_number)
    spring_number = spring.ix[:, 0]
    k = spring.ix[:, 'constant']

    # ばねの角度の計算
    spring_deg = []
    for i in spring_number - 1:
        x1 = node.ix[spring.ix[i,1]-1, 1]
        x2 = node.ix[spring.ix[i,2]-1, 1]
        y1 = node.ix[spring.ix[i,1]-1, 2]
        y2 = node.ix[spring.ix[i,2]-1, 2]
        
        if x2 - x1 ==0:
            degree = 90
        else:
            slope = (y2 - y1)/(x2 - x1)
            degree = np.rad2deg(np.arctan(slope))

        spring_deg.append(degree)
    spring['degree'] = spring_deg

    # 支持条件を読み込んで、方程式IDと節点の順番を結びつけて辞書に登録
    free = []
    fix = []
    for i in node_number - 1:
        if node.ix[i,3] == 'free':
            free.append(str(node.ix[i,0]) + 'x')
            free.append(str(node.ix[i,0]) + 'y')
        elif node.ix[i,3] == 'fix':
            fix.append(str(node.ix[i,0]) + 'x')
            fix.append(str(node.ix[i,0]) + 'y')

    point_order = free + fix    
    eq_id = list(range(1, len(point_order) +1))
    dic = dict(zip(point_order, eq_id))

    # ここから剛体マトリクスの生成
    # 節点数の大きさの０行列
    matrix = np.zeros((matrix_size * 2, matrix_size * 2))

    # 基本部材→座標変換部材→対応箇所に加算して全体剛性マトリクスの作成
    for spring_id in spring_number - 1:    
        # 座標変換マトリクスの作成
        sin = np.around(np.sin(np.deg2rad(spring.ix[spring_id, 'degree'])), decimals=3)
        cos = np.around(np.cos(np.deg2rad(spring.ix[spring_id, 'degree'])), decimals=3)
        trans = np.array([[cos, sin, 0, 0],
                        [-1 * sin, cos, 0, 0],
                        [0, 0, cos, sin],
                        [0, 0, -1 * sin, cos]])

        for point_id in node_number - 1:
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


    # マトリクスのうち、必要な部分を抽出
    part_matrix = matrix[0:len(free), 0:len(free)]

    # 支持条件='free'の力ベクトルを抽出
    force = []
    for i in node_number - 1:
        if node.ix[i, 'support'] == 'free':
            force.append(node.ix[i, 'forceX'])
            force.append(node.ix[i, 'forceY'])
    force = np.array(force)

    # 逆行列がゼロ→構造的に不安定
    if np.linalg.det(part_matrix) == 0:
        print('マトリクスの逆行列＝０、構造物が不安定')

    # 連立方程式を解く
    else:
        u = np.linalg.solve(part_matrix, force)

        # 座標表示
        # グラフ出力のため、新しいリストを定義
        xnewpoint = []
        ynewpoint = []
        xpoint = []
        ypoint = []
        pointlist = []

        for i in fix:
            if 'x' in i:
                i = int(i.replace('x', ''))
                x = node.ix[i-1, 'CorrdiX']
                xpoint.append(node.ix[i-1, 'CorrdiX'])
                xnewpoint.append(x)
            
            elif 'y' in i:
                i = int(i.replace('y', ''))
                y = node.ix[i-1, 'CorrdiY']
                ypoint.append(node.ix[i-1, 'CorrdiY'])
                ynewpoint.append(y)
                pointlist.append(i)

        j = 0
        for i in free:
            if 'x' in i:
                i = int(i.replace('x', ''))
                x = node.ix[i-1, 'CorrdiX'] + u[j]
                xpoint.append(node.ix[i-1, 'CorrdiX'])
                xnewpoint.append(x)
                j = j + 1
            elif 'y' in i:
                i = int(i.replace('y', ''))
                y = node.ix[i-1, 'CorrdiY'] + u[j]
                ypoint.append(node.ix[i-1, 'CorrdiY'])
                ynewpoint.append(y)
                j = j + 1
                pointlist.append(i)

    # 結果のデータフレーム
    node_resluts = pd.DataFrame(
        {'Point_ID': pointlist,
        'New CorrdiX': xnewpoint,
        'New CorrdiY': ynewpoint},
        columns = ['Point_ID', 'New CorrdiX', 'New CorrdiY'])
    node_resluts = node_resluts.sort_values('Point_ID')
    node_resluts['support'] = node.ix[:, 'support']

    # 支持反力
    reaction_force = matrix[len(free):matrix_size * 2, 0:len(free)].dot(np.linalg.inv(part_matrix)).dot(force)


    # ばねにかかる力を計算して、プロットする
    fig = plt.figure()
    sns.set_style('whitegrid')
    for i in spring_number - 1:
        # ばねの伸びから、変形後に掛かる力を計算
        # 変形前のばねの長さ
        dx = node.ix[spring.ix[i, 'Point2']-1, 'CorrdiX'] - node.ix[spring.ix[i, 'Point1']-1, 'CorrdiX']
        dy = node.ix[spring.ix[i, 'Point2']-1, 'CorrdiY'] - node.ix[spring.ix[i, 'Point1']-1, 'CorrdiY']
        primary_length = np.sqrt(dx*dx + dy*dy)

        # 変形後のばねの長さ
        newdx = node_resluts.ix[spring.ix[i, 'Point2']-1, 'New CorrdiX'] - node_resluts.ix[spring.ix[i, 'Point1']-1, 'New CorrdiX']
        newdy = node_resluts.ix[spring.ix[i, 'Point2']-1, 'New CorrdiY'] - node_resluts.ix[spring.ix[i, 'Point1']-1, 'New CorrdiY']
        after_length = np.sqrt(newdx*newdx + newdy*newdy)

        # フックの法則より力をもとめる
        dif_length = after_length - primary_length
        spring_force = spring.ix[i, 'constant'] * dif_length
        
        # プロットに表示
        if spring_force != 0:
            text_plot_x = (node.ix[spring.ix[i, 'Point2']-1, 'CorrdiX'] + node.ix[spring.ix[i, 'Point1']-1, 'CorrdiX'])/2
            text_plot_y = (node.ix[spring.ix[i, 'Point2']-1, 'CorrdiY'] + node.ix[spring.ix[i, 'Point1']-1, 'CorrdiY'])/2
            plt.text(text_plot_x, text_plot_y, np.around(spring_force, decimals=3))
        
        # ばねの線表示
        # 伸びてたら赤線、縮んでたら青線、変化なしは黒線
        plt.plot([node.ix[spring.ix[i, 'Point1']-1, 'CorrdiX'], node.ix[spring.ix[i, 'Point2']-1, 'CorrdiX']], 
                [node.ix[spring.ix[i, 'Point1']-1, 'CorrdiY'], node.ix[spring.ix[i, 'Point2']-1, 'CorrdiY']],':k')
        
        x1 = node_resluts.ix[spring.ix[i, 'Point1']-1, 'New CorrdiX']
        x2 = node_resluts.ix[spring.ix[i, 'Point2']-1, 'New CorrdiX']
        y1 = node_resluts.ix[spring.ix[i, 'Point1']-1, 'New CorrdiY']
        y2 = node_resluts.ix[spring.ix[i, 'Point2']-1, 'New CorrdiY']
        
        if spring_force == 0:
            unchanged, = plt.plot([x1, x2], [y1, y2], 'k',  lw = 2)
        elif spring_force > 0:
            extended, = plt.plot([x1, x2], [y1, y2], 'r',  lw = 2)
        elif spring_force < 0:
            shrunk, = plt.plot([x1, x2], [y1, y2], 'b',  lw = 2)
            
    for i in node_number - 1:
        # 力のベクトル
        if node.ix[i, 'forceX'] != 0 or node.ix[i, 'forceY'] != 0:
            ExternalForce = plt.quiver(node.ix[i, 'CorrdiX'], node.ix[i, 'CorrdiY'], 
                                    node.ix[i, 'forceX'], node.ix[i, 'forceY'],angles='xy',scale_units='xy',scale=1)
            plt.text(node.ix[i, 'CorrdiX'], node.ix[i, 'CorrdiY'] * 1.02, 
                    '(' + str(node.ix[i, 'forceX']) + ',' + str(node.ix[i, 'forceY']) + ')')
            
        # 変形前、変形後のプロット
        # 固定されている場合は☓をプロットする
        if node_resluts.ix[i, 'support'] == 'free':
            Before = plt.scatter(xpoint[i],ypoint[i], c = 'white', s = 75, marker = 'o')
            After = plt.scatter(xnewpoint[i],ynewpoint[i], c = 'white', s = 75, marker = 's')
            
        elif node_resluts.ix[i, 'support'] == 'fix':
            Fix = plt.scatter(xpoint[i],ypoint[i], s = 100, marker = 'x', c = 'k', lw = 3)
            ReactionForce = plt.quiver(node.ix[i, 'CorrdiX'], node.ix[i, 'CorrdiY'], 
                                        reaction_force[2 * i], reaction_force[2 * i + 1],angles='xy' ,scale_units='xy', color = 'gray', scale=1)
            
            if node.ix[i, 'CorrdiY'] == 0:
                plt.text(node.ix[i, 'CorrdiX'] + 0.25, node.ix[i, 'CorrdiY'] - 0.75, 
                        '(' + str(reaction_force[2 * i]) + ',' + str(reaction_force[2 * i + 1]) + ')')
            else:
                plt.text(node.ix[i, 'CorrdiX'], node.ix[i, 'CorrdiY'] * 1.02, 
                        '(' + str(reaction_force[2 * i]) + ',' + str(reaction_force[2 * i + 1]) + ')')

                
    # 支持反力ベクトルの表示

        

    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend([Fix, Before, After, ExternalForce, ReactionForce, unchanged, extended, shrunk], 
            ['Fix', 'Before', 'After', 'External Force', 'Reaction Force', 'unchanged', 'extended', 'shrunk'], 
            bbox_to_anchor=(1.4, 0.7), frameon = True)
    # 右側の余白を調整
    plt.subplots_adjust(right=0.7)

    strio = io.StringIO()
    fig.savefig(strio, format='svg')
    plt.close(fig)

    strio.seek(0)
    strio.buf = strio.getvalue()
    svgstr = strio.buf[strio.buf.find('<svg'):]

    return render_template('index.html', svgstr=svgstr)

if __name__ == '__main__':
    app.run()