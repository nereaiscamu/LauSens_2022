<<<<<<< Updated upstream
<<<<<<< Updated upstream
import serial.tools.list_ports
#import serial
import sys

list = serial.tools.list_ports.comports()
connected = []
for element in list:
    connected.append(element.device)
print("Connected COM ports: " + str(connected))
# compliments of https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python#14224477
""" Lists serial port names

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
"""
if sys.platform.startswith('win'):
# !attention assumes pyserial 3.x
    ports = ['COM%s' % (i + 1) for i in range(256)]
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    # this excludes your current terminal "/dev/tty"
    ports = glob.glob('/dev/tty[A-Za-z]*')
elif sys.platform.startswith('darwin'):
    ports = glob.glob('/dev/tty.*')
else:
    raise EnvironmentError('Unsupported platform')

result = []
for port in ports:
    try:
        s = serial.Serial(port)
        s.close()
        result.append(port)
    except (OSError, serial.SerialException):
        pass
=======
<<<<<<< Updated upstream
=======
>>>>>>> Stashed changes
import serial.tools.list_ports
#import serial
import sys

list = serial.tools.list_ports.comports()
connected = []
for element in list:
    connected.append(element.device)
print("Connected COM ports: " + str(connected))
# compliments of https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python#14224477
""" Lists serial port names

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
"""
if sys.platform.startswith('win'):
# !attention assumes pyserial 3.x
    ports = ['COM%s' % (i + 1) for i in range(256)]
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    # this excludes your current terminal "/dev/tty"
    ports = glob.glob('/dev/tty[A-Za-z]*')
elif sys.platform.startswith('darwin'):
    ports = glob.glob('/dev/tty.*')
else:
    raise EnvironmentError('Unsupported platform')

result = []
for port in ports:
    try:
        s = serial.Serial(port)
        s.close()
        result.append(port)
    except (OSError, serial.SerialException):
        pass
=======
import serial.tools.list_ports
#import serial
import sys

list = serial.tools.list_ports.comports()
connected = []
for element in list:
    connected.append(element.device)
print("Connected COM ports: " + str(connected))
# compliments of https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python#14224477
""" Lists serial port names

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
"""
if sys.platform.startswith('win'):
# !attention assumes pyserial 3.x
    ports = ['COM%s' % (i + 1) for i in range(256)]
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    # this excludes your current terminal "/dev/tty"
    ports = glob.glob('/dev/tty[A-Za-z]*')
elif sys.platform.startswith('darwin'):
    ports = glob.glob('/dev/tty.*')
else:
    raise EnvironmentError('Unsupported platform')

result = []
for port in ports:
    try:
        s = serial.Serial(port)
        s.close()
        result.append(port)
    except (OSError, serial.SerialException):
        pass
>>>>>>> Stashed changes
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
print("Availible COM Ports: " + str(result))