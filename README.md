# Project Description
This repo has python code for reverse engineering the RS-485 protocol on a Hayward 81504 full inverter heatpump aka HP (water).
This HP has a display and documented wifi connector-plug, but there is no way to buy that wifi controller.
The HP is so-called a full inverter, but in reality has only 2 operational steps, slow/eco and full power.
The unit can be set to eco-mode, but it "forgets" that eco mode so in the middle of the night it goes full power (and noisy). From observations this happens when upon hitting the "set-temperature".
The original intent was to connect the HP up to an arduino and mimick and replace the external display and hook the arduino up to mqtt for display/control of main parameters: On/off/eco, set temp, read ingoing/outgoing temperature of water.
For that to work, we need to reverse engineer the rs-485 bus.
# Reverse engineering the RS-485 bus
The traffic on the internal RS-485 is 9600,8N1 and not following modbus or other hayward/aqualogic protocols.
The python code produces CSV files that can be configured to have header & payload in the csv.
## Hardware setup
The python code runs on a linux/windows machine with a USB RS-485 transceiver. That transceiver is hooked up in series with the HP's internal RS485 bus using JST-SM connectors as used in the HP. 
## Assumptions
- Bus: RS485, half duplex, 9600, 8N1
- Packet: no size or address field found inside the packets
- All Packets have a unique 8-byte header
- All Packets have 2 bytes of modbus crc-16 in little endian at the end of the packet
- Packet sizes 8, 31, 65 185, 189 are the observed sizes 
- Master starts tx with packet, slave responds with packet
- Timeout – 100-150 ms (unverified)
- If slave response within timeout, new master tx
## Observations
- After heater start, ventilator starts after approx 11 sec
- After heater start, without waterflow, E03 after approx 60 sec
- M7 does not get response = gets retried 3 times, followed by a M8/S2 
- M10 does not get response = gets retried 3 times, followed by a M11/S2 sequence
- Heater on results after approx 8 secs in M3 when S2 is expected, followed by S3 and 3 unanswered M7’s
- Set temp change results after approx 12 secs in M4 when S2 is expected, followed by S4 and 3 unanswered M10’s
- Heater on/off instant results in M6/S6 and M5/S5
- M1 only gets answered 5 secs after power up
- M1 stops responding 2 secs after power down
- Unit stays bus active 17 secs after powered down
## Message Table
So far, I identified 11 unique master headers, and 7 unique slave response headers, the actual 8-byte headers are in phyton_serial.py 
| Master ID | Slave ID  | To | Return | Device | MA| SL | 
| --- | --- | --- | --- | --- | --- | --- | 
| MA1  | SL1 (SL1B) | 8   | 65  | Display | 01030bb9001e1603 | 01033c5746323030 | 
| MA2  | SL2        | 8   | 189 | EEV     | 02030bb9001e1630 | 001007d1005ab457 |
| MA3  | SL3        | 189 | 8   | Display | 011003e9005ab457 | 011003e9005a9182 |
| MA4  | SL4        | 189 | 8   | Display | 01100443005ab457 | 01100443005ab0d6 | 
| MA5  | SL5        | 31  | 8   | Display | 01100bb9000b1657 | 01100bb9000b520f |
| MA6  | SL6        | 8   | 185 | Display | 010303e9005a1441 | 0103b45746323030 | 
| MA7  |            | 189 |     | Unknown | 021003e9005ab457 | |
| MA8  | SL2        | 189 | 189 | EEV     | 001003e9005ab457 | 001007d1005ab457 | 
| MA9  | SL6        | 8   | 185 | Display | 01030443005a3515 | 0103b45746323030 |
| MA10 |            | 189 |     | Unknown | 02100443005ab457 | |
| MA11 | SL2        | 189 | 189 | EEV     | 00100443005ab457 | 001007d1005ab457 | 
## Test sequence 01
The result of this test sequence can be found in seq1-01.csv in the repo
- 00:00 - START python logging
- 00:10 - HP POWER supply switched on
- 00:40 - Heater ON by pushing power button for 1 sec
- 01:10 - Increase set temperature by 0.3 deg C - 4 pushes up
- 01:30 - Heater OFF by pushing power buttor for 1 sec
- 01:50 - HP POWER supply switched off
- 02:10 - STOP python logging
## Test sequence 02
The result of this test sequence can be found in seq2-01.csv in the repo  
Write down current temp on the display during the whole sequence, heat a bit to make it change  
- 00:00 - START python logging
- 00:10 - HP POWER supply switched on
- 00:40 - Heater ON by pushing power button for 1 sec
- 01:35 - Heater OFF by pushing power buttor for 1 sec
- 01:50 - HP POWER supply switched off
- 02:10 - STOP python logging
## Packet Analysis
### SL1
Byte 15 : 0x80 once upon startup  
Byte 16 : 0x01 once upon heater on and upon heater off/ 0x40 once upon temp change  
Byte 24 : Hour field  
Byte 26 : Minutes field  
Byte 28 : Seconds field  
### MA3
Byte 20 :  
Byte 24 :  
Byte 26 :
### MA4 
Byte : 90  
## Sequence Analysis
### HP POWER supply switched on
MA1/MA2/SL2 (No SL1 response)  
*Approx 5 seconds later*  
MA1/SL1 Byte 18 0x80   
MA3/SL3  
MA4/SL4  
MA5/SL5  
MA1/SL1/MA2/SL2 loops 
### HP POWER supply switched off
MA1/MA2/SL2 (No SL1 response) until psu dies after approx. 17 secs
### Heater ON
MA1/SL1 Byte 16 0X01  
MA6/SL6  
MA5/SL5   
MA1/SL1/MA2/SL2 loops  

*Approx 5 seconds later*  
MA3/SL3  
MA7/MA7/MA7  
MA8/SL2  
MA1/SL1/MA2/SL2 loops  

*Approx 25 seconds later*  
MA4/SL4  
MA10/MA10/MA10  
MA11/SL2  
MA1/SL1/MA2/SL2 loops  
### Heater OFF
MA1/SL1 Byte 16 0X01  
MA6/SL6  
MA5/SL5   
MA1/SL1/MA2/SL2 loops  

*Approx 5 seconds later*  
MA3/SL3  
MA7/MA7/MA7  
MA8/SL2  
MA1/SL1/MA2/SL2 loops  

### Set temperature change
*Approx 5 seconds later*  
MA1/SL1 Byte 16 0X40 once  
MA9/SL6   
MA5/SL5  
MA1/SL1/MA2/SL2 loops 
