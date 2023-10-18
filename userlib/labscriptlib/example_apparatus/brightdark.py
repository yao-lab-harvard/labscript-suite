from labscript import *
from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
from labscript_devices.NI_DAQmx.models import NI_PCIe_6343
from labscript_devices.SRS384 import SRS384, SRS384DDS

PulseBlasterESRPro500(name= 'pb', loop_number = numIterations,  extra_flags = 0, extra_inst = 3, extra_inst_data = 3, extra_length= 10, inst_location = 28, additional_inst = 12, loop_start = 1, board_number = 0, programming_scheme = 'pb_start/BRANCH')
ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")

NI_PCIe_6343(name = 'Dev2',
    parent_device = pb_clockline,
    clock_terminal = '/Dev2/PFI5',
    MAX_name = 'Dev2',
    static_AO = True,
    stop_order = -1,
    acquisition_rate = 1e5
    )
DigitalOut('pb_1',pb.direct_outputs, 'flag 1') #counter readout
DigitalOut('pb_2',pb.direct_outputs, 'flag 2') #laser 
DigitalOut('pb_3',pb.direct_outputs, 'flag 3') #MW trigger
DigitalOut('pb_4',pb.direct_outputs, 'flag 4') #MW gate
DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #MW gate

StaticAnalogOut('anaout_0', Dev2, 'ao0')
StaticAnalogOut('anaout_1', Dev2, 'ao1')

CounterIn("counter", Dev2, connection = "ctr2", CPT_connection = "PFI0", trigger = "PFI1", numIterations = numIterations)
#ctr 1 is cpt

DigitalOut('daq_dout_8', Dev2, 'port0/line8') 
DigitalOut('daq_dout_9', Dev2, 'port0/line9') 
ZCU111(name = 'ZCU', parent_device = pb_clockline_2, com_port = 'COM5')
ZCU111DDS('ZCUDDS', ZCU, 'a')
PiezoEO(name = 'EO', parent_device = pb_clockline_2)
PiezoEODDS('Piezo', EO, 'a')
SRS384(name = 'SRS1', parent_device = pb_clockline_2, com_port = 'COM12')
SRS384DDS('SRSDDS1', SRS1, 'a1')
SRS384(name = 'SRS2', parent_device = pb_clockline_2, com_port = 'COM3')
SRS384DDS('SRSDDS2', SRS2, 'a2')

t = 0  
add_time_marker(t, "Start", verbose = True)
start()
#dt = 5e-3
#print(sys.path)
counter_gate_time = 500e-9

counter.fast_counter(1e8, 6, 1)
Piezo.setamp(t, 50)
SRSDDS1.setamp(t, bd_SRS_amp)
SRSDDS1.setfreq(t, bd_SRS_freq_1)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_IQ(t)
SRSDDS2.setamp(t, bd_SRS_amp)
SRSDDS2.setfreq(t, bd_SRS_freq_2)
SRSDDS2.enable_mod(t, True)
SRSDDS2.enable_IQ(t)
ZCUDDS.set_repetitions(t, '2')
ZCUDDS.set_delay_time(t,str(0)) 
ZCUDDS.set_start_src(t, 'external')
ZCUDDS.add_TTL(4, 0, 10e-9)

