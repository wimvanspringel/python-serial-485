# Hardware of the Hayward 81504 heatpump

## Introduction

![81504](https://github.com/wimvanspringel/python-serial-485/assets/23611681/05178b72-2590-4eca-a454-902c13c0df03)
The 81504 pump is full inverter, swimming pool heat exchange pump.
This version is the smallest 6.7 kW version of this model, but it has 5 versions with a highest power of 17,8 kW version.

The main components are:

- Display controller (rs-485 bus connected)
- Compressor 
- Main controller PCB 
- Titanium Electronic Echange valve (**EEV**=water heater element)
- DC ventilator motor
- 4-way compressor valve

Display controller, EEV and Main PCB are connected by a single rs-485 bus. Schematics seem to hint at an optional Wifi module. Internet research seems to lead to a Hayward Eyepool smart inverter wifi module [hwx26100016](https://www.zwemland.nl/hayward-warmtepomp-wifi-module-type-hwx26100016.html)

## Schematics

![schematics](https://github.com/wimvanspringel/python-serial-485/assets/23611681/ee066f25-2c3c-4c1b-a55b-10b58faa966c)

## Internal build-up pictures

![13](https://github.com/wimvanspringel/python-serial-485/assets/23611681/e85f6d15-e4e0-4e67-bfe6-b1cf704ccae4)
![18](https://github.com/wimvanspringel/python-serial-485/assets/23611681/fb2a0e1a-558f-4d2a-bd87-a57a5cb727ea)
![17](https://github.com/wimvanspringel/python-serial-485/assets/23611681/eb69b6d7-f4ac-4741-ab09-3fdf1e7d0ac2)
![01](https://github.com/wimvanspringel/python-serial-485/assets/23611681/1022d63b-b816-4f26-8168-cfd636e00a57)
![19](https://github.com/wimvanspringel/python-serial-485/assets/23611681/f9787d59-f59e-47a8-87f8-83935f956508)
![16](https://github.com/wimvanspringel/python-serial-485/assets/23611681/88c39ade-47b5-473c-9d2d-bdb233829cf3)

## Display PCB Pictures

[MCU = STM8S207](manuals/stm8s207mb.pdf)  
[Low-side switch darlington array = TI ULN2003AI (multiple)](manuals/uln2003ai.pdf)  
[EEPROM = FMD FT24C08A 8192 bits serial eeprom](manuals/FT24C08A_datasheet.pdf)  
[RS485 transceiver = TI SN65LBC184](manuals/SN65LBC184.PDF)  
![21](https://github.com/wimvanspringel/python-serial-485/assets/23611681/5b37a5f3-ac33-4790-a703-dc31faa43953)
![20](https://github.com/wimvanspringel/python-serial-485/assets/23611681/bc46ded7-b22c-4169-9f77-cd463313d3ed)
![31](https://github.com/wimvanspringel/python-serial-485/assets/23611681/6d9e31e7-6c1e-4aa5-a088-5e56b1281857)
![30](https://github.com/wimvanspringel/python-serial-485/assets/23611681/590681e1-e069-408c-a6c2-b56366777a19)
![29](https://github.com/wimvanspringel/python-serial-485/assets/23611681/e384f0c0-8e75-40ca-86a7-5dd843edaa92)
![28](https://github.com/wimvanspringel/python-serial-485/assets/23611681/59d28623-e680-4bb9-b1ec-81828c1b9375)
![27](https://github.com/wimvanspringel/python-serial-485/assets/23611681/f6503874-347c-4bfb-8210-b4921357df60)

## Main PCB pictures
[MCU = renesas 44-pin R5F100FFA](manuals/rl78g13-datasheet.pdf)  
[RS485 transceiver = TI SN65LBC184](manuals/SN65LBC184.PDF)  
[Low-side switch darlington array = TI ULN2003AI (multiple)](manuals/uln2003ai.pdf)  
![15](https://github.com/wimvanspringel/python-serial-485/assets/23611681/cdf2adc0-ffa3-4bd4-8d1d-852e19a1e700)
![14](https://github.com/wimvanspringel/python-serial-485/assets/23611681/fdbddc15-79c0-4837-8924-fc455851b8c8)
![12](https://github.com/wimvanspringel/python-serial-485/assets/23611681/bc3b4786-497d-46ff-b5b4-a06b01f76c4f)
![11](https://github.com/wimvanspringel/python-serial-485/assets/23611681/b8e45403-7498-4b8e-bbcd-9b5073bb6940)
![10](https://github.com/wimvanspringel/python-serial-485/assets/23611681/f2a6c0ac-b30d-4125-8001-b487faea4cd2)
![09](https://github.com/wimvanspringel/python-serial-485/assets/23611681/acc14361-19ca-46a7-96fc-7907c2a006c6)
![08](https://github.com/wimvanspringel/python-serial-485/assets/23611681/a99f36be-cecd-4630-83f3-4bc764ef3c1f)
![07](https://github.com/wimvanspringel/python-serial-485/assets/23611681/c072b3c5-cef5-4049-9609-b4ccf5cb51fe)
![06](https://github.com/wimvanspringel/python-serial-485/assets/23611681/f79fdc50-12a6-4d61-832c-0e13966d509d)
![05](https://github.com/wimvanspringel/python-serial-485/assets/23611681/bdcfe392-9dba-4919-882b-2422d63ee38c)
![04](https://github.com/wimvanspringel/python-serial-485/assets/23611681/f70821b1-57b1-454a-949a-e8e739c307c2)
![03](https://github.com/wimvanspringel/python-serial-485/assets/23611681/6c56034a-616d-4869-a98a-d65187737033)
![02](https://github.com/wimvanspringel/python-serial-485/assets/23611681/4953231c-1a0a-49d8-99ff-d754fe642feb)
![26](https://github.com/wimvanspringel/python-serial-485/assets/23611681/f7efec53-1c79-4321-96cb-a96d51c9faa4)
![25](https://github.com/wimvanspringel/python-serial-485/assets/23611681/10e5af28-b38a-45fd-b842-1d7f17515990)
![24](https://github.com/wimvanspringel/python-serial-485/assets/23611681/ff05418c-0db4-4bb8-85b2-cdf68387c239)
![23](https://github.com/wimvanspringel/python-serial-485/assets/23611681/a720cfb7-fb66-4c15-8d6c-c79fa98dc42d)
![22](https://github.com/wimvanspringel/python-serial-485/assets/23611681/08781c84-c12a-47d8-a493-dbe7a3c137c5)
![33](https://github.com/wimvanspringel/python-serial-485/assets/23611681/47a8c405-2fb8-4535-b8bc-c865e30ef0f9)
