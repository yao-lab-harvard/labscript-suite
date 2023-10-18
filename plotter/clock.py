
import matplotlib
import os
import subprocess
import psutil
import numpy as np
import time
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
try:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
except ImportError:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from mpl_toolkits.axes_grid1 import make_axes_locatable

from matplotlib import style

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageGrab
import h5py
import pickle


LARGE_FONT= ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(5,5), dpi=100)
f_2 = Figure(figsize=(5,5), dpi=100)

a = f.add_subplot(121)
a_2 = f.add_subplot(122)
b = f_2.add_subplot(111)
b.axis('equal')
div = make_axes_locatable(b)
cax = div.append_axes('right', '5%', '5%')
b.set_facecolor('white')
a.set_facecolor('white')
a_2.set_facecolor('white')

for word in ['left', 'right', 'top', 'bottom']:
    b.spines[word].set_color('black')
    a.spines[word].set_color('black')
    a_2.spines[word].set_color('black')

b.tick_params(axis='x', colors='black')    #setting up X-axis tick color to red
b.tick_params(axis='y', colors='black')    #setting up X-axis tick color to red
a.tick_params(axis='x', colors='black')    #setting up X-axis tick color to red
a.tick_params(axis='y', colors='black')    #setting up X-axis tick color to red
a_2.tick_params(axis='x', colors='black')    #setting up X-axis tick color to red
a_2.tick_params(axis='y', colors='black')    #setting up X-axis tick color to red


def animate(i):
    with open('C:/Users/Yao Lab/labscript-suite/plotter/plot_parameters.txt', 'rb') as f:
        loaded_dict = pickle.load(f)
    try:
        x_values = np.loadtxt('C:/Users/Yao Lab/labscript-suite/plotter/x_values.txt')
        yList = np.loadtxt('C:/Users/Yao Lab/labscript-suite/plotter/analysis_data.txt')
        yList_2 = np.loadtxt('C:/Users/Yao Lab/labscript-suite/plotter/analysis_data_2.txt')

        #print(yList)
        a.clear()
        a_2.clear()
        a.set_title(loaded_dict['titles'][0])
        a.set_xlabel(loaded_dict['xlabels'][0])
        a.set_ylabel(loaded_dict['ylabels'][0])

        if len(np.shape(yList)) > 1:
            #print(np.shape(yList)[0])
            for i in range(np.shape(yList)[0]):
                #a.plot(x_values, yList[i])
                #print(loaded_dict['labels'][0].strip().strip('][').split(',')[i])
                a.plot(x_values, yList[i], marker = '.', label = loaded_dict['labels'][0].strip().strip('][').split(',')[i], )
            a.legend()

            a_2.set_title(loaded_dict['titles'][1])
            a_2.set_xlabel(loaded_dict['xlabels'][1])
            a_2.set_ylabel(loaded_dict['ylabels'][1])

            if len(np.shape(yList_2)) == 1:
                a_2.plot(x_values, yList_2, '.')
                a_2.plot(x_values, yList_2, '-')
            else:
                for i in range(np.shape(yList_2)[0]):
                    a_2.plot(x_values, yList_2[i], marker = '.',  label = loaded_dict['labels'][1].strip().strip('][').split(',')[i], )
                a_2.legend()
        else:
            a.plot(x_values,yList)
            #print(yList[i])
        #a.plot(plot_parameters, yList)
    except:
        print("failed")
        pass


def count_update(x_cur,y_cur,x_array,y_array,data_array):
    for i in range(len(x_array) - 1):
        x_mid = (x_array[i] + x_array[i+1])/2
        if x_array[i] <= x_cur and x_cur < x_mid:
            for j in range(len(y_array) - 1):
                y_mid = (y_array[j] + y_array[j+1])/2
                if y_array[j] <= y_cur and y_cur < y_mid:
                    return data_array[j, i]
                elif y_mid <= y_cur and y_cur < y_array[j+1]:
                    return data_array[j+1, i]
        elif x_mid <= x_cur and x_cur < x_array[i+1]:
            for j in range(len(y_array) - 1):
                y_mid = (y_array[j] + y_array[j+1]) / 2
                if y_array[j] <= y_cur and y_cur < y_mid:
                    return data_array[j, i+1]
                elif y_mid <= y_cur and y_cur < y_array[j+1]:
                    return data_array[j+1, i+1]


