import serial

ser = serial.Serial('/dev/ttyUSB0',9600, timeout=10)  # open serial port, 9600, 8N1, blocking with 10 second timeout
print("Actual serial port name: ", ser.name)         # check which port was really used
counter=0
# flush the port
ser.read(ser.inWaiting())
x = ser.read() # read one byte (blocking with timeout)
while True:
    try:
        x = ser.read()
        print('0x',x.hex(),' ',sep='', end='')
        counter+=1
        if counter == 16 :
            print('')
            counter=0
        
    except:
        print("Exception (timeout)")
        break

