from datetime import datetime

class bcolors:
    HEADER = '\033[95m'
    PACKETDIFF = '\033[30;42m'
    REDBG = '\033[30;41m'
    GREENBG = '\033[30;42m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print_colored = True

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

def read_bytes(read_file, read_nr_bytes):
    global gl_byte_counter
    read_EOF=True
    read_buf=None
    read_buf=read_file.read(read_nr_bytes)
    if (read_buf is not None) and (len(read_buf)==read_nr_bytes):
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

def print_packet_header(packet:bytes):
    if (PRINT_PACKET_HEADER):
        print_packet(packet)

def print_packet_payload(packet:bytes):
    if (PRINT_PACKET_PAYLOAD):
        print_packet(packet)

def print_packet(packet:bytes):
    if PRINT_HEX_0X_MODE:
        # print it in hex format with 0x and spaces
        for i in range(len(packet)):
            byte = packet[i:i+1]
            print('0x',byte.hex(),' ',sep='', end='')    
    else:    
        # print in hex wo 0x and no spaces
        print(packet.hex(),sep='', end='')    
    print(PRINT_SEPARATOR,sep='', end='')

def print_packet_mask(packet:bytes, packet_previous:bytes, mask):
    for i in range(len(packet)):
        if i in mask:
            byte=packet[i:i+1]
            byte_previous=packet_previous[i:i+1]
            if byte==byte_previous:
                print(byte.hex(), ' ', end='', sep='')
            else:
                if print_colored:
                    print(bcolors.PACKETDIFF,byte.hex(), bcolors.ENDC, ' ', end='', sep='')
                else:
                    print(byte.hex(), ' ', end='', sep='')

def print_deltatime_stamp():
    global gl_delta_time
    new_time=datetime.now()
    new_delta_time = new_time-gl_delta_time
    if PRINT_DELTATIME: 
        print(new_delta_time, PRINT_SEPARATOR, sep='', end='')
    gl_delta_time = new_time

def print_starttime_stamp():
    global gl_start_time
    if PRINT_TIME_SINCE_START: 
        print(datetime.now()-gl_start_time, PRINT_SEPARATOR, sep='', end='')

def print_datetime_stamp():
    if PRINT_TIMESTAMP: 
        print(datetime.now(), PRINT_SEPARATOR, sep='', end='')

def print_packet_counter():
    if PRINT_PACKETCOUNT: 
        print(str(gl_packet_counter), PRINT_SEPARATOR, sep='', end='')

def print_packet_crc(calc_crc:bytes,packet_crc:bytes):
    if PRINT_PACKET_CRC: 
        print_packet(calc_crc)
    if PRINT_PACKET_CRC: 
        print_packet(packet_crc)

def print_byte_counter():
    global gl_byte_counter
    global gl_delta_byte_counter
    delta_bytes = gl_byte_counter-gl_delta_byte_counter
    gl_delta_byte_counter=gl_byte_counter
    if PRINT_BYTECOUNT: 
        print(str(gl_byte_counter), PRINT_SEPARATOR, str(delta_bytes), PRINT_SEPARATOR, sep='', end='')

def print_line_header():
    if PRINT_TIMESTAMP: 
        print("Date/Time", PRINT_SEPARATOR, sep='', end='')
    if PRINT_TIME_SINCE_START: 
        print("Time since Start", PRINT_SEPARATOR, sep='', end='')
    if PRINT_DELTATIME: 
        print("Time since Previous", PRINT_SEPARATOR, sep='', end='')
    if PRINT_BYTECOUNT: 
        print("Byte Counter", PRINT_SEPARATOR,"Byte Diff Counter", PRINT_SEPARATOR, sep='', end='')
    if PRINT_PACKETCOUNT: 
        print("Packet Counter", PRINT_SEPARATOR, sep='', end='')
    print("Header Info", PRINT_SEPARATOR, sep='', end='')
    if PRINT_PACKET_HEADER: 
        print("Packet Header", PRINT_SEPARATOR, sep='', end='')
    if PRINT_PACKET_PAYLOAD: 
        print("Packet Payload", PRINT_SEPARATOR, sep='', end='')
    if PRINT_PACKET_CRC: 
        print("Calc CRC", PRINT_SEPARATOR,"Packet CRC", PRINT_SEPARATOR, sep='', end='')
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

def log_unknownpacket(packet):
    global gl_unknownheaders_count
    gl_unknownheaders_count += 1
    global gl_packet_counter
    gl_packet_counter+=1

    print_line_stamp()
    print('*ERR: UNKNOWN*)', PRINT_SEPARATOR, sep='', end='')
    print_packet(packet)
    print('')

def log_slavewomaster(packet, p_index):
    global gl_slavepacketswomaster_count
    gl_slavepacketswomaster_count += 1
    global gl_packet_counter
    gl_packet_counter+=1
    
    print_line_stamp()
    print(knownheaders[p_index][1], '(*ERR: SLAVE WITHOUT MASTER*)', PRINT_SEPARATOR, sep='', end='')
    print_packet_header(packet)
    print('')

def log_masterwhenslaveexpected(packet, p_index):
    global gl_masterwhenslaveexpected_count
    gl_masterwhenslaveexpected_count += 1
    global gl_packet_counter
    gl_packet_counter+=1
    
    print_line_stamp()
    print(knownheaders[p_index][1], '(*ERR: MASTER WHEN SLAVE EXPECTED*)', PRINT_SEPARATOR, sep='', end='')
    print_packet_header(packet)
    print('')

def log_crc_error(packet:bytes, calc_crc:bytes, packet_crc:bytes):
    print_line_stamp()
    print('*ERR: CRC ERROR*', PRINT_SEPARATOR, sep='', end='')
    print_packet(packet)
    print_packet(calc_crc)
    print_packet(packet_crc)
    print('')

