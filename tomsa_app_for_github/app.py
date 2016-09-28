#!/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import os
import io
from io import StringIO
from flask import Flask, render_template, request, g ,send_from_directory
import json

app = Flask(__name__)
app.debug = True

@app.route('/')
def table():
    return render_template('index.html')


@app.route('/post', methods=['POST'])
def post():
    
    all_data = request.json
    if 'null' in all_data:
        return 'データを入力してください'
        sys.exit()
    else:
        pass
    data(all_data)

    
    table = 'table_data'
    with open("tmp/" + table, 'w') as f:
        f.write(str(g.node_raw))


    import matrix_analysis as ma
    svgstr = ma.main()

    return svgstr

def data(jsondata):
    index = jsondata.find('][')
    g.node_raw = eval(jsondata[0:index + 1])
    g.node_data = pd.DataFrame(g.node_raw)
    g.node_data['Point_ID'] = np.array(range(len(g.node_data))) + 1
    g.node_data.columns = ['CorrdiX', 'CorrdiY', 'support', 'forceX', 'forceY', 'Point_ID']
    g.node_data = g.node_data.ix[:,['Point_ID', 'CorrdiX', 'CorrdiY', 'support', 'forceX', 'forceY']]

    g.spring_data = pd.DataFrame(eval(jsondata[index+1:]))
    g.spring_data['Spring_No'] = np.array(range(len(g.spring_data))) + 1
    g.spring_data.columns = ['Point1', 'Point2', 'constant', 'Spring_No']
    g.spring_data = g.spring_data.ix[:, ['Spring_No', 'Point1', 'Point2', 'constant']]

def node_data():
    return g.node_data

def spring_data():
    return g.spring_data


@app.route('/tmp/<path:table>')
def down(table):
    t = open("tmp/" +table)
    data3 = t.read()
    data3 = data3.replace('\'','"' )
    return data3


if __name__ == '__main__':
    app.run()