class Data_Analysis(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "Analysis")
        
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)



        tk.Tk.config(self, menu=menubar)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree):

            frame = F(container, self)
            

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = ttk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = ttk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(PageThree))
        button3.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):        
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Scan Page!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        self.canvas = FigureCanvasTkAgg(f_2, self)
        #self.canvas.draw()
        #self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()
        #self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.X)
        self.canvas.get_tk_widget().config(width = 600, height = 600)

        self.canvas._tkcanvas.place(x = 900, y = 100)
        
        #self.canvas.get_tk_widget().configure(bg='white')
        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Plot Newest",
                            command=self.plot_newest)
        button2.pack()

        button2 = ttk.Button(self, text="Plot Loaded",
                            command=self.plot_loaded)
        button2.pack()

        button3 = ttk.Button(self, text="Load",
                            command=self.openfile)
        button3.pack()
        
        x_offset = 0
        y_offset = 0 
        fix_button = ttk.Button(self, text="Fix",
                            command=self.fix)
        fix_button.place(x = x_offset + 460, y = y_offset + 150)

    
        scan_button = ttk.Button(self, text="Scan",command=self.scan)
        scan_button.place(x = x_offset + 460, y = y_offset + 400)

        stop_button = ttk.Button(self, text="Stop",command=self.stop)
        stop_button.place(x = x_offset + 370, y = y_offset + 400)

        run_CPS_button = ttk.Button(self, text="Run CPS",command=lambda: self.run_CPS(True))
        run_CPS_button.place(x = x_offset + 160, y = y_offset + 500)

        stop_CPS_button = ttk.Button(self, text="Stop CPS",command=lambda: self.run_CPS(False))
        stop_CPS_button.place(x = x_offset + 260, y = y_offset + 500)

        self.CPS_label = ttk.Label(self, background='purple', foreground='white')
        self.CPS_label.place(x = x_offset + 260, y = y_offset + 450)

        count_label = tk.Label(self, text="Counts:", font=10)
        count_label.pack(pady=2,padx=2)
        count_label.place(x = x_offset + 180, y = y_offset + 600)

        self.count_disp = ttk.Label(self, foreground='black', font=10)
        self.count_disp.place(x = x_offset + 260, y = y_offset + 600)

        self.V_x_min_text = tk.Entry(self, width = 7)
        self.V_x_min_text.place(x = x_offset + 160, y = y_offset + 200)
        self.V_x_min_text.insert(tk.END, "-0.1")

        self.V_x_max_text = tk.Entry(self, width = 7)
        self.V_x_max_text.place(x = x_offset + 260, y = y_offset + 200)
        self.V_x_max_text.insert(tk.END, "0.1")

        self.V_x_points_text = tk.Entry(self, width = 7)
        self.V_x_points_text.place(x = x_offset + 360, y = y_offset + 200)
        self.V_x_points_text.insert(tk.END, "100")

        self.Fix_V_x_text = tk.Checkbutton(self, text = "Fix Vx")
        self.Fix_V_x_text.place(x = x_offset + 400, y = 200)

        self.V_x_text = tk.Entry(self, width = 7)
        self.V_x_text.place(x = x_offset + 460, y = y_offset + 200)

        self.V_y_min_text = tk.Entry(self, width = 7)
        self.V_y_min_text.place(x = x_offset + 160, y = y_offset + 250)
        self.V_y_min_text.insert(tk.END, "-0.1")

        self.V_y_max_text = tk.Entry(self, width = 7)
        self.V_y_max_text.place(x = x_offset + 260, y = y_offset + 250)
        self.V_y_max_text.insert(tk.END, "0.1")

        self.V_y_points_text = tk.Entry(self, width = 7)
        self.V_y_points_text.place(x = x_offset + 360, y = y_offset + 250)
        self.V_y_points_text.insert(tk.END, "100")

        self.Fix_V_y_text = tk.Checkbutton(self, text = "Fix Vy")
        self.Fix_V_y_text.place(x = x_offset + 400, y = 250)

        self.V_y_text = tk.Entry(self, width = 7)
        self.V_y_text.place(x = x_offset + 460, y = y_offset + 250)

        self.V_z_min_text = tk.Entry(self, width = 7)
        self.V_z_min_text.place(x = x_offset + 160, y = y_offset + 300)
        self.V_z_min_text.insert(tk.END, "0")

        self.V_z_max_text = tk.Entry(self, width = 7)
        self.V_z_max_text.place(x = x_offset + 260, y = y_offset + 300)
        self.V_z_max_text.insert(tk.END, "100")

        self.V_z_points_text = tk.Entry(self, width = 7)
        self.V_z_points_text.place(x = x_offset + 360, y = y_offset + 300)
        self.V_z_points_text.insert(tk.END, "100")

        self.Fix_V_z_text = tk.Checkbutton(self, text = "Fix Vz")
        self.Fix_V_z_text.place(x = x_offset + 400, y = 300)

        self.V_z_text = tk.Entry(self, width = 7)
        self.V_z_text.place(x = x_offset + 460, y = y_offset + 300)
        self.V_z_text.insert(tk.END, "50")

        self.dt_min_text = tk.Entry(self, width = 7)
        self.dt_min_text.place(x = x_offset + 160, y = y_offset + 350)
        self.dt_min_text.insert(tk.END, "0.001")

        self.dt_max_text = tk.Entry(self, width = 7)
        self.dt_max_text.place(x = x_offset + 260, y = y_offset + 350)
        self.dt_max_text.insert(tk.END, "0.003")

        self.dt_points_text = tk.Entry(self, width = 7)
        self.dt_points_text.place(x = x_offset + 360, y = y_offset + 350)
        self.dt_points_text.insert(tk.END, "10")

        self.Fix_dt_text = tk.Checkbutton(self, text = "Fix dt")
        self.Fix_dt_text.place(x = x_offset + 400, y = 350)

        self.dt_text = tk.Entry(self, width = 7)
        self.dt_text.place(x = x_offset + 460, y = y_offset + 350)
        self.dt_text.insert(tk.END, "0.001")

        self.x_cursor = None
        self.y_cursor = None
        self.cursor = None

        f_2.canvas.mpl_connect('button_press_event', self.mouse_event)

    def mouse_event(self,event):
        print('x: {} and y: {}'.format(event.xdata, event.ydata))
        self.x_cursor = event.xdata
        self.y_cursor = event.ydata
        if self.cursor is not None:
            self.cursor.remove()
        if self.x_cursor is not None:
            self.cursor = b.scatter(self.x_cursor, self.y_cursor, s = 5, c = 'red', marker = '+')
        self.canvas.draw()
        self.V_x_text.delete(0, tk.END)
        self.V_y_text.delete(0, tk.END)

        self.V_x_text.insert(tk.END, str(self.x_cursor))
        self.V_y_text.insert(tk.END, str(self.y_cursor))
        
        check = np.loadtxt('load_status.txt')
        if check == 1:
            #arr = np.rot90(np.loadtxt("load_colorplot.txt"),3)
            arr = np.loadtxt('load_colorplot.txt')
            V_x_units = self.b_x_offset + np.linspace(self.b_x_min, self.b_x_max, self.n)
            V_y_units = self.b_y_offset + np.linspace(self.b_y_min, self.b_y_max, self.n)
            counts_val = count_update(self.x_cursor, self.y_cursor, V_x_units, V_y_units, arr)
        else:
            arr = np.loadtxt('colorplot.txt')
            V_x_units = self.b_x_offset + np.linspace(self.b_x_min, self.b_x_max, self.n)
            V_y_units = self.b_y_offset + np.linspace(self.b_y_min, self.b_y_max, self.n)
            counts_val = count_update(self.x_cursor, self.y_cursor, V_x_units, V_y_units, arr)
        self.count_disp.config(text=str(counts_val))
        
        np.savetxt('laser_location.txt', np.array([self.x_cursor, self.y_cursor]))

    def calculate_newest(self):
        directory = 'C:/Users/Yao Lab/labscript-suite/Experiments/example_apparatus/Scan'

        newest_path = min([os.path.join(directory,d) for d in os.listdir(directory)], key=os.path.getmtime)
        for i in range(3):
            newest_path = max([os.path.join(newest_path,d) for d in os.listdir(newest_path)], key=os.path.getmtime)
        for file_a in os.listdir(newest_path):
            if file_a[-2:] != 'h5': #speed this up by placing all txt files in a separate location
                data_path = newest_path + '\\' + file_a
            else:
                h5_path = newest_path + '\\' + file_a
        data = np.loadtxt(data_path)
        data = np.append(data,0)
        self.n = int( (len(data))**0.5 )
        #print(len(data))
        data = np.reshape(data, (self.n,self.n))
        data[1::2, :] = data[1::2, ::-1]
        data = np.rot90(data, 1)
        np.savetxt('colorplot.txt', data)
        with h5py.File(h5_path,'r') as hdf5_file:
            parameters = hdf5_file['globals/raster_parameters_non_blacs']
            self.b_x_min = np.float64(parameters.attrs['V_x_min'])
            self.b_x_max = np.float64(parameters.attrs['V_x_max'])
            self.b_x_offset = np.float64(parameters.attrs['V_x_offset'])
            self.b_y_min = np.float64(parameters.attrs['V_y_min'])
            self.b_y_max = np.float64(parameters.attrs['V_y_max'])
            self.b_y_offset = np.float64(parameters.attrs['V_y_offset'])

    def plot_newest(self):
        print("Plotting Newest Image")
        b.clear()
        self.calculate_newest()
        arr = np.loadtxt('colorplot.txt')
        vmax     = np.max(arr)
        vmin     = np.min(arr)
        levels   = np.linspace(vmin, vmax, 200, endpoint = True)
        V_x_units = self.b_x_offset + np.linspace(self.b_x_min, self.b_x_max, self.n)
        V_y_units = self.b_y_offset + np.linspace(self.b_y_min, self.b_y_max, self.n)
        V_x_mesh, V_y_mesh = np.meshgrid(V_x_units, V_y_units)
        #print(V_x_units)
        #cf = b.contourf(V_x_mesh, V_y_mesh, arr, levels)
        cf = b.imshow(arr, origin = 'lower', extent=(self.b_x_min+self.b_x_offset,self.b_x_max+self.b_x_offset,self.b_y_min+self.b_y_offset,self.b_y_max+self.b_y_offset),aspect='auto',interpolation='none')
        cax.cla()
        #b.set_xlim([self.b_x_min, self.b_x_max])
        #b.set_ylim([self.b_y_min, self.b_y_max])
        f_2.colorbar(cf, cax=cax)
        np.savetxt('load_status.txt', np.array([0]))
        if self.x_cursor is not None:
            self.cursor = b.scatter(self.x_cursor, self.y_cursor, s = 5, c = 'red', marker = '+')
            #counts_val = count_update(self.x_cursor, self.y_cursor, V_x_units, V_y_units, np.rot90(arr, 3))
            counts_val = count_update(self.x_cursor, self.y_cursor, V_x_units, V_y_units, arr)
            self.count_disp.config(text=str(counts_val))
        self.canvas.draw()
        

    def plot_loaded(self):
        print("Plotting Loaded Image")
        b.clear()
        data = np.loadtxt(self.loaded_file)
        self.n = int( (len(data))**0.5 )
        data = np.reshape(data, (self.n, self.n))
        data[1::2, :] = data[1::2, ::-1]
        data = np.rot90(data, 1)
        np.savetxt('load_colorplot.txt', data)
        arr = np.loadtxt('load_colorplot.txt')
        for i in range(-1,-len(self.loaded_file),-1):
            if self.loaded_file[i] == "/":
                pos = i
                file_name = self.loaded_file[i+1:]
                break
        root_path = self.loaded_file[:pos+1]
        h5file_name = file_name[13:-3]+"h5"
        h5_path = root_path + h5file_name
        with h5py.File(h5_path,'r') as hdf5_file:
            parameters = hdf5_file['globals/raster_parameters_non_blacs']
            self.b_x_min = np.float64(parameters.attrs['V_x_min'])
            self.b_x_max = np.float64(parameters.attrs['V_x_max'])
            self.b_x_offset = np.float64(parameters.attrs['V_x_offset'])
            self.b_y_min = np.float64(parameters.attrs['V_y_min'])
            self.b_y_max = np.float64(parameters.attrs['V_y_max'])
            self.b_y_offset = np.float64(parameters.attrs['V_y_offset'])
        vmax     = np.max(arr)
        vmin     = np.min(arr)
        levels   = np.linspace(vmin, vmax, 200, endpoint = True)
        V_x_units = self.b_x_offset + np.linspace(self.b_x_min, self.b_x_max, self.n)
        V_y_units = self.b_y_offset + np.linspace(self.b_y_min, self.b_y_max, self.n)
        V_x_mesh, V_y_mesh = np.meshgrid(V_x_units, V_y_units)
        #cf = b.contourf(V_x_mesh, V_y_mesh, arr, vmax=vmax, vmin=vmin, levels=levels)
        #cf = b.contourf(V_x_mesh, V_y_mesh, arr, levels)
        cf = b.imshow(arr,origin='lower',extent=(self.b_x_min+self.b_x_offset,self.b_x_max+self.b_x_offset,self.b_y_min+self.b_y_offset,self.b_y_max+self.b_y_offset), aspect='auto',interpolation='none')
        cax.cla()
        #b.set_xlim([self.b_x_min, self.b_x_max])
        #b.set_ylim([self.b_y_min, self.b_y_max])
        f_2.colorbar(cf, cax=cax)
        np.savetxt('load_status.txt', np.array([1]))
        if self.x_cursor is not None:
            self.cursor = b.scatter(self.x_cursor, self.y_cursor, s = 5, c = 'red', marker = '+')
            counts_val = count_update(self.x_cursor, self.y_cursor, V_x_units, V_y_units, arr)
            self.count_disp.config(text=str(counts_val))
        self.canvas.draw()
        
        
    def openfile(self):
        self.loaded_file = tk.filedialog.askopenfilename()
        return 0

    def get_values(self):
        V_x_min, V_x_max, V_x_points, V_x = self.V_x_min_text.get(), self.V_x_max_text.get(), self.V_x_points_text.get(), self.V_x_text.get()
        V_y_min, V_y_max, V_y_points, V_y = self.V_y_min_text.get(), self.V_y_max_text.get(), self.V_y_points_text.get(), self.V_y_text.get()
        V_z_min, V_z_max, V_z_points, V_z = self.V_z_min_text.get(), self.V_z_max_text.get(), self.V_z_points_text.get(), self.V_z_text.get()
        dt_min, dt_max, dt_points, dt = self.dt_min_text.get(), self.dt_max_text.get(), self.dt_points_text.get(), self.dt_text.get()
        return (V_x_min, V_x_max, V_x_points, V_x), (V_y_min, V_y_max, V_y_points, V_y), (V_z_min, V_z_max, V_z_points, V_z), (dt_min, dt_max, dt_points, dt)

    def fix(self):
        print(self.get_values())
        return self.get_values()

    def scan(self):
        return 0

    def stop(self):
        return 0

    def run_CPS(self, enable):
        self.cancel = not enable
        self.CPS_updater()
        

    def CPS_updater(self):
        if not self.cancel:
            np.savetxt('C:/Users/Yao Lab/labscript-suite/plotter/CPS_status.txt', np.array([1]))
            num_string = np.loadtxt('CPS.txt')
            self.CPS_label.config(text=num_string)
            self.CPS_ID = self.CPS_label.after(1000, self.CPS_updater)
        else:
            np.savetxt('C:/Users/Yao Lab/labscript-suite/plotter/CPS_status.txt', np.array([0]))
            self.CPS_ID = self.CPS_label.after_cancel(self.CPS_updater)

        #else:
            #self.CPS_label.after_cancel(self.CPS_ID)


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Data Page!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas.get_tk_widget().configure(bg='white')

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        button2 = ttk.Button(self, text="Load Analysis Script",
                            command=self.loadfile)
        button2.pack()

        button3 = ttk.Button(self, text="Run Analysis Script",
                            command=self.runfile)
        button3.pack()


    def loadfile(self):
        self.loaded_file = tk.filedialog.askopenfilename(initialdir='C:/Users/Yao Lab/labscript-suite/plotter/analysis')
        '''for proc in psutil.process_iter():
            try:
                # Get process name & pid from process object.
                processName = proc.name()
                processID = proc.pid

                if processName.startswith("python3"): # adapt this line to your needs
                    print(f"I will kill {processName}[{processID}] : {''.join(proc.cmdline())})")
                    # proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                print(e)'''
        try:
            self.subprocess.kill()
        except:
            print("no subprocess")
            pass
    def runfile(self):
        print(self.loaded_file)
        '''with open(self.loaded_file) as f:
            exec(f.read())'''
        my_pid = os.getpid()
        self.subprocess = subprocess.Popen(['python', self.loaded_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


app = Data_Analysis()
#app.geometry("1280x720")

ani = animation.FuncAnimation(f, animate, interval=1000)

#ani = animation.FuncAnimation(f_2, animate, interval=1000)

app.mainloop()

