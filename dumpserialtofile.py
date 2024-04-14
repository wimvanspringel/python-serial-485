import serial

file_path = "./dumpserial.bin"
ser = serial.Serial('/dev/ttyUSB0',9600, timeout=10)  # open serial port, 9600, 8N1, blocking with 10 second timeout
print("Actual serial port name: ", ser.name)         # check which port was really used

# Flush the serial port
ser.read(ser.inWaiting())
counter=0

with open(file_path, "wb") as file:
    while True:
        x = ser.read() # read one byte (blocking with timeout)
        # print it in hex format with 0x 
        print('0x',x.hex(),' ',sep='', end='')
        # Every 16 bytes we print a line break       
        counter+=1
        if counter == 16 :
            print('')
            counter=0
        # Write it to a binary file
        file.write(x)    

