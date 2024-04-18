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
## Test sequence 01
The result of this test sequence can be found in seq1-01.csv in the repo
- 00:00 - START python logging
- 00:10 - HP POWER supply switched on
- 00:40 - Heater ON by pushing power button for 1 sec
- 01:10 - Increase set temperature by 0.3 deg C - 4 pushes up
- 01:30 - Heater OFF by pushing power buttor for 1 sec
- 01:50 - HP POWER supply switched off
- 02:10 - STOP python logging

## Message Table
``So far, I identified 11 unique master headers (8-byte), and 7 unique slave headers 
- MA_1 : size: 8, header : 01030bb9001e1603, 
- SL_1 : size: 65, header : 01033c5746323030, 
- SL_1_B : size: 65, header : 01033c0000000000, 
- MA_2 : size: 8, header : 02030bb9001e1630, 
- SL_2 : size: 189, header : 001007d1005ab457, 
- MA_3 : size: 189, header : 011003e9005ab457, 
- SL_3 : size: 8, header : 011003e9005a9182, 
- MA_4 : size: 189, header : 01100443005ab457, 
- SL_4 : size: 8, header : 01100443005ab0d6, 
- MA_5 : size: 31, header : 01100bb9000b1657, 
- SL_5 : size: 8, header : 01100bb9000b520f, 
- MA_6 : size: 8, header : 010303e9005a1441, 
- SL_6 : size: 185, header : 0103b45746323030, 
- MA_7 : size: 189, header : 021003e9005ab457, 
- MA_8 : size: 189, header : 001003e9005ab457, 
- MA_9 : size: 8, header : 01030443005a3515, 
- MA_10 : size: 189, header : 02100443005ab457, 
- MA_11 : size: 189, header : 00100443005ab457, 