def log_wrongslave(packet, p_index):
    global gl_wrongslavereceived_count
    gl_wrongslavereceived_count += 1
    global gl_packet_counter
    gl_packet_counter+=1
    
    print_line_stamp()
    print(knownheaders[p_index][1], '(*ERR: UNEXPECTED SLAVE*)', PRINT_SEPARATOR, sep='', end='')
    print_packet_header(packet)
    print('')

def log_masterpacket(header:bytes, payload:bytes, p_index:int):
    global gl_packet_counter
    gl_packet_counter+=1

    print_line_stamp()
    print(knownheaders[p_index][1], PRINT_SEPARATOR, sep='', end='')
    print_packet_header(header)
    if (payload):
        print_packet_payload(payload)

    crc_good,calc_crc,packet_crc= crc_check(header+payload)
    print_packet_crc(calc_crc,packet_crc)
    print('')
    
    if (crc_good is False):
        log_crc_error(header+payload, calc_crc,packet_crc)

def log_slavepacket(header, payload, p_index):
    global gl_packet_counter
    gl_packet_counter+=1

    print_line_stamp()
    print(knownheaders[p_index][1], PRINT_SEPARATOR, sep='', end='')
    print_packet_header(header)
    if (payload):
        print_packet_payload(payload)
    
    crc_good,calc_crc,packet_crc= crc_check(header+payload)
    print_packet_crc(calc_crc,packet_crc)
    print('')
    
    if (crc_good is False):
        log_crc_error(header+payload, calc_crc,packet_crc)

knownheaders = [
    #       8-byte packet start (always expected unique)      Text       Length, Resp, Address 
    #                                                                               1 = Display, 2 = Unit, 3 = Unknown    
    [bytes([0x01, 0x03, 0x0b, 0xb9, 0x00, 0x1e, 0x16, 0x03]), "MA_1",         8, 11,   1], # Master 1 
    [bytes([0x01, 0x03, 0x3c, 0x57, 0x46, 0x32, 0x30, 0x30]), "SL_1",        65, -1,   1], # Slave  1: 65 byte response 
    [bytes([0x01, 0x03, 0x3c, 0x00, 0x00, 0x00, 0x00, 0x00]), "SL_1B",       65, -1,   1], # Slave  1B: Alternate 65-byte response
    [bytes([0x02, 0x03, 0x0b, 0xb9, 0x00, 0x1e, 0x16, 0x30]), "MA_2",         8,  4,   2], # Master 2 
    [bytes([0x00, 0x10, 0x07, 0xd1, 0x00, 0x5a, 0xb4, 0x57]), "SL_2",       189, -1,   2], # Slave  2: 189 byte response
    [bytes([0X01, 0x10, 0x03, 0xe9, 0x00, 0x5a, 0xb4, 0x57]), "MA_3",       189,  6,   1], # Master 3
    [bytes([0x01, 0x10, 0x03, 0xe9, 0x00, 0x5a, 0x91, 0x82]), "SL_3",         8, -1,   1], # Slave  3: 8-byte acq response
    [bytes([0x01, 0x10, 0x04, 0x43, 0x00, 0x5a, 0xb4, 0x57]), "MA_4",       189,  8,   1], # Master 4
    [bytes([0x01, 0x10, 0x04, 0x43, 0x00, 0x5a, 0xb0, 0xd6]), "SL_4",         8, -1,   1], # Slave  4: 8-byte acq response
    [bytes([0x01, 0x10, 0x0b, 0xb9, 0x00, 0x0b, 0x16, 0x57]), "MA_5",        31, 10,   1], # Master 5
    [bytes([0x01, 0x10, 0x0b, 0xb9, 0x00, 0x0b, 0x52, 0x0f]), "SL_5",         8, -1,   1], # Slave  5: 8-byte acq response
    [bytes([0x01, 0x03, 0x03, 0xe9, 0x00, 0x5a, 0x14, 0x41]), "MA_6",         8, 12,   1], # Master 6
    [bytes([0x01, 0x03, 0xb4, 0x57, 0x46, 0x32, 0x30, 0x30]), "SL_6",       185, -1,   1], # Slave  6: 185 byte response
    [bytes([0x02, 0x10, 0x03, 0xe9, 0x00, 0x5a, 0xb4, 0x57]), "MA_7",       189, 18,   3], # Master 7 with no observed slave response
    [bytes([0x00, 0x10, 0x03, 0xe9, 0x00, 0x5a, 0xb4, 0x57]), "MA_8",       189,  4,   2], # Master 8 with observed slave 2 response
    [bytes([0x01, 0x03, 0x04, 0x43, 0x00, 0x5a, 0x35, 0x15]), "MA_9",         8, 12,   1], # Master 9 with observed slave 6 response
    [bytes([0x02, 0x10, 0x04, 0x43, 0x00, 0x5a, 0xb4, 0x57]), "MA_10",      189, 18,   3], # Master 10 with no observed slave response
    [bytes([0x00, 0x10, 0x04, 0x43, 0x00, 0x5a, 0xb4, 0x57]), "MA_11",      189,  4,   2], # Master 11 with observed slave 2 response
    [bytes([0x01, 0x03, 0x0b, 0xb9, 0x00, 0x1e, 0x16, 0x03]), "SL_NO_REPLY",  8, -1,   3] # Slave not responding, only there to catch new master tx
]

# Global packet counters & time trackers
gl_slavepacketswomaster_count = 0
gl_unknownheaders_count = 0 
gl_masterwhenslaveexpected_count = 0 
gl_wrongslavereceived_count = 0
gl_packet_counter=0
gl_byte_counter=0
gl_delta_byte_counter=0
gl_delta_time=datetime.now()
gl_start_time=datetime.now()

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