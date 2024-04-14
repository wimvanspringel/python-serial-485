import serial
from datetime import datetime

def crc16_modbus(data : bytes, cutend:int):
    if data is None or cutend>len(data):
        return 0
    
    crc = 0xFFFF
    for n in range(len(data)-cutend):
        crc ^= data[n]
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def crc_check(packet : bytes):
    calc_crc = crc16_modbus(packet, 2).to_bytes(2,'little')
    packet_crc = packet[len(packet)-2:len(packet)]
    if packet_crc==calc_crc:
        return True, calc_crc, packet_crc
    else:
        return False, calc_crc, packet_crc

def print_byte_packet(packet:bytes):
    if (PRINT_PACKET_HEADER):
        if PRINT_HEX_0X_MODE:
            # print it in hex format with 0x and spaces
            for i in range(len(packet)):
                byte = packet[i:i+1]
                print('0x',byte.hex(),' ',sep='', end='')    
        else:    
            # print in hex wo 0x and no spaces
            print(packet.hex(),sep='', end='')    
        print(PRINT_SEPARATOR,sep='', end='')

def print_byte_packet_forced(packet:bytes):
    if PRINT_HEX_0X_MODE:
        # print it in hex format with 0x and spaces
        for i in range(len(packet)):
            byte = packet[i:i+1]
            print('0x',byte.hex(),' ',sep='', end='')    
    else:    
        # print in hex wo 0x and no spaces
        print(packet.hex(),sep='', end='')    
    print(PRINT_SEPARATOR,sep='', end='')

def print_byte_packet_payload(my_bytes):
    if (PRINT_PACKET_PAYLOAD):
        if PRINT_HEX_0X_MODE:
            # print it in hex format with 0x and spaces
            for i in range(len(my_bytes)):
                byte = my_bytes[i:i+1]
                print('0x',byte.hex(),' ',sep='', end='')    
        else:    
            # print in hex wo 0x and no spaces
            print(my_bytes.hex(),sep='', end='')    
        print(PRINT_SEPARATOR,sep='', end='')

def print_deltatime_stamp():
    global gl_delta_time
    new_time=datetime.now()
    new_delta_time = new_time-gl_delta_time
    if PRINT_DELTATIME: print(new_delta_time, PRINT_SEPARATOR, sep='', end='')
    gl_delta_time = new_time

def print_starttime_stamp():
    global gl_start_time
    if PRINT_TIME_SINCE_START: print(datetime.now()-gl_start_time, PRINT_SEPARATOR, sep='', end='')

def print_datetime_stamp():
    if PRINT_TIMESTAMP: print(datetime.now(), PRINT_SEPARATOR, sep='', end='')

def print_packet_counter():
    if PRINT_PACKETCOUNT: print(str(gl_packet_counter), PRINT_SEPARATOR, sep='', end='')

def print_packet_crc(calc_crc:bytes,packet_crc:bytes):
    if PRINT_PACKET_CRC: print_byte_packet_forced(calc_crc)
    if PRINT_PACKET_CRC: print_byte_packet_forced(packet_crc)

def print_byte_counter():
    global gl_byte_counter
    global gl_delta_byte_counter
    delta_bytes = gl_byte_counter-gl_delta_byte_counter
    gl_delta_byte_counter=gl_byte_counter
    if PRINT_BYTECOUNT: 
        print(str(gl_byte_counter), PRINT_SEPARATOR, str(delta_bytes), PRINT_SEPARATOR, sep='', end='')

