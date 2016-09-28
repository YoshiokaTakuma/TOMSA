#!/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

import os
import io
# import StringIO
from io import StringIO
from flask import Flask, render_template, request
import json

from app import node_data
from app import spring_data
'''
node = pd.read_csv('node.csv')
spring = pd.read_csv('spring.csv')
'''

def main():
    # よく使う定数と配列の定義
    global node, node_number, matrix_size, spring, spring_number, k
    node = node_data()
    node_number = node.ix[:, 0]
    matrix_size = len(node_number)

    spring = spring_data()
    spring_number = spring.ix[:, 0]
    k = spring.ix[:, 'constant']
    spring['degree'] = [cal_spring_degree(i) for i in spring_number - 1]
    
    # 節点IDと方程式IDを格納した辞書作成
    node_id2eq_id()
    # マトリクス生成、計算実行
    cal()
    # 結果整理
    results()
    # プロット
    plot()
    
    return svgstr
    
def make_dataframe():
    index = all_data.find('][')
    node = pd.DataFrame(eval(all_data[0:index + 1]))
    node['Point_ID'] = np.array(range(len(node))) + 1
    node.columns = ['CorrdiX', 'CorrdiY', 'support', 'forceX', 'forceY', 'Point_ID']
    node = node.ix[:,['Point_ID', 'CorrdiX', 'CorrdiY', 'support', 'forceX', 'forceY']]

    spring = pd.DataFrame(eval(all_data[index+1:]))
    spring['Spring_No'] = np.array(range(len(spring))) + 1
    spring.columns = ['Point1', 'Point2', 'constant', 'Spring_No']
    spring = spring.ix[:, ['Spring_No', 'Point1', 'Point2', 'constant']]

    return
    
    
def cal_spring_degree(sp):
    x1 = node.ix[spring.ix[sp,1]-1, 1]
    x2 = node.ix[spring.ix[sp,2]-1, 1]
    y1 = node.ix[spring.ix[sp,1]-1, 2]
    y2 = node.ix[spring.ix[sp,2]-1, 2]
    
    if x2 - x1 ==0:
        degree = 90
    else:
        slope = (y2 - y1)/(x2 - x1)
        degree = np.rad2deg(np.arctan(slope))
    
    return degree

def node_id2eq_id():
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
    
    global dic
    dic = dict(zip(point_order, eq_id))
    
    return

# 基本部材→座標変換部材→対応箇所に加算して全体剛性マトリクスの作成
def local_matrix(sp):
    
    local = np.zeros((4, 4))
    for n in [0, 2]:
        for m in [0, 2]:
            if n == m:
                local[n, m] = k[sp]
            else:
                local[n, m] = -k[sp]

    sin = np.around(np.sin(np.deg2rad(spring.ix[sp, 'degree'])), decimals=3)
    cos = np.around(np.cos(np.deg2rad(spring.ix[sp, 'degree'])), decimals=3)
    trans = np.array([[cos, sin, 0, 0],
                      [-1 * sin, cos, 0, 0],
                      [0, 0, cos, sin],
                      [0, 0, -1 * sin, cos]])    
    global_element = np.linalg.inv(trans).dot(local).dot(trans)
    
    return global_element

def element_matrix(sp, cl, rw):
    element_matrix = np.zeros((matrix_size * 2, matrix_size * 2))
    # 座標変換部材マトリクスの０ではない要素を読み込み、辞書keyと関連付ける
    # もっと賢いやり方があるはず!!!
    if cl == 0:
        column = str(int(spring.ix[sp, 'Point1'])) + 'x'
    elif cl == 1:
        column = str(int(spring.ix[sp, 'Point1'])) + 'y'
    elif cl == 2:
        column = str(int(spring.ix[sp, 'Point2'])) + 'x'
    elif cl == 3:
        column = str(int(spring.ix[sp, 'Point2'])) + 'y'

    if rw == 0:
        row = str(int(spring.ix[sp, 'Point1'])) + 'x'
    elif rw == 1:
        row = str(int(spring.ix[sp, 'Point1'])) + 'y'
    elif rw == 2:
        row = str(int(spring.ix[sp, 'Point2'])) + 'x'
    elif rw == 3:
        row = str(int(spring.ix[sp, 'Point2'])) + 'y'
    
    element_matrix[dic[column]-1, dic[row]-1] = local_matrix(sp)[cl, rw]
    
    return element_matrix
    

def total_matrix():
    # 剛性マトリクス生成
    matrix = np.zeros((matrix_size * 2, matrix_size * 2))
    for i in spring_number - 1:
        for n in list(range(4)):
            for m in list(range(4)):
                if local_matrix(i)[n, m] != 0:
                    matrix = matrix + element_matrix(i, n, m)
    
    return matrix

