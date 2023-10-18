import numpy as np
import os
import time as time
import h5py
import pickle 

directory = 'C:/Users/Yao Lab/labscript-suite/Experiments/example_apparatus/rabi_debugging'

newest_path = min([os.path.join(directory,d) for d in os.listdir(directory)], key=os.path.getmtime)
for i in range(3):
    newest_path = max([os.path.join(newest_path,d) for d in os.listdir(newest_path)], key=os.path.getmtime)
for file_a in os.listdir(newest_path):
    if file_a[-2:] == 'h5': #speed this up by placing all txt files in a separate location
        h5_path = newest_path + '\\' + file_a
        break
with h5py.File(h5_path,'r') as hdf5_file:
    parameters = hdf5_file['globals/AOM_delay']
    xList = eval(parameters.attrs['AOM_delay'])
xList_len = len(xList)
used_files = []
file_list = []
ref = np.zeros(xList_len)
sig = np.zeros(xList_len)
used_files_array = np.zeros(xList_len)

used_files = []
file_list = []
np.savetxt('C:/Users/Yao Lab/labscript-suite/plotter/x_values.txt', xList)
plot_parameters_dict = {'titles': ["AOM Delay", "Contrast"], 'xlabels': ["Time (ns)", "Time (ns)"], 'ylabels': ["Counts", "sig/ref"], "labels": ['[ref,sig]', " "] }

with open('C:/Users/Yao Lab/labscript-suite/plotter/plot_parameters.txt', 'wb') as f:
    pickle.dump(plot_parameters_dict, f)

while True:
    for file_a in os.listdir(newest_path):
        if file_a[-2:] != 'h5' and file_a not in used_files: #speed this up by placing all txt files in a separate location
            file_list.append(newest_path + '\\' + file_a)
    for k in range(xList_len):
        for file_b in file_list:
            if int(file_b[138:140]) == k and file_b not in used_files:
                try:
                    data = np.loadtxt(file_b)
                    ref[k] += data[0]
                    sig[k] += data[1]
                    used_files_array[k] += 1

                    used_files.append(file_b)
                    logger_file = open('C:/Users/Yao Lab/labscript-suite/plotter/logger_help.txt', 'w')
                    logger_file.write(str(used_files))
                    logger_file.close()
                    np.savetxt('C:/Users/Yao Lab/labscript-suite/plotter/analysis_data.txt', np.vstack((ref/used_files_array,sig//used_files_array)))
                    np.savetxt('C:/Users/Yao Lab/labscript-suite/plotter/analysis_data_2.txt', (sig/ref))

                except:
                    '''logger_file = open('C:/Users/Yao Lab/labscript-suite/plotter/logger_help.txt', 'w')
                    logger_file.write('ERROR')
                    logger_file.close()'''
                    time.sleep(1)
                    pass