def print_line_header():
    if PRINT_TIMESTAMP: print("Date/Time", PRINT_SEPARATOR, sep='', end='')
    if PRINT_TIME_SINCE_START: print("Time since Start", PRINT_SEPARATOR, sep='', end='')
    if PRINT_DELTATIME: print("Time since Previous", PRINT_SEPARATOR, sep='', end='')
    if PRINT_BYTECOUNT: print("Byte Counter", PRINT_SEPARATOR,"Byte Diff Counter", PRINT_SEPARATOR, sep='', end='')
    if PRINT_PACKETCOUNT: print("Packet Counter", PRINT_SEPARATOR, sep='', end='')
    print("Header Info", PRINT_SEPARATOR, sep='', end='')
    if PRINT_PACKET_HEADER: print("Packet Header", PRINT_SEPARATOR, sep='', end='')
    if PRINT_PACKET_PAYLOAD: print("Packet Payload", PRINT_SEPARATOR, sep='', end='')
    if PRINT_PACKET_CRC: print("Calc CRC", PRINT_SEPARATOR,"Packet CRC", PRINT_SEPARATOR, sep='', end='')
    print('')

def print_line_stamp():
    print_datetime_stamp()
    print_starttime_stamp()
    print_deltatime_stamp()
    print_byte_counter()
    print_packet_counter()

def print_line (string_value):
    print_line_stamp()
    print(string_value,PRINT_SEPARATOR, sep='')

def found_unknownheader(packet):
    global gl_unknownheaders_count
    gl_unknownheaders_count += 1
    global gl_packet_counter
    gl_packet_counter+=1

    print_line_stamp()
    print('*ERR: UNKNOWN*)', PRINT_SEPARATOR, sep='', end='')
    print_byte_packet_forced(packet)
    print('')

def found_slavepacketwomaster(packet, p_index):
    global gl_slavepacketswomaster_count
    gl_slavepacketswomaster_count += 1
    global gl_packet_counter
    gl_packet_counter+=1
    
    print_line_stamp()
    print(knownheaders[p_index][1], '(*ERR: SLAVE WITHOUT MASTER*)', PRINT_SEPARATOR, sep='', end='')
    print_byte_packet(packet)
    print('')

def found_masterwhenslaveexpected(packet, p_index):
    global gl_masterwhenslaveexpected_count
    gl_masterwhenslaveexpected_count += 1
    global gl_packet_counter
    gl_packet_counter+=1
    
    print_line_stamp()
    print(knownheaders[p_index][1], '(*ERR: MASTER WHEN SLAVE EXPECTED*)', PRINT_SEPARATOR, sep='', end='')
    print_byte_packet(packet)
    print('')

def found_wrongslavereceived(packet, p_index):
    global gl_wrongslavereceived_count
    gl_wrongslavereceived_count += 1
    global gl_packet_counter
    gl_packet_counter+=1
    
    print_line_stamp()
    print(knownheaders[p_index][1], '(*ERR: UNEXPECTED SLAVE*)', PRINT_SEPARATOR, sep='', end='')
    print_byte_packet(packet)
    print('')

def print_crc_error(packet:bytes, calc_crc:bytes, packet_crc:bytes):
    print_line_stamp()
    print('*ERR: CRC ERROR*', PRINT_SEPARATOR, sep='', end='')
    print_byte_packet_forced(packet)
    print_byte_packet_forced(calc_crc)
    print_byte_packet_forced(packet_crc)
    print('')

def log_masterpacket(header:bytes, payload:bytes, p_index:int):
    global gl_packet_counter
    gl_packet_counter+=1

    print_line_stamp()
    print(knownheaders[p_index][1], PRINT_SEPARATOR, sep='', end='')
    print_byte_packet(header)
    if (payload):
        print_byte_packet_payload(payload)

    crc_good,calc_crc,packet_crc= crc_check(header+payload)
    print_packet_crc(calc_crc,packet_crc)
    print('')
    
    if (crc_good==False):
        print_crc_error(header+payload, calc_crc,packet_crc)

def log_slavepacket(header, payload, p_index):
    global gl_packet_counter
    gl_packet_counter+=1

    print_line_stamp()
    print(knownheaders[p_index][1], PRINT_SEPARATOR, sep='', end='')
    print_byte_packet(header)
    if (payload):
        print_byte_packet_payload(payload)
    
    crc_good,calc_crc,packet_crc= crc_check(header+payload)
    print_packet_crc(calc_crc,packet_crc)
    print('')
    
    if (crc_good==False):
        print_crc_error(header+payload, calc_crc,packet_crc)

