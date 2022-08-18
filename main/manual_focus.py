from sangaboard import Sangaboard
import serial 
import time
import sys

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)
print(arduino)
time.sleep(2)

"""
def write_read():
    arduino.write("xbw 100\n".encode("ascii"))
    time.sleep(1)
    data = arduino.readlines()
    return data
"""

def move(com):
    arduino.write(com.encode("ascii"))
    time.sleep(0.05)

focus = True
saved_focus = 100
saved_axis = "z"
saved_direction = "fw"

while (focus):
    com = "04 "
    print("Step focus or quit (q)")
    x = input()
    if x == "q" or x == "quit":
        focus = False
        sys.exit()
    if x.isdigit() == False or int(x) <= 0:
        x = saved_focus
    saved_focus = x
    com += str(x).zfill(4) + " "
    print("Axis (x/y/z)")
    x = input()
    if (x == "x" or x == "y" or x == "z") == False:
        x = saved_axis
    saved_axis = x
    com += x
    print("Direction (fw/bw)")
    x = input()
    if (x == "fw" or x == "bw") == False:
        x = saved_direction
    saved_direction = x
    com += x
    print(com)
    move(com)

    # test
    # time.sleep(1)
    # data = arduino.readlines()
    # print(data)
    
arduino.flushInput()
arduino.flushOutput()
arduino.close()