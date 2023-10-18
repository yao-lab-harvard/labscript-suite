import numpy as np
import os
import time as time
import h5py
import pickle 

directory = 'C:/Users/Yao Lab/labscript-suite/Experiments/example_apparatus/brightdark'
index_num = 1
newest_path = min([os.path.join(directory,d) for d in os.listdir(directory)], key=os.path.getmtime)
for i in range(3):
    newest_path = max([os.path.join(newest_path,d) for d in os.listdir(newest_path)], key=os.path.getmtime)
for file_a in os.listdir(newest_path):
    if file_a[-2:] == 'h5': #speed this up by placing all txt files in a separate location
        h5_path = newest_path + '\\' + file_a
        break
with h5py.File(h5_path,'r') as hdf5_file:
    parameters = hdf5_file['globals/bright_dark_parameters']
    xList = eval(parameters.attrs['bd_time'])[0:-1*index_num]
xList_len = len(xList) + 1
used_files = set()
file_list = set()
bref = np.zeros(xList_len)
bsig = np.zeros(xList_len)
dref = np.zeros(xList_len)
dsig = np.zeros(xList_len)
ddref = np.zeros(xList_len)
ddsig = np.zeros(xList_len)
used_files_array = np.zeros(xList_len)
np.savetxt('C:/Users/Yao Lab/labscript-suite/plotter/x_values.txt',xList)
plot_parameters_dict = {'titles': ["Bright Dark", "Contrast"], 'xlabels': ["Time (ns)", "Time (ns)"], 'ylabels': ["Counts", "sig/ref"], "labels": ['[bright_ref,bright_sig, dark_p_ref, dark_p_sig, dark_m_ref, dark_m_sig]', '[bcontrast, d_p_contrast, d_m_contrast]'] }

with open('C:/Users/Yao Lab/labscript-suite/plotter/plot_parameters.txt', 'wb') as f:
    pickle.dump(plot_parameters_dict, f)

while True:
    for file_a in os.listdir(newest_path):
        if file_a[-2:] != 'h5' and file_a not in used_files: #speed this up by placing all txt files in a separate location
            file_list.add(newest_path + '\\' + file_a)
    for k in range(index_num,xList_len):
        for file_b in file_list:
            if float(file_b[130:132]) == k and file_b not in used_files:
                try:
                    data = np.loadtxt(file_b)
                    bref[k-1] += data[0]
                    bsig[k-1] += data[1]
                    dref[k-1] += data[2]
                    dsig[k-1] += data[3]
                    ddref[k-1] += data[4]
                    ddsig[k-1] += data[5]
                    used_files_array[k-1] += 1
                    used_files.add(file_b)
                    logger_file = open('C:/Users/Yao Lab/labscript-suite/plotter/logger_help.txt', 'w')
                    logger_file.write(str(used_files))
                    logger_file.close()
                    #total = sig[1:]/ref[1:]
                    #np.savetxt('C:/Users/Yao Lab/labscript-suite/plotter/analysis_data.txt', total)
                    np.savetxt('C:/Users/Yao Lab/labscript-suite/plotter/analysis_data.txt', np.vstack((bref[0:-1]/used_files_array[0:-1],bsig[0:-1]/used_files_array[0:-1], dref[0:-1]/used_files_array[0:-1],dsig[0:-1]/used_files_array[0:-1], 
                    ddref[0:-1]/used_files_array[0:-1],ddsig[0:-1]/used_files_array[0:-1])))
                    np.savetxt('C:/Users/Yao Lab/labscript-suite/plotter/analysis_data_2.txt', np.vstack((bsig[0:-1]/bref[0:-1],dsig[0:-1]/dref[0:-1],ddsig[0:-1]/ddref[0:-1] )))

                except:
                    '''logger_file = open('C:/Users/Yao Lab/labscript-suite/plotter/logger_help.txt', 'w')
                    logger_file.write('ERROR')
                    logger_file.close()'''
                    time.sleep(1)
                    pass
    file_list = set(file_list) - set(used_files)