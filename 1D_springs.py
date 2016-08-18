import numpy as np
import pandas as pd

node = pd.read_csv('node.csv')
spring = pd.read_csv('spring.csv')

force = node.ix[:,3]

k1 = spring.ix[0, 3]
k2 = spring.ix[1, 3]

stmx = np.array([[k1, -k1, 0],
                 [-k1, k1+k2, -k2],
                 [0, -k2, k2]])


force =  np.array(force[1:3])
stmx =  stmx[np.ix_([1,2],[1,2])]

x = np.linalg.solve(stmx, force)
print(x)