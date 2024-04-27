from python_serial import print_packet, print_packet_mask
import csv

def packet_compare(packet1:bytes,packet2:bytes,mask):
    for i in range(len(packet1)):
        byte1=packet1[i]
        byte2=packet2[i]
        if byte1!=byte2:
            if (i in mask)==False:
                mask.append(i)

    return mask

packet_mask_SL1 = [15, 16, 26, 28]
packet_mask_SL2 = [20, 36, 37, 38, 43, 44, 46, 50, 88, 90, 92, 94, 96, 98, 100, 119, 120, 124, 131, 132, 135, 136, 170]
packet_mask_MA_4 = [90]

# This is the list of packet ID's to test
packets_to_test=[
                # Packets to test and track  Mask list   previous packet
                ['MA_1',                     [],         b''],
                ['SL_1',                     [],         b''],
  #              ['MA_2',                     [],         b''],
  #              ['SL_2',                     [],         b''],
                ['MA_3',                     [],         b''],
                ['SL_3',                     [],         b''],
                ['MA_4',                     [],         b''],
                ['SL_4',                     [],         b''],
                ['MA_5',                     [],         b''],
                ['SL_5',                     [],         b''],
                ['MA_6',                     [],         b''],
                ['SL_6',                     [],         b''],
 #               ['MA_7',                     [],         b''],
 #               ['MA_8',                     [],         b''],
                ['MA_9',                     [],         b'']
 #               ['MA_10',                    [],         b''],
 #               ['MA_11',                    [],         b'']
                ]
TEST_ID = 0
MASK_ID = 1
PREV_ID = 2

# This will contain all filtered packets
packet_test_data=[]
# TEST_ID = 0 = same position as for previous list
TIMESTAMP_ID = 1
PAYLOAD_ID = 2

# Read complete CSV data into memory
file = open("seq1_01.csv", "r")
data = list(csv.reader(file, delimiter=","))
file.close

# first go through all packets and filter out all packets under test
for i in range(len(data)):
    packet=data[i][6].lstrip(' ')
    for j in range(len(packets_to_test)):
        if packet == packets_to_test[j][TEST_ID]:
            packet_payload_full = bytes.fromhex(data[i][8].lstrip(' '))
            packet_payload=packet_payload_full[0:len(packet_payload_full)-2]
            packet_timestamp=data[i][1].lstrip(' ')
            packet_test_data.append([packets_to_test[j][TEST_ID],packet_timestamp, packet_payload])
            # We need to set the previous packet to the first packet of this TEST_ID
            if packets_to_test[j][PREV_ID]==b'':
                packets_to_test[j][PREV_ID]=packet_payload

# Next find for each test packet the changed bytes and add positions in "mask"
for i in range(1,len(packet_test_data)):
    for j in range(len(packets_to_test)):
        # check for each packet under test 
        test_data=packet_test_data[i][TEST_ID]
        to_test_data=packets_to_test[j][TEST_ID]
        if packet_test_data[i][TEST_ID]==packets_to_test[j][TEST_ID]:
            packets_to_test[j][MASK_ID]=packet_compare(packets_to_test[j][PREV_ID], packet_test_data[i][PAYLOAD_ID],packets_to_test[j][MASK_ID])
            packets_to_test[j][PREV_ID]=packet_test_data[i][PAYLOAD_ID]
           # packet_mask[j] = packet_compare(packet_test_data[i-1][1], packet_test_data[i][1], packet_mask[j])

# Sort each mask in increasing position & reset previous packet field
for j in range(len(packets_to_test)):
    packets_to_test[j][MASK_ID].sort()
    packets_to_test[j][PREV_ID]=b''
    # Print each mask 
    print(packets_to_test[j][TEST_ID], ' : ' , packets_to_test[j][MASK_ID])

# Defines if we want to print all -or- only the masked
print_with_mask = True

# Print all packets  
for i in range(len(packet_test_data)):
    # for each packet to print, find the corresponding mask
    for j in range(len(packets_to_test)):
        if packet_test_data[i][TEST_ID]==packets_to_test[j][TEST_ID]:
            packet_mask=packets_to_test[j][MASK_ID]
            break
    print(packet_test_data[i][TEST_ID],' : ',end='',sep='')
    print(packet_test_data[i][TIMESTAMP_ID],' : ',end='',sep='')
    
    if print_with_mask==True:
        print_packet_mask(packet_test_data[i][PAYLOAD_ID],packets_to_test[j][PREV_ID],packet_mask)
    else:
        print_packet(packet_test_data[i][PAYLOAD_ID])
    print('')
    
    # Set Previous packet for this packet type
    packets_to_test[j][PREV_ID]=packet_test_data[i][PAYLOAD_ID]