def read_bytes(read_file, read_nr_bytes):
    global gl_byte_counter
    read_EOF=True
    read_buf=None
    read_buf=read_file.read(read_nr_bytes)
    if (read_buf!=None) and (len(read_buf)==read_nr_bytes):
        gl_byte_counter+=read_nr_bytes
        read_EOF=False
    return read_EOF, read_buf

def loop_over_headers(packet):
    packet_index = -1
    slave_index = -1
    for j in range(len(knownheaders)):
        index = packet.find(knownheaders[j][0])
        if index != -1:  # Check if this header is known
            # Known header found - now check if it is a master
            slave_index=knownheaders[j][3]
            packet_index = j
            # No need to continue looping as we have found a match
            return True,packet_index,slave_index
    return False,packet_index,slave_index
    

knownheaders = [
    #       8-byte packet start (always expected unique)      Text       Length, Response packet
    [bytes([0x01, 0x03, 0x0b, 0xb9, 0x00, 0x1e, 0x16, 0x03]), "MA_1",         8,  1], # Master 1: ? Addressing display unit ?
    [bytes([0x01, 0x03, 0x3c, 0x57, 0x46, 0x32, 0x30, 0x30]), "SL_1",        65, -1], # Slave  1: 65 byte response 
    [bytes([0x01, 0x03, 0x3c, 0x00, 0x00, 0x00, 0x00, 0x00]), "SL_1_B",      65, -1], # Slave  1B: Alternate 65-byte response
    [bytes([0x02, 0x03, 0x0b, 0xb9, 0x00, 0x1e, 0x16, 0x30]), "MA_2",         8,  4], # Master 2: ? Addressing compressor unit 
    [bytes([0x00, 0x10, 0x07, 0xd1, 0x00, 0x5a, 0xb4, 0x57]), "SL_2",       189, -1], # Slave  2: 189 byte response
    [bytes([0X01, 0x10, 0x03, 0xe9, 0x00, 0x5a, 0xb4, 0x57]), "MA_3",       189,  6], # Master 3: Display packet 1
    [bytes([0x01, 0x10, 0x03, 0xe9, 0x00, 0x5a, 0x91, 0x82]), "SL_3",         8, -1], # Slave  3: respones (8-byte acq)
    [bytes([0x01, 0x10, 0x04, 0x43, 0x00, 0x5a, 0xb4, 0x57]), "MA_4",       189,  8], # Master 4: Display packet 2
    [bytes([0x01, 0x10, 0x04, 0x43, 0x00, 0x5a, 0xb0, 0xd6]), "SL_4",         8, -1], # Slave  4: respones (8-byte acq)
    [bytes([0x01, 0x10, 0x0b, 0xb9, 0x00, 0x0b, 0x16, 0x57]), "MA_5",        31, 10], # Master 5: Display packet 3
    [bytes([0x01, 0x10, 0x0b, 0xb9, 0x00, 0x0b, 0x52, 0x0f]), "SL_5",         8, -1], # Slave  5: respones (8-byte acq)
    [bytes([0x01, 0x03, 0x03, 0xe9, 0x00, 0x5a, 0x14, 0x41]), "MA_6",         8, 12], # Master 6: Addressing display unit
    [bytes([0x01, 0x03, 0xb4, 0x57, 0x46, 0x32, 0x30, 0x30]), "SL_6",       185, -1], # Slave  6: 185 byte response
    [bytes([0x02, 0x10, 0x03, 0xe9, 0x00, 0x5a, 0xb4, 0x57]), "MA_7",       189, 18], # Master 7 with no observed slave response
    [bytes([0x00, 0x10, 0x03, 0xe9, 0x00, 0x5a, 0xb4, 0x57]), "MA_8",       189,  4], # Master 8 with observed slave 2 response
    [bytes([0x01, 0x03, 0x04, 0x43, 0x00, 0x5a, 0x35, 0x15]), "MA_9",         8, 12], # Master 9 with observed slave 6 response
    [bytes([0x02, 0x10, 0x04, 0x43, 0x00, 0x5a, 0xb4, 0x57]), "MA_10",      189, 18], # Master 10 with no observed slave response
    [bytes([0x00, 0x10, 0x04, 0x43, 0x00, 0x5a, 0xb4, 0x57]), "MA_11",      189,  4], # Master 11 with observed slave 2 response
    [bytes([0x01, 0x03, 0x0b, 0xb9, 0x00, 0x1e, 0x16, 0x03]), "SL_NO_REPLY",  8, -1] # Slave not responding, only there to catch new master tx
]

