#!/usr/bin/env python
# coding: utf-8

# In[1]:


import serial
from serial import Serial
import numpy as np
from matplotlib import pyplot as plt
import serial.tools.list_ports as port_list
import seaborn as sns
import time
import codecs


# In[2]:


ser = serial.Serial()


# In[3]:


#TPI-1002-A Parameters
baud_rate=3000000
port='/dev/tty.usbserial-DM00ZI4H' #Port
byte_size=8
stop_bits=2
parity='N'
timeout=1
count=1


# # Initialization

# In[ ]:


#In order to run any commands, the DDS must be initialized with this code. 
with serial.Serial(port=port, baudrate=baud_rate, bytesize=byte_size, timeout=timeout, stopbits=stop_bits, parity=parity) as ser:
     ser.write(serial.to_bytes([0xAA, 0x55, 0x00, 0x02, 0x08, 0x01, 0xF4])


# # Command Sequence

# In[14]:


#num_of_runs=5

#Starting Values
start_frequency=85000 #Set to MHz * 1000 (ex. 85000 = 85 MHz)
start_power=-20 #dBm - DO NOT EXCEED -10 dBm

#for p in range(num_of_runs):
#start_frequency=start_frequency+1000
#start_power=start_power+1
if(start_power>2):
    raise Exception("Power is greater than +2 dBm")
    
#if(start_frequency!=85000):
#    raise Exception("Frequency is not set to 85.000 MHz")
        
    
#INPUT
commands=[[0x08, 0x01], #Initialize
          [0x08,0x09]+list((start_frequency).to_bytes(4,"little")), #Set Frequency
          [0x08,0x0A]+list((start_power).to_bytes(1,"little",signed="True")), #Set Power
          [0x08, 0x0B, 1], #RF On
          [0x07, 0x0A], #Read Power
          [0x07,0x09], #Read Frequency
          ['wait', 10], #Wait, int value seconds to wait
          [0x08, 0x0B, 0], #RF Off
          ['wait', 1] 
         ]
in_commands=[]
for i in range(len(commands)):
    if(commands[i][0]=='wait'):
        in_commands.append(commands[i])
    else:
        checksum=0xff-sum(commands[i],len(commands[i]))
#         checksum=np.int32(0xff-sum(commands[i],len(commands[i])))
        if(checksum>-1):
            entry=[0xAA,0x55,0x00]+[len(commands[i])]+commands[i]+[checksum]
        else:
            print(checksum)
            if(checksum>3):
                entry=[0xAA,0x55,0x00]+[len(commands[i])]+commands[i]+list((checksum).to_bytes(4,"little",signed="True"))
            else:
                entry=[0xAA,0x55,0x00]+[len(commands[i])]+commands[i]+list((checksum).to_bytes(1,"little",signed="True"))
#               entry=[0xAA,0x55,0x00]+[len(commands[i])]+commands[i]+list((checksum).to_bytes(1,"little",signed="True"))
        in_commands.append(entry)


#EXECUTION
print("Frequency is set to " + str(start_frequency/1000) + " MHz.\n")
print("Power is set to " + str(start_power) + " dBm.\n\n")
with serial.Serial(port=port, baudrate=baud_rate, bytesize=byte_size, timeout=timeout, stopbits=stop_bits, parity=parity) as ser:
    for i in range(len(commands)):
        if(in_commands[i][0]=='wait'):
            print("Waiting " + str(in_commands[i][1]) + " seconds!\n") 
            time.sleep(in_commands[i][1])
        else:
            ser.write(serial.to_bytes(in_commands[i]))
            x=ser.readline(6)
            s = ser.readlines()
            print("Command "+str(i+1)+":")
            print(s)
            if(len(s[0])>1):
                nums=list(s[0])
                nums.pop()
                val=int.from_bytes(serial.to_bytes(nums),"little",signed="True")
                if(val>1000):
                    print("Frequency is currently " + str(val/1000) + " MHz")
                else:
                    print("Power is currently " + str(val) + " dBm")

            print("\n")

ser.close()
print("Run " + str(count) + " completed!")


# In[29]:


list((checksum).to_bytes(1,"little",signed="True"))


# # Set Power

# In[63]:


power=1

commands=[0x08,0x0A]+list((power).to_bytes(1,"little",signed="True"))
checksum=0xff-sum(commands,len(commands))
if(checksum>-1):
    entry=[0xAA,0x55,0x00]+[len(commands)]+commands+[checksum]
else:
    entry=[0xAA,0x55,0x00]+[len(commands)]+commands+list((checksum).to_bytes(1,"little",signed="True"))

#print(entry)
with serial.Serial(port=port, baudrate=baud_rate, bytesize=byte_size, timeout=timeout, stopbits=stop_bits, parity=parity) as ser:
    ser.write(serial.to_bytes(entry))


# # Read Power

# In[64]:


with serial.Serial(port=port, baudrate=baud_rate, bytesize=byte_size, timeout=timeout, stopbits=stop_bits, parity=parity) as ser:
    ser.write(serial.to_bytes([170, 85, 0, 2, 7, 10, 236]))
    x=ser.readline(6)
    s = ser.readlines()
    #print(s)
    if(len(s[0])>1):
        nums=list(s[0])
        nums.pop()
        val=int.from_bytes(serial.to_bytes(nums),"little",signed="True")
        print("Power is currently " + str(val) + " dBm")


# # On

# In[89]:


with serial.Serial(port=port, baudrate=baud_rate, bytesize=byte_size, timeout=timeout, stopbits=stop_bits, parity=parity) as ser:
    ser.write(serial.to_bytes([170, 85, 0, 3, 8, 11, 1, 232]))

print("On")


# e###### Off

# In[90]:


with serial.Serial(port=port, baudrate=baud_rate, bytesize=byte_size, timeout=timeout, stopbits=stop_bits, parity=parity) as ser:
    ser.write(serial.to_bytes([170, 85, 0, 3, 8, 11, 0, 233]))
print("Off")


# In[ ]:




