from labscript import *
from labscript_devices.PulseBlasterESRPro500 import PulseBlasterESRPro500
from labscript_devices.ZCU111 import ZCU111, ZCU111DDS
from labscript_devices.PiezoEO import PiezoEO, PiezoEODDS
from labscript_devices.NI_DAQmx.models import NI_PCIe_6343
from labscript_devices.SRS384 import SRS384, SRS384DDS


##############################
## Connection table ##
##############################
PulseBlasterESRPro500(name= 'pb', loop_number = numIterations)#,  extra_flags = 0, extra_inst = 3, extra_inst_data = 3, extra_length= 10, inst_location = 0, additional_inst = 0, loop_start = 1, board_number = 0, programming_scheme = 'pb_start/BRANCH')
#PulseBlasterESRPro500(name= 'pb', loop_number = numIterations,  extra_flags = 3, extra_inst = 3, extra_inst_data = 3, extra_length= 10, inst_location = 13, additional_inst = 8, loop_start = 1, board_number = 0, programming_scheme = 'pb_start/BRANCH')
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
counter_gate_time = 5e-6      # original value is 500e-9
counter.fast_counter(1e8, 2, 1) #original value is (1e8, 2, 1)
Piezo.setamp(t, 100)
SRSDDS1.setamp(t, SRS_amp)
SRSDDS1.setfreq(t, freq_center)
SRSDDS1.enable_mod(t, True)
SRSDDS1.enable_IQ(t)
SRSDDS2.enable_mod(t,False)
'''SRSDDS2.setamp(t, SRS_amp)
SRSDDS2.setfreq(t, 3497)
SRSDDS2.enable_mod(t, True)
SRSDDS2.enable_IQ(t)
SRSDDS1.enable_mod(t, False)'''

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

# t += 20e-9

# # add_time_marker(t,'laser on')
# pb_2.go_high(t) #laser # this line and pb_2.go_low should be uncommented when running
# # # t += 20e-6 #original value was 20e-6
# # add_time_marker(t + ref_count_offset,'counter on')
# pb_1.go_high(t) #start reference counts
# t+= 20e-6
# # # t += 20e-6 #original value was 20e-6
# # # t += counter_gate_time
# # # t += 5e-6 
# # # 
# # # pb_3.go_high(t) #tells FPGA to output the loaded signal
# # # t += 1e-6#800e-9
# # # 
# # # pb_3.go_low(t)
# # # 
# pb_1.go_low(t) #stop reference counts
# # # 
# pb_2.go_low(t) #laser turns off 

# t+= 5e-6

add_time_marker(t,'laser on')
pb_2.go_high(t) #laser # this line and pb_2.go_low should be uncommented when running
t += 20e-6 #original value was 20e-6
add_time_marker(t+delay,'counter on')
pb_1.go_high(t+delay) #start reference counts
t += counter_gate_time
add_time_marker(t+delay,'counter off')
pb_1.go_low(t+delay) #stop reference counts
t += 5e-6
add_time_marker(t,'FPGA on')
pb_3.go_high(t) #tells FPGA to output the loaded signal
t += 800e-9
add_time_marker(t,'FPGA off')
pb_3.go_low(t)
add_time_marker(t,'laser off')
pb_2.go_low(t) #laser turns off 

t += 0.860e-6 + 200e-9 + 4e-6
t+=20e-5
add_time_marker(t,'MW switch on')
pb_4.go_high(t) #turn on MW switch
if rabi_pulse_time < 20:
    add_time_marker(t + 40e-9,'MW switch off')
    pb_4.go_low(t + 40e-9)
elif rabi_pulse_time-pulse_time_offset >= 0:
    add_time_marker(t + (rabi_pulse_time-pulse_time_offset)*(10**(-9)) + 24e-9,'MW switch off')
    pb_4.go_low(t + (rabi_pulse_time-pulse_time_offset)*(10**(-9)) + 24e-9) #turn it off

t += 5e-6

add_time_marker(t,'laser on')
pb_2.go_high(t) #(this should be uncommented when running)
t += 500e-9 #450e-9 #AOM Delay #AOM delay changed to 250 ns?... or 210 ns?
add_time_marker(t,'counter on')
pb_1.go_high(t) #start signal counts
t += counter_gate_time
add_time_marker(t,'counter off')
pb_1.go_low(t) #end signal counts
pb_2.go_low(t)
t += 12.34e-5
# pb_2.go_low(t) # this was not originally present; remove after debugging complete

# pb_1.go_high(t)
# t += 6e-8
# pb_1.go_low(t)
# t+= 6e-8
# pb_1.go_high(t)
# t += 6e-8
# pb_1.go_low(t)
# t+= 6e-8
# pb_1.go_high(t)
# t += 6e-8
# pb_1.go_low(t)
# t+= 6e-8
# pb_1.go_high(t)
# t += 6e-8
# pb_1.go_low(t)
# t+= 6e-8

stop(t)