from labscript import *
from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
from labscript_devices.NI_DAQmx.models import NI_PCIe_6343
from labscript_devices.SRS384 import SRS384, SRS384DDS


##############################
## Connection table ##
##############################
# The Pulseblaster is triggering the FPGA and the NI DAQ
PulseBlasterESRPro500(name='pb')#loop_number = numIterations
pb.setParams(numIterations)
ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")

DigitalOut('pb_1',pb.direct_outputs, 'flag 1') #counter readout
DigitalOut('pb_2',pb.direct_outputs, 'flag 2') #laser 
DigitalOut('pb_3',pb.direct_outputs, 'flag 3') #MW trigger
DigitalOut('pb_4',pb.direct_outputs, 'flag 4') #MW gate
DigitalOut('pb_6',pb.direct_outputs, 'flag 6') #MW gate


NI_PCIe_6343(name = 'Dev2',
    parent_device = pb_clockline,
    clock_terminal = '/Dev2/PFI5',
    MAX_name = 'Dev2',
    static_AO = True,
    stop_order = -1,
    acquisition_rate = 1e5
    )
StaticAnalogOut('anaout_0', Dev2, 'ao0') #dev2 is the NI DAq...RENAME
StaticAnalogOut('anaout_1', Dev2, 'ao1')
GatedCounterIn("myCounter", Dev2, connection = "ctr2", gate = "PFI1")#, numIterations = numIterations)
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
##############################
## END Connection table ##
##############################

##############################
## START SEQUENCE ##
##############################
t = 0  
add_time_marker(t, "Start", verbose = True)
start()

##############################
## set up instruments ##
##############################
Piezo.setamp(t, objPiezoHeight)

SRSDDS1.setamp(t, SRS_amp)
SRSDDS1.setfreq(t, freq_center)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_IQ(t)
SRSDDS2.enable_mod(t,False)


ZCUDDS.set_repetitions(t, '2')
ZCUDDS.set_delay_time(t,str(0)) #ejd why string? #us #6.447 + (60 - rabi_pulse_time)/1000
ZCUDDS.set_start_src(t, 'external')
ZCUDDS.add_TTL(4, 0, 10e-9) #ejd what is this?
if rabi_pulse_time == 0: #ejd can we delete?
    ZCUDDS.add_pulse(3,'buffer',5e-6+ 200e-9, rabi_pulse_time, 0,1000,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    ZCUDDS.add_pulse(4,'buffer',5e-6+ 200e-9, rabi_pulse_time, 0,1000,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  
else: #ejd where can I read about the gain 32766?
    #ZCUDDS.add_pulse(2,'buffer',5e-6+ 200e-9, rabi_pulse_time, 32766,100,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    ZCUDDS.add_pulse(5,'buffer',5e-6+ 200e-9, rabi_pulse_time, 32766,100,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    ZCUDDS.add_pulse(6,'buffer',5e-6+ 200e-9, rabi_pulse_time, 32766,100,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  


anaout_0.constant(V_laser_x)
anaout_1.constant(V_laser_y)  

t+=10e-6
add_time_marker(t,'laser on')
# pb_2.go_high(t) 
pb_1.go_high(t) #start reference counts
myCounter.acquire(numIterations=numIterations, label='ref')
pb_1.go_low(t+ctrGateDuration) #stop reference counts
# pb_2.go_low(t+polDuration) #laser turns off 

t+=polDuration+10e-6
add_time_marker(t,'FPGA on')
pb_3.go_high(t) #tells FPGA to output the loaded signal
t += 800e-9
add_time_marker(t,'FPGA off')
pb_3.go_low(t)
t += 0.860e-6 + 200e-9 + 4e-6
# t+=20e-5
add_time_marker(t,'MW switch on')
pb_4.go_high(t) #turn on MW switch
if rabi_pulse_time < 20:
    add_time_marker(t + 40e-9,'MW switch off')
    pb_4.go_low(t + 40e-9)
elif rabi_pulse_time-pulse_time_offset >= 0:
    add_time_marker(t + (rabi_pulse_time-pulse_time_offset)*(10**(-9)) + 24e-9,'MW switch off')
    pb_4.go_low(t + (rabi_pulse_time-pulse_time_offset)*(10**(-9)) + 24e-9) #turn it off

t += 5e-6
# pb_2.go_high(t)
# pb_2.go_low(t+polDuration)
pb_1.go_high(t) #start reference counts
myCounter.acquire(numIterations=numIterations, label='sig1')
pb_1.go_low(t+2*ctrGateDuration) #stop reference counts
t+=10e-6

pb_1.go_high(t) #start reference counts
myCounter.acquire(numIterations=numIterations, label='sig2')
pb_1.go_low(t+1.5*ctrGateDuration) #stop reference counts
t+=50e-6+polDuration

stop(t)