#!/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import os
import io
from io import StringIO
from flask import Flask, render_template, request, g
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
    import matrix_analysis as ma
    svgstr = ma.main()
    return svgstr

def data(jsondata):
    index = jsondata.find('][')
    g.node = pd.DataFrame(eval(jsondata[0:index + 1]))
    g.node['Point_ID'] = np.array(range(len(g.node))) + 1
    g.node.columns = ['CorrdiX', 'CorrdiY', 'support', 'forceX', 'forceY', 'Point_ID']
    g.node = g.node.ix[:,['Point_ID', 'CorrdiX', 'CorrdiY', 'support', 'forceX', 'forceY']]

    g.spring = pd.DataFrame(eval(jsondata[index+1:]))
    g.spring['Spring_No'] = np.array(range(len(g.spring))) + 1
    g.spring.columns = ['Point1', 'Point2', 'constant', 'Spring_No']
    g.spring = g.spring.ix[:, ['Spring_No', 'Point1', 'Point2', 'constant']]

def node():
    return g.node

def spring():
    return g.spring




if __name__ == '__main__':
    app.run()