import python_serial    
import csv

def packet_compare(packet1:bytes,packet2:bytes,mask):
    for i in range(len(packet1)):
        byte1=packet1[i]
        byte2=packet2[i]
        if byte1!=byte2:
            if (i in mask)==False:
                mask.append(i)

    return mask

file = open("seq1_01.csv", "r")
data = list(csv.reader(file, delimiter=","))
file.close

packet_mask_SL1 = [15, 16, 26, 28]
packet_mask_SL2 = [20, 36, 37, 38, 43, 44, 46, 50, 88, 90, 92, 94, 96, 98, 100, 119, 120, 124, 131, 132, 135, 136, 170]
packet_mask_MA_4 = [90]

packet_under_test='MA_4'
packet_mask=[]
packet_test_data=[]

for i in range(len(data)):
    # first go through all packets for the packet under test
    packet=data[i][6].lstrip(' ')
    
    if packet == packet_under_test:
        packet_payload_full = bytes.fromhex(data[i][8].lstrip(' '))
        packet_payload=packet_payload_full[0:len(packet_payload_full)-2]
        print(data[i][1],' - ', packet_payload.hex(), sep='', end='')
        print('')
        packet_test_data.append(packet_payload)

for i in range(1,len(packet_test_data)):
    packet_mask = packet_compare(packet_test_data[i-1], packet_test_data[i], packet_mask)

packet_mask.sort()
print(packet_mask)