def cal():
    size = list(node.ix[:, 'support']).count('free') * 2
    part_matrix = total_matrix()[0:size, 0:size]

    part_force = []
    for i in node_number - 1:
        if node.ix[i, 'support'] == 'free':
            part_force.append(node.ix[i, 'forceX'])
            part_force.append(node.ix[i, 'forceY'])
    part_force = np.array(part_force)
    

    if np.linalg.det(part_matrix) == 0:
        return 'マトリクスの逆行列＝０、構造物が不安定'
        sys.exit()
        

    else:
        global u
        u = np.linalg.solve(part_matrix, part_force)
        # 支持反力
        global reaction_force
        reaction_force = total_matrix()[size:matrix_size * 2, 0:size].dot(np.linalg.inv(part_matrix)).dot(part_force)

        return
    

def results():
    xnewpoint = []
    ynewpoint = []
    pointlist = []
    
    j = 0
    for i in node_number - 1:
        pointlist.append(i + 1)
        if node.ix[i,3] == 'fix':
            xnewpoint.append(node.ix[i, 'CorrdiX'])
            ynewpoint.append(node.ix[i, 'CorrdiY'])
        elif node.ix[i,3] == 'free':
            xnewpoint.append(node.ix[i, 'CorrdiX'] + u[j])
            j = j +1
            ynewpoint.append(node.ix[i, 'CorrdiY'] + u[j])
            j = j +1
    
    global node_results
    node_results = pd.DataFrame({'Point_ID': pointlist,
                                 'New CorrdiX': xnewpoint,
                                 'New CorrdiY': ynewpoint},
                                columns = ['Point_ID', 'New CorrdiX', 'New CorrdiY'])
    node_results = node_results.sort_values('Point_ID').reset_index(drop=True)
    node_results['support'] = node.ix[:, 'support']
    
    return

def spring_force(sp):
    dx = node.ix[spring.ix[sp, 'Point2']-1, 'CorrdiX'] - node.ix[spring.ix[sp, 'Point1']-1, 'CorrdiX']
    dy = node.ix[spring.ix[sp, 'Point2']-1, 'CorrdiY'] - node.ix[spring.ix[sp, 'Point1']-1, 'CorrdiY']
    primary_length = np.sqrt(dx*dx + dy*dy)

    # 変形後のばねの長さ
    newdx = node_results.ix[spring.ix[sp, 'Point2']-1, 'New CorrdiX'] - node_results.ix[spring.ix[sp, 'Point1']-1, 'New CorrdiX']
    newdy = node_results.ix[spring.ix[sp, 'Point2']-1, 'New CorrdiY'] - node_results.ix[spring.ix[sp, 'Point1']-1, 'New CorrdiY']
    after_length = np.sqrt(newdx*newdx + newdy*newdy)
    

    dif_length = after_length - primary_length
    spring_force = spring.ix[sp, 'constant'] * dif_length
    
    return spring_force

def plot_springs(sp):

    # プロットに表示
    spf = spring_force(sp)

    # 伸びてたら赤線、縮んでたら青線、変化なしは黒線
    plt.plot([node.ix[spring.ix[sp, 'Point1']-1, 'CorrdiX'], node.ix[spring.ix[sp, 'Point2']-1, 'CorrdiX']], 
             [node.ix[spring.ix[sp, 'Point1']-1, 'CorrdiY'], node.ix[spring.ix[sp, 'Point2']-1, 'CorrdiY']],':k')
    
    x1 = node_results.ix[spring.ix[sp, 'Point1']-1, 'New CorrdiX']
    x2 = node_results.ix[spring.ix[sp, 'Point2']-1, 'New CorrdiX']
    y1 = node_results.ix[spring.ix[sp, 'Point1']-1, 'New CorrdiY']
    y2 = node_results.ix[spring.ix[sp, 'Point2']-1, 'New CorrdiY']
    

    if spf == 0:
        plt.plot([x1, x2], [y1, y2], color = [0.5, 0.0, 0.5],  lw = 2)
    elif spf > 0:
        plt.plot([x1, x2], [y1, y2], color = [0.5 + (spf/max_color) / 2, 0.0, 0.5 - (spf/max_color) / 2], lw = 2)
    elif spf < 0:
        plt.plot([x1, x2], [y1, y2], color = [0.5 - (-spf/max_color) / 2, 0.0, 0.5 + (-spf/max_color) / 2],  lw = 2)
    
    return