# Global packet counters
gl_slavepacketswomaster_count = 0
gl_unknownheaders_count = 0 
gl_masterwhenslaveexpected_count = 0 
gl_wrongslavereceived_count = 0
gl_packet_counter=0
gl_byte_counter=0
gl_delta_byte_counter=0
gl_delta_time=datetime.now()
gl_start_time=datetime.now()

# Global state variables for processing
END_OF_FILE=False   # State variable to indicate end of file reached
SYNC=False          # State variable to indicate processing found a known masterpacket header 

# Global Print configuration settings
PRINT_HEX_0X_MODE=False     # if True print hex with 0x and spaces in between
PRINT_PACKET_HEADER=True   # State variable to print out packet headers as they come in
PRINT_PACKET_PAYLOAD=True   # State variable to print out packet headers as they come in
PRINT_PACKETCOUNT=True
PRINT_PACKET_CRC=True
PRINT_SEPARATOR=', '
PRINT_TIMESTAMP=True
PRINT_DELTATIME=True
PRINT_TIME_SINCE_START=True
PRINT_BYTECOUNT=True

file_path = "./dumpserial.bin"

# for i in range(len(knownheaders)):
#    print('- ', sep='', end='')
#    print(knownheaders[i][1],' : ', sep='', end='')
#    print('size: ', knownheaders[i][2], ', header : ', sep='', end='')
#    print_byte_packet_forced(knownheaders[i][0])
#    print('')

print_line_header()
print_line("START PROGRAM WITH "+str(len(knownheaders))+" HEADERS KNOWN")

