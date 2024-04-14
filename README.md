This repo has python code for reverse engineering the RS-485 protocol on a Hayward 81504 full inverter heatpump (water).
This heatpump has a display and documented wifi plug, but there is no way to buy that wifi controller.
The heatpump is full inverter, but has only 2 operational steps, slow/eco and full power.
It also "forgets" the eco mode so in the middle of the night it goes full power (and noisy).

The traffic on the internal RS-485 is 9600,8N1 and not following modbus or other hayward/aqualogic protocols.
The python code produces CSV files that can be configured to have header & payload in the csv.
