#!/usr/bin/python

import visa
import csv
import time

from instruments.keithley.k2xxx import *
from instruments.amrel.pla import *

## TODO: Reduce code duplication.
def cc_discharge(keithley1, keithley2, amrelpla, setcurrent, voltage_lower_limit,
                 output_file, measurement_interval):
    """Constant current discharge with current and voltage measured separately."""
    voltage = keithley2xxx_measure_voltage(keithley1)

    if voltage > voltage_lower_limit:
        start_time = time.time()
        amrelpla_constant_current(amrelpla, setcurrent, 1)
        while voltage > voltage_lower_limit:
            voltage = keithley2xxx_measure_voltage(keithley1)
            # Current is calculated by measuring the voltage drop over a 5e-4 Ohm shunt.
            current = keithley2xxx_measure_voltage(keithley2)/ 0.0005
            elapsed = time.time() - start_time
            with open(output_file, 'a') as csvfile:
                datawriter = csv.writer(csvfile, delimiter=' ', quotechar='|',
                                        quoting=csv.QUOTE_MINIMAL)
                datawriter.writerow([voltage] + [current] + [elapsed])
            print('Voltage: %f, Current: %f, Time: %f' % (voltage, current, elapsed))
            time.sleep(measurement_interval)
        amrelpla.write('curr 0; input 0')
    else:
        print('Cell below voltage threshold!')

def cc_charge(keithley1, keithley2, amrelsps, setcurrent, voltage_upper_limit,
              output_file, measurement_interval):
    """Constant current charge with current and voltage measured separately."""
    voltage = keithley2xxx_measure_voltage(keithley2000)

    if voltage < voltage_upper_limit:
        start_time = time.time()
        amrelsps_constant_current(amrelsps, setcurrent, 1)
        while voltage < voltage_upper_limit:
            voltage = keithley2xxx_measure_voltage(keithley1)
            # Current is calculated by measuring the voltage drop over a 5e-4 Ohm shunt.
            current = keithley2xxx_measure_voltage(keithley2)/ 0.0005
            elapsed = time.time() - start_time
            with open(output_file, 'a') as csvfile:
                datawriter = csv.writer(csvfile, delimiter=' ', quotechar='|',
                                        quoting=csv.QUOTE_MINIMAL)
                datawriter.writerow([voltage] + [current] + [elapsed])
            print('Voltage: %f, Current: %f, Time: %f' % (voltage, current, elapsed))
            time.sleep(measurement_interval)
        amrelsps.write('curr 0; output 0')
    else:
        print('Cell above voltage threshold!')

rm = visa.ResourceManager()

## User editable variables:
voltage_lower_limit = 2.5
voltage_upper_limit = 4.1
setcurrent = 8.5
output_file_charge = '~/Documents/Alexander/data/CCC_0.5C.csv'
output_file_discharge = '~/Documents/Alexander/data/CCD_0.5C.csv'
measurement_interval = 1

amrelsps = rm.get_instrument('GPIB0::4::INSTR')
amrelpla = rm.get_instrument('GPIB0::5::INSTR')
keithley2700 = rm.get_instrument('GPIB0::16::INSTR')
keithley2000 = rm.get_instrument('GPIB0::21::INSTR')

instruments = [amrelsps, amrelpla, keithley2700, keithley2000]

for i in instruments:
    i.write('*rst; status:preset; *cls')

for i in range(10):
    cc_discharge(keithley2000, keithley2700, amrelpla, setcurrent, voltage_lower_limit,
                 output_file_discharge, measurement_interval)
    cc_charge(keithley2000, keithley2700, amrelsps, setcurrent, voltage_upper_limit,
              output_file_charge, measurement_interval)

for i in instruments:
    i.write('trace:clear; feed:control next')
