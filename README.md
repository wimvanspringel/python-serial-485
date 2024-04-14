# Project Description
This repo has python code for reverse engineering the RS-485 protocol on a Hayward 81504 full inverter heatpump (water).
This heatpump has a display and documented wifi plug, but there is no way to buy that wifi controller.
The heatpump is full inverter, but has only 2 operational steps, slow/eco and full power.
It also "forgets" the eco mode so in the middle of the night it goes full power (and noisy).
The original intent was to connect the heatpump up to an arduino and mimick the external display and hook the arduino up to mqtt for display/control of main parameters: On/off/eco, set temp, read ingoing/outgoing temperature of water.
For that to work, we need to reverse engineer the rs-485 bus.
# RS-485 bus
The traffic on the internal RS-485 is 9600,8N1 and not following modbus or other hayward/aqualogic protocols.
The python code produces CSV files that can be configured to have header & payload in the csv.
# Assumptions
- Bus: RS485, half duplex, 9600, 8N1
- Packet: no known size or address, have 2 bytes of modbus crc-16 in little endian at the end
- Master starts tx with packet, slave responds with packet
- Timeout – 100-150 ms
- If slave response within timeout, new master tx
# Observations
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