j = 0
def plot_node(nd, cnt):
    global Fix, Before, After, ExternalForce, ReactionForce

    # 力のベクトル
    if node.ix[nd, 'forceX'] != 0 or node.ix[nd, 'forceY'] != 0:
        ExternalForce = plt.quiver(node.ix[nd, 'CorrdiX'], node.ix[nd, 'CorrdiY'], 
                                   node.ix[nd, 'forceX'], node.ix[nd, 'forceY'],angles='xy',scale_units='xy',scale=1)
        plt.text(node.ix[nd, 'CorrdiX'], node.ix[nd, 'CorrdiY'] * 1.02, 
                 '(' + str(node.ix[nd, 'forceX']) + ',' + str(node.ix[nd, 'forceY']) + ')')
        plt.plot(node.ix[nd, 'CorrdiX'] + node.ix[nd, 'forceX'], node.ix[nd, 'CorrdiY'] + node.ix[nd, 'forceY'], marker = '')

    # 変形前、変形後のプロット
    # 固定されている場合は☓をプロットする
    if node_results.ix[nd, 'support'] == 'free':
        Before = plt.scatter(node.ix[nd, 'CorrdiX'], node.ix[nd, 'CorrdiY'], c = 'white', s = 75, marker = 'o')
        After = plt.scatter(node_results.ix[nd, 'New CorrdiX'], node_results.ix[nd, 'New CorrdiY'], c = 'white', s = 75, marker = 's')
        
    elif node_results.ix[nd, 'support'] == 'fix':
        Fix = plt.scatter(node_results.ix[nd, 'New CorrdiX'], node_results.ix[nd, 'New CorrdiY'], s = 100, marker = 'x', c = 'k', lw = 3)
        ReactionForce = plt.quiver(node.ix[nd, 'CorrdiX'], node.ix[nd, 'CorrdiY'], 
                                    reaction_force[2 * cnt], reaction_force[2 * cnt + 1],angles='xy' ,scale_units='xy', color = 'gray', scale=1)
        plt.plot(node.ix[nd, 'CorrdiX'] + reaction_force[2 * cnt], node.ix[nd, 'CorrdiY'] + reaction_force[2 * cnt + 1], marker = '')


        if node.ix[nd, 'CorrdiY'] == min(node.ix[:, 'CorrdiY']):
            plt.text(node.ix[nd, 'CorrdiX'] - max(node.ix[:, 'CorrdiY'])*0.1, node.ix[nd, 'CorrdiY'] - max(node.ix[:, 'CorrdiY'])*0.1, 
                     '(' + str(np.around(reaction_force[2 * cnt], decimals=3)) + ',' + str(np.around(reaction_force[2 * cnt + 1], decimals=3)) + ')', va = 'top', ha = 'center')
            
        else:
            plt.text(node.ix[nd, 'CorrdiX'], node.ix[nd, 'CorrdiY'] * 1.02, 
                     '(' + str(np.around(reaction_force[2 * cnt], decimals=3)) + ',' + str(np.around(reaction_force[2 * cnt + 1], decimals=3)) + ')')
        
    return

def color_list():
    color_list = [spring_force(i) for i in spring_number - 1]
    
    global max_color
    max_color = max(np.absolute(color_list))

    return
            
def plot():
    fig = plt.figure()
    sns.set_style('whitegrid')
    plt.clf()
    color_list()
    for i in spring_number - 1:
        plot_springs(i)
    
    j = 0
    for i in node_number - 1:
        plot_node(i, j)
        if node_results.ix[i, 'support'] == 'fix':
            j = j + 1
    
    title, = plt.plot([0, 0], [0, 0], 'w')
    redmax, = plt.plot([0, 0], [0, 0], 'r')
    purplezero, = plt.plot([0, 0], [0, 0], color = [0.5, 0.0, 0.5])
    bluemax, = plt.plot([0, 0], [0, 0], 'b')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.axis('equal')
    plt.legend([Fix, Before, After, ExternalForce, ReactionForce, title, redmax, purplezero, bluemax], 
               ['Fix', 'Before', 'After', 'External Force', 'Reaction Force', 'Spring Force',
               np.around(max_color, decimals=2), '0.0', np.around(max_color, decimals=2) * (-1)], 
               bbox_to_anchor=(1.4, 0.7), frameon = True)
    # 右側の余白を調整
    plt.subplots_adjust(right=0.7)
    
    strio = io.StringIO()
    fig.savefig(strio, format='svg')
    plt.close(fig)
    strio.seek(0)
    strio.buf = strio.getvalue()
    global svgstr
    svgstr = strio.buf[strio.buf.find('<svg'):]
    
    return 
    
if __name__ == "__main__":
    main()