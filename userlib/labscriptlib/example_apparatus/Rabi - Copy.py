################################################################
######################CONNECTION TABLE##########################
################################################################
from labscript import *
from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
from labscript_devices.NI_DAQmx.models import NI_PCIe_6343
from labscript_devices.SRS384 import SRS384, SRS384DDS

   
######## Pulseblaster outputs ############
PulseBlasterESRPro500(name= 'pb', loop_number = numIterations,  extra_flags = 0, extra_inst = 3, extra_inst_data = 3, extra_length= 10, inst_location = 13, additional_inst = 8, loop_start = 1, board_number = 0, programming_scheme = 'pb_start/BRANCH')
ClockLine(name = "pb_clockline", pseudoclock = pb.pseudoclock, connection = "flag 0")
ClockLine(name = "pb_clockline_2", pseudoclock = pb.pseudoclock, connection = "flag 5")
DigitalOut('ctrGate',pb.direct_outputs, 'flag 1') #counter readout
DigitalOut('laser',pb.direct_outputs, 'flag 2') #laser 
DigitalOut('FPGATrig',pb.direct_outputs, 'flag 3') #MW trigger
DigitalOut('MWSwitch',pb.direct_outputs, 'flag 4') #MW gate

######## NI DAQ ############
NI_PCIe_6343(name = 'Dev2',
    parent_device = pb_clockline,
    clock_terminal = '/Dev2/PFI5',
    MAX_name = 'Dev2',
    static_AO = True,
    stop_order = -1,
    acquisition_rate = 1e5
    )
StaticAnalogOut('galvoX', Dev2, 'ao0')
StaticAnalogOut('galvoY', Dev2, 'ao1')

CounterIn("counter", Dev2, connection = "ctr2", CPT_connection = "PFI0", trigger = "PFI1", numIterations = numIterations)
#ctr 1 is cpt

DigitalOut('daq_dout_8', Dev2, 'port0/line8') 
DigitalOut('daq_dout_9', Dev2, 'port0/line9') 

######## FPGA ############
ZCU111(name = 'ZCU', parent_device = pb_clockline_2, com_port = 'COM5')
ZCU111DDS('ZCUDDS', ZCU, 'a')

######## OBJECTIVE PIEZO ############
'''PiezoEO(name = 'EO', parent_device = pb_clockline_2)
PiezoEODDS('Piezo', EO, 'a')'''

######## SRS ############
SRS384(name = 'SRS1', parent_device = pb_clockline_2, com_port = 'COM12')
SRS384DDS('SRSDDS1', SRS1, 'a1')
SRS384(name = 'SRS2', parent_device = pb_clockline_2, com_port = 'COM3')
SRS384DDS('SRSDDS2', SRS2, 'a2')
################################################################
######################END CONNECTION TABLE######################
################################################################


################################################################
######################VARIABLE DEFINITIONS##########################
################################################################
FPGADelay = 600e-9 #e-6

################################################################
###################### EXPERIMENT PULSE SEQUENCE################
################################################################
t = 0  
add_time_marker(t, "Start", verbose = True)
start()
counter.fast_counter(1e8, 2, 1)
#Piezo.setamp(t, 44)

################ Set SRS params #############
SRSDDS1.setamp(t, SRS_amp)
SRSDDS1.setfreq(t, freq_center)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_IQ(t)
SRSDDS2.enable_mod(t,False)

################# FPGA ######################
ZCUDDS.set_repetitions(t, '2')
ZCUDDS.set_delay_time(t,str(0)) #us #6.447 + (60 - rabi_pulse_time)/1000
ZCUDDS.set_start_src(t, 'external')
ZCUDDS.add_TTL(4, 0, 10e-9)
if rabi_pulse_time == 0:
    ZCUDDS.add_pulse(3,'buffer',0, rabi_pulse_time, 0,1000,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    ZCUDDS.add_pulse(4,'buffer',0, rabi_pulse_time, 0,1000,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  
else:
    #ZCUDDS.add_pulse(2,'buffer',5e-6+ 200e-9, rabi_pulse_time, 32766,100,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 

    ZCUDDS.add_pulse(5,'buffer',0, rabi_pulse_time, 32766,100,0,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _ 
    ZCUDDS.add_pulse(6,'buffer',0, rabi_pulse_time, 32766,100,90,'oneshot','product','[]') #channel, mode, start time, pulse length, gain, frequency, phase, _, _, _  


galvoX.constant(V_laser_x)
galvoY.constant(V_laser_y)  


laser.go_high(t) #laser
t += 2*polDuration 
ctrGate.go_high(t) #start reference counts
t += ctrDuration 
ctrGate.go_low(t) #stop reference counts
FPGATrig.go_high(t) #tells FPGA to output the loaded signal
laser.go_low(t) #laser turns off 
t += FGPADelay
FPGATrig.go_low(t)
MWSwitch.go_high(t) #turn on MW switch
if rabi_pulse_time < 20:
    MWSwitch.go_low(t + 40e-9)
elif rabi_pulse_time-pulse_time_offset >= 0:
    MWSwitch.go_low(t + (rabi_pulse_time-pulse_time_offset)*(10**(-9)) + 24e-9) #turn it off

t += 5e-6  

laser.go_high(t)
t += 210e-9#450e-9 #AOM Delay #AOM delay changed to 250 ns?...
ctrGate.go_high(t) #start signal counts
t += ctrDuration 
ctrGate.go_low(t) #end signal counts
t += 10e-6

ctrGate.go_high(t)
t += 6e-8
ctrGate.go_low(t)
t+= 6e-8
ctrGate.go_high(t)
t += 6e-8
ctrGate.go_low(t)
t+= 6e-8
ctrGate.go_high(t)
t += 6e-8
ctrGate.go_low(t)
t+= 6e-8
ctrGate.go_high(t)
t += 6e-8
ctrGate.go_low(t)
t+= 6e-8

stop(t)