serial_file = serial.Serial('/dev/ttyUSB0',9600, timeout=None)  # open serial port, 9600, 8N1, blocking with 10 second timeout
while True:
#with open(file_path, "rb") as serial_file:
    # Keep going until serial port breaks or file ends
    while END_OF_FILE==False:
        # This is the start of the SEEKING part, read enough bytes until we find a known masterpacket header
        # If that is found, we go into the main SYNC loop with a SYNC = True
        SYNC=False
        print_line ("SEEK_START")

        # Reset global packet variables
        masterpacket_index = -1
        masterpacket_header_present = False
        masterpacket_header = b''
        slavepacket_index = -1
        slavepacket_header = b''

        # We start by reading 8 bytes 
        END_OF_FILE, newbuf=read_bytes(serial_file,8)
        if END_OF_FILE:
            SYNC=False
            break

        while SYNC==False:
            # Seek for first known master packet header in newbuf by checking for every known header
            found=False
            found,masterpacket_index,slavepacket_index=loop_over_headers(newbuf)
            if (found==True):
                if slavepacket_index == -1:
                    # We found a slave packet during seek, so keep seeking
                    found_slavepacketwomaster(newbuf,masterpacket_index)
                else:
                    # Known master packet header found 
                    SYNC=True
            
            # If we havent found a known master packet header yet, read the next byte and loop again
            if SYNC==False:
                # Read the next byte 
                END_OF_FILE, nextbyte=read_bytes(serial_file,1)
                if END_OF_FILE:
                    break
                # And put that byte into the newbuf
                newbuf=newbuf[1:8]+nextbyte
        
            
        # if we get here with no sync, this is the EOF without finding a known masterpacket header
        if (SYNC == False):
            break
        
        masterpacket_header_present = True
        masterpacket_header = newbuf

        # This is the main SYNC loop: first process master packet, then process slave, repeat ...
        # if anything is not in sequence as expected we bump out with SYNC = False and go back to main SEEKING loop
        while SYNC==True:
            # ************** MASTER packet handling MASTER **************
            # It is possible that the next masterpacket is already read (eg. first time or found during slave response processing
            # That state is indicated with the masterpacket_header_present flag
            if (masterpacket_header_present==False):
                # Reset global packet variables
                masterpacket_index = -1
                masterpacket_header = b''
                slavepacket_index = -1
                slavepacket_header = b''

                # Read next expected masterpacket header
                END_OF_FILE, newbuf=read_bytes(serial_file,8)
                if END_OF_FILE:
                    SYNC=False
                    break

                # check if these 8 bytes are a known masterpacket header, otherwise we have to go back seeking sync
                found=False
                found,masterpacket_index,slavepacket_index=loop_over_headers(newbuf)
                if (found==True):
                    # We have found a known header
                    if slavepacket_index != -1:
                        # Found: New known masterpacket_header 
                        masterpacket_header_present = True
                        masterpacket_header = newbuf
                    else: 
                        # Found: Known slavepacket header while we expected a masterpacket header, go back to SEEKING
                        found_slavepacketwomaster(newbuf, masterpacket_index)
                        SYNC=False
                else: 
                    # We have found an unknown header
                    found_unknownheader(newbuf)
                    SYNC = False

            # Break out of SYNC while loop if anything was unexpected, back to SEEKING
            if SYNC==False:
                break
            

            # There may still be remaining payload in the master packet
            masterpacket_size=knownheaders[masterpacket_index][2]
            if masterpacket_size > 8:
                # Read remaining payload
                END_OF_FILE, masterpacket_payload=read_bytes(serial_file,masterpacket_size-8)
                if END_OF_FILE:
                    SYNC=False
                    break
            else:
                masterpacket_payload = b''

            # LOG MASTER PACKET 
            log_masterpacket(masterpacket_header, masterpacket_payload, masterpacket_index)    

            # ************** SLAVE packet handling SLAVE **************
            # We know have a known and read a masterpacke, set the expected slave now
          
            # Read next expected slavepacket header
            END_OF_FILE, newbuf=read_bytes(serial_file,8)
            if END_OF_FILE:
                SYNC=False
                break            

            # Process these 8 bytes
            packet_index = -1
            sl_packet_index = -1
            
            found=False
            found,packet_index,sl_packet_index=loop_over_headers(newbuf)
            if (found==True):
                # We have found a known header
                if sl_packet_index != -1:
                    # We found a known masterpacket header, while we expected a slave !
                    found_masterwhenslaveexpected(newbuf, slavepacket_index)
                    # But since this is a known masterpacket header, we just skip the slave packet processing
                    # and stay in SYNC = True!!
                    masterpacket_index = packet_index
                    masterpacket_header_present = True
                    masterpacket_header = newbuf
                    slavepacket_index = sl_packet_index
                else: 
                    # We found a known slavepacket header
                    slavepacket_header=newbuf
                    
                    # First check if it is the expected
                    if (packet_index != slavepacket_index):
                        # It is an unexpected slave 
                        slavepacket_index=packet_index
                        # Log the unexpected slave packet
                        found_wrongslavereceived(newbuf, packet_index)
                    
                    # There may still be remaining payload in the slave packet
                    slavepacket_size=knownheaders[slavepacket_index][2]
                    if slavepacket_size > 8:
                        # Read remaining payload
                        END_OF_FILE, slavepacket_payload=read_bytes(serial_file,slavepacket_size-8)
                        if END_OF_FILE:
                            SYNC=False
                            break            
                    else:
                        slavepacket_payload=b''

                    # Log the full slave packet 
                    log_slavepacket(slavepacket_header,slavepacket_payload,slavepacket_index)
                    
                    # Processing of master and slave is done, back to SYNC start of processing
                    masterpacket_header_present = False

            else: 
                # We have found an unknown header, log it and back to SEEKING
                found_unknownheader(newbuf)
                SYNC = False

# End of Program
print_line("END PROGRAM")




