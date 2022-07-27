from sangaboard import Sangaboard
import serial 
import time

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

def foward():
    arduino.write("xfw 100\n".encode("ascii"))
    time.sleep(0.05)

def backward():
    arduino.write("xbw 100\n".encode("ascii"))
    time.sleep(0.05)

def set_step(step):
    arduino.write(str(step).encode("ascii"))
    time.sleep(0.05)


focus = True
saved_x = 100
while (focus):
    print("Step focus")
    x = input()
    if x.isdigit() == False or int(x) <= 0:
        x = saved_x
    set_step(x)
    saved_x = x

    # test
    time.sleep(1)
    data = arduino.readlines()
    print(data)

    print("Focus : Forward (F), Backward (B), Done (D) ?")
    x = input()
    if x == "F" or x == "f":
        foward()
    elif x == "B" or x == "b":
        backward()
    else:
        focus = False
    
    # test
    time.sleep(1)
    data = arduino.readlines()
    print(data)
    
arduino.flushInput()
arduino.flushOutput()
arduino.close()