if bd_time < 100e-9:
    ZCUDDS.add_pulse(5,'buffer',120e-9, bd_pi_pulse_time, int(32766),100,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    ZCUDDS.add_pulse(6,'buffer',120e-9, bd_pi_pulse_time, int(32766),100,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  
    ZCUDDS.add_pulse(5,'buffer',120e-9 + 32e-9 + bd_pi_pulse_time*(10**(-9)) + bd_time + 2*counter_gate_time + 15e-6, bd_pi_pulse_time, int(32766),100,0,'oneshot','product','[]') 
    ZCUDDS.add_pulse(6,'buffer',120e-9 + 32e-9 + bd_pi_pulse_time*(10**(-9)) + bd_time + 2*counter_gate_time + 15e-6, bd_pi_pulse_time, int(32766),100,90,'oneshot','product','[]') 
    ZCUDDS.add_pulse(5,'buffer',120e-9 + 32e-9 + 2*bd_pi_pulse_time*(10**(-9)) + 2*bd_time + 2*counter_gate_time + 15e-6, bd_pi_pulse_time, int(32766),100,0,'oneshot','product','[]') 
    ZCUDDS.add_pulse(6,'buffer',120e-9 + 32e-9 + 2*bd_pi_pulse_time*(10**(-9)) + 2*bd_time + 2*counter_gate_time + 15e-6, bd_pi_pulse_time, int(32766),100,90,'oneshot','product','[]') 
    ZCUDDS.add_pulse(5,'buffer',120e-9 + 2*32e-9 + 3*bd_pi_pulse_time*(10**(-9)) + 2*bd_time + 4*counter_gate_time + 30e-6, bd_pi_pulse_time, int(32766),100,0,'oneshot','product','[]') 
    ZCUDDS.add_pulse(6,'buffer',120e-9 + 2*32e-9 + 3*bd_pi_pulse_time*(10**(-9)) + 2*bd_time + 4*counter_gate_time + 30e-6, bd_pi_pulse_time, int(32766),100,90,'oneshot','product','[]') 

    ZCUDDS.add_pulse(0,'buffer',120e-9 + 2*32e-9 + 4*bd_pi_pulse_time*(10**(-9)) + 3*bd_time + 4*counter_gate_time + 30e-6, bd_pi_pulse_time, int(20766),100,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    ZCUDDS.add_pulse(2,'buffer',120e-9 + 2*32e-9 + 4*bd_pi_pulse_time*(10**(-9)) + 3*bd_time + 4*counter_gate_time + 30e-6, bd_pi_pulse_time, int(20766),100,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
else:
    ZCUDDS.add_pulse(5,'const',120e-9, bd_pi_pulse_time, int(32766/2),100,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    ZCUDDS.add_pulse(6,'const',120e-9, bd_pi_pulse_time, int(32766/2),100,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  
    ZCUDDS.add_pulse(5,'const',120e-9 + 32e-9 + bd_pi_pulse_time*(10**(-9)) + bd_time + 2*counter_gate_time + 15e-6, bd_pi_pulse_time, int(32766/2),100,0,'oneshot','product','[]') 
    ZCUDDS.add_pulse(6,'const',120e-9 + 32e-9 + bd_pi_pulse_time*(10**(-9)) + bd_time + 2*counter_gate_time + 15e-6, bd_pi_pulse_time, int(32766/2),100,90,'oneshot','product','[]') 
    ZCUDDS.add_pulse(5,'const',120e-9 + 32e-9 + 2*bd_pi_pulse_time*(10**(-9)) + 2*bd_time + 2*counter_gate_time + 15e-6, bd_pi_pulse_time, int(32766/2),100,0,'oneshot','product','[]') 
    ZCUDDS.add_pulse(6,'const',120e-9 + 32e-9 + 2*bd_pi_pulse_time*(10**(-9)) + 2*bd_time + 2*counter_gate_time + 15e-6, bd_pi_pulse_time, int(32766/2),100,90,'oneshot','product','[]') 
    ZCUDDS.add_pulse(5,'const',120e-9 + 2*32e-9 + 3*bd_pi_pulse_time*(10**(-9)) + 2*bd_time + 4*counter_gate_time + 30e-6, bd_pi_pulse_time, int(32766/2),100,0,'oneshot','product','[]') 
    ZCUDDS.add_pulse(6,'const',120e-9 + 2*32e-9 + 3*bd_pi_pulse_time*(10**(-9)) + 2*bd_time + 4*counter_gate_time + 30e-6, bd_pi_pulse_time, int(32766/2),100,90,'oneshot','product','[]') 

    ZCUDDS.add_pulse(0,'const',120e-9 + 2*32e-9 + 4*bd_pi_pulse_time*(10**(-9)) + 3*bd_time + 4*counter_gate_time + 30e-6, bd_pi_pulse_time, int(14766/2),100,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    ZCUDDS.add_pulse(2,'const',120e-9 + 2*32e-9 + 4*bd_pi_pulse_time*(10**(-9)) + 3*bd_time + 4*counter_gate_time + 30e-6, bd_pi_pulse_time, int(14766/2),100,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
anaout_0.constant(V_laser_x)
anaout_1.constant(V_laser_y)   
pb_2.go_high(t) #laser
#pb_4.go_high(t)
pb_bd_time = max(0, bd_time - bd_time_offset)
t += 20e-6
pb_3.go_high(t)
t += 300e-9
pb_1.go_high(t) #start reference counts
t += counter_gate_time
pb_1.go_low(t) #stop reference counts
pb_3.go_low(t)

pb_4.go_high(t-20e-9) #turn on MW switch
pb_4.go_low(t + (bd_pi_pulse_time)*(10**(-9)) + 10e-9) #turn it off
t += pb_bd_time + bd_pi_pulse_time*(10**(-9)) +35e-9
pb_1.go_high(t) #start signal counts
t += counter_gate_time
pb_1.go_low(t) #end signal counts
t += 15e-6

pb_1.go_high(t) #start reference counts
t += counter_gate_time
pb_1.go_low(t) #stop reference counts

if pb_bd_time < 50e-9:
    pb_4.go_high(t-20e-9)
    t += bd_pi_pulse_time*(10**(-9))/2
    pb_6.go_high(t)
    t +=bd_pi_pulse_time *(10**(-9))/2
    pb_6.go_low(t)
    t+= pb_bd_time + bd_pi_pulse_time*(10**(-9)) + 35e-9
    pb_4.go_low(t-40e-9)
else:
    pb_4.go_high(t-20e-9) #turn on MW switch
    pb_4.go_low(t + (bd_pi_pulse_time)*(10**(-9)) + 10e-9) 
    t += pb_bd_time + 2*bd_pi_pulse_time*(10**(-9)) + 35e-9

    pb_4.go_high(t - 50e-9 - bd_pi_pulse_time*(10**(-9))) #turn on MW swit
    pb_4.go_low(t-30e-9) #turn it off'''
pb_1.go_high(t) #start signal counts
t += counter_gate_time
pb_1.go_low(t) #end signal counts
t+=15e-6

pb_1.go_high(t) #start reference counts
t += counter_gate_time
pb_1.go_low(t) #stop reference counts
if pb_bd_time < 50e-9:
    pb_4.go_high(t-20e-9)
    t += bd_pi_pulse_time*(10**(-9))/2
    pb_6.go_high(t)
    t +=bd_pi_pulse_time *(10**(-9))/2
    pb_6.go_low(t)
    t+= pb_bd_time + bd_pi_pulse_time*(10**(-9)) + 35e-9
    pb_4.go_low(t-30e-9)
else:
    pb_4.go_high(t-20e-9) #turn on MW switch
    pb_4.go_low(t + (bd_pi_pulse_time)*(10**(-9)) + 10e-9) #turn it off
    t += pb_bd_time + 2*bd_pi_pulse_time*(10**(-9)) + 35e-9

    pb_4.go_high(t - 50e-9 - bd_pi_pulse_time*(10**(-9))) #turn on MW switch
    pb_4.go_low(t-30e-9) #turn it off
pb_1.go_high(t) #start signal counts
t += counter_gate_time
pb_1.go_low(t) #end signal counts


pb_2.go_low(t)
t+= 30e-6
pb_2.go_high(t)
t += 20e-6

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
pb_1.go_high(t)
t += 6e-8
pb_1.go_low(t)
t+= 6e-8
pb_1.go_high(t)
t += 6e-8
pb_1.go_low(t)
t+= 6e-8
stop(t)