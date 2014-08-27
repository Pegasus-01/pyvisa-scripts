#!/usr/bin/python

import visa
from time import sleep

rm = visa.ResourceManager()

amrel_sps = rm.get_instrument('GPIB0::4::INSTR')
amrel_pla = rm.get_instrument('GPIB0::5::INSTR')
keithley2700 = rm.get_instrument('GPIB0::16::INSTR')
keithley2000 = rm.get_instrument('GPIB0::21::INSTR')

instruments = [amrel_sps, amrel_pla, keithley2700, keithley2000]

for i in instruments:
    i.write('*rst; status:preset; *cls')

voltage = keithley2000.ask_for_values('meas:volt?')[0]

if voltage > 3.2:
    amrel_pla.write('curr 2; input 1')
    voltages = []
    currents = []
    while voltage > 3.2:
        voltage = keithley2000.ask_for_values('meas:volt?')[0]
        current = keithley2700.ask_for_values('meas:volt?')[0] / 0.1
        voltages.append(voltage)
        currents.append(current)
        sleep(1)
    amrel_pla.write('curr 0; input 0')
else:
    print('Cell below voltage threshold!')

for i in instruments:
    i.write('trace:clear; feed:control next')
