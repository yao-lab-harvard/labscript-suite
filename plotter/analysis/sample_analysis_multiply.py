import numpy as np

directory = 'C:/Users/nateu/Downloads/plotter'

total = np.loadtxt('data1.txt')
for i in range(2,10):
    data = np.loadtxt('data' +str(i) +'.txt')
    total = np.multiply(total, data)

np.savetxt('C:/Users/nateu/Downloads/plotter/analysis_data.txt', total)