import serial
from python_serial import knownheaders, print_line_header, print_line, read_bytes, loop_over_headers, log_slavewomaster, log_unknownpacket, log_wrongslave, log_masterwhenslaveexpected, log_masterpacket, log_slavepacket

from datetime import datetime



# for i in range(len(knownheaders)):
#    print('- ', sep='', end='')
#    print(knownheaders[i][1],' : ', sep='', end='')
#    print('size: ', knownheaders[i][2], ', header : ', sep='', end='')
#    print_byte_packet_forced(knownheaders[i][0])
#    print('')

print_line_header()
print_line("START PROGRAM WITH "+str(len(knownheaders))+" HEADERS KNOWN")

# Global state variables for processing
END_OF_FILE=False   # State variable to indicate end of file reached
SYNC=False          # State variable to indicate processing found a known masterpacket header 
file_path = "./dumpserial.bin"
serial_file_handle = None

try:
    serial_file_handle = serial.Serial('/dev/ttyUSB0',9600, timeout=None)  # open serial port, 9600, 8N1, blocking with no timeout
    # serial_file_handle = open(file_path, "rb") 

except IOError:
    print_line("Couldnt open serial file handle")

else:
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
        END_OF_FILE, newbuf=read_bytes(serial_file_handle,8)
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
                    log_slavewomaster(newbuf,masterpacket_index)
                else:
                    # Known master packet header found 
                    SYNC=True
            
            # If we havent found a known master packet header yet, read the next byte and loop again
            if SYNC==False:
                # Read the next byte 
                END_OF_FILE, nextbyte=read_bytes(serial_file_handle,1)
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
                END_OF_FILE, newbuf=read_bytes(serial_file_handle,8)
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
                        log_slavewomaster(newbuf, masterpacket_index)
                        SYNC=False
                else: 
                    # We have found an unknown header
                    log_unknownpacket(newbuf)
                    SYNC = False

            # Break out of SYNC while loop if anything was unexpected, back to SEEKING
            if SYNC==False:
                break
            

            # There may still be remaining payload in the master packet
            masterpacket_size=knownheaders[masterpacket_index][2]
            if masterpacket_size > 8:
                # Read remaining payload
                END_OF_FILE, masterpacket_payload=read_bytes(serial_file_handle,masterpacket_size-8)
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
            END_OF_FILE, newbuf=read_bytes(serial_file_handle,8)
            if END_OF_FILE:
                SYNC=False
                break            

            # Process these 8 bytes
            packet_index = -1
            sl_packet_index = -1
            
            found=False
            found,packet_index,sl_packet_index=loop_over_headers(newbuf)
            if (found==True):
                # We have found a known header, check if it is a master or a slave
                if sl_packet_index != -1:
                    # We found a known masterpacket header, while we expected a slave !
                    log_masterwhenslaveexpected(newbuf, slavepacket_index)
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
                        log_wrongslave(newbuf, packet_index)
                    
                    # There may still be remaining payload in the slave packet
                    slavepacket_size=knownheaders[slavepacket_index][2]
                    if slavepacket_size > 8:
                        # Read remaining payload
                        END_OF_FILE, slavepacket_payload=read_bytes(serial_file_handle,slavepacket_size-8)
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
                log_unknownpacket(newbuf)
                SYNC = False
finally:
    if serial_file_handle: serial_file_handle.close

# End of Program
print_line("END PROGRAM")




