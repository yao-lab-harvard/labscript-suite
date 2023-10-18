from labscript import *
from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
from labscript_devices.NI_DAQmx.models import NI_PCIe_6343
from labscript_devices.SRS384 import SRS384, SRS384DDS

PulseBlasterESRPro500(name= 'pb', loop_number = 2*ESRnumIterations,  extra_flags = 0, extra_inst = 3, extra_inst_data = 2, extra_length= 10, inst_location = 7, additional_inst = 8,
                         loop_start = 0, board_number = 0, programming_scheme = 'pb_start/BRANCH') #our pulseblaster
ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0") #specialized clockline for NI DAQ
ClockLine(name = "pb_clockline_5", pseudoclock = pb.pseudoclock, connection = "flag 5") #dummy clockline because every device needs a clockline

NI_PCIe_6343(name = 'Dev2',  #defining our DAQ
    parent_device = pb_clockline,
    clock_terminal = '/Dev2/PFI5',
    MAX_name = 'Dev2',
    stop_order = -1,
    acquisition_rate = 1e5
    )

DigitalOut('pb_1',pb.direct_outputs, 'flag 1') #trigger DAQ counter
DigitalOut('pb_2',pb.direct_outputs, 'flag 2') #laser
DigitalOut('pb_3',pb.direct_outputs, 'flag 3') #trigger fpga
DigitalOut('pb_4',pb.direct_outputs, 'flag 4') #open mw switch
DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #dummy

#StaticAnalogOut('anaout_0', Dev2, 'ao0')
#StaticAnalogOut('anaout_1', Dev2, 'ao1')
AnalogOut('anaout_0', Dev2, 'ao0')
AnalogOut('anaout_1', Dev2, 'ao1')
AnalogOut('anaout_2', Dev2, 'ao2')
AnalogOut('anaout_3', Dev2, 'ao3')
CounterIn("counter", Dev2, connection = "ctr2", CPT_connection = "PFI0", trigger = "PFI1", numIterations = ESRnumIterations)

DigitalOut('daq_dout_8', Dev2, 'port0/line8') 
DigitalOut('daq_dout_9', Dev2, 'port0/line9') 


PiezoEO(name = 'EO', parent_device = pb_clockline_5) #defining piezo
PiezoEODDS('Piezo', EO, 'a')

SRS384(name = 'SRS1', parent_device = pb_clockline_5, com_port = 'COM12')
SRS384DDS('SRSDDS1', SRS1, 'a1')
#SRS384(name = 'SRS2', parent_device = pb_clockline_5, com_port = 'COM3')
#SRS384DDS('SRSDDS2', SRS2, 'a2')
t = 0  
add_time_marker(t, "Start", verbose = True)
start()
counter.fast_counter(1e8,2, 0) #freq, number of times called per sequence, 0/1 = save all data/save efficient data 
SRSDDS1.setamp(t, ESR_SRS_amp)
SRSDDS1.setfreq(t, ESR_freq_center)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_freq_sweep(t)
SRSDDS1.set_sweep_rate(t, freq_sweep_rate)
SRSDDS1.set_sweep_dev(t, freq_dev)
#SRSDDS2.enable_mod(t, False)
anaout_0.constant(t, V_laser_x)
anaout_1.constant(t, V_laser_y)
Piezo.setamp(t, 50)
t += 20e-9

pb_2.go_high(t)
pb_4.go_high(t)
for i in range(repetitions):
    for j in range(N_data_points):
        anaout_2.constant(t, -1 + 2*j/(N_data_points - 1)) 
        t+=SRS_dt
        pb_1.go_high(t)
        t+=3*SRS_dt     
        pb_1.go_low(t)        
        
    for j in range(N_data_points):
        anaout_2.constant(t, 1 - 2*j/(N_data_points - 1)) 
        t+=SRS_dt
        pb_1.go_high(t)
        t+=3*SRS_dt        
        pb_1.go_low(t)        
            
pb_2.go_low(t)
pb_4.go_low(t)
t += 10e-6
pb_1.go_high(t)
t += 6e-8
pb_1.go_low(t)
t+= 6e-8
pb_1.go_high(t)
t += 6e-8
pb_1.go_low(t)
t+= 6e-8
pb_1.go_high(t)
t += 6e-8
pb_1.go_low(t)
t+= 6e-8
pb_1.go_high(t)
t += 6e-8
pb_1.go_low(t)
t+= 6e-8

stop(t)