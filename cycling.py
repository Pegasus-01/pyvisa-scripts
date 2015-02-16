#!/usr/bin/python

## The MIT/Expat License (MIT)

## Copyright (c) 2014-2015 Alexander Bessman

## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.

import time
import csv
import visa
import datetime

def cc(target_voltage, set_current):
    if set_current >= 0:
        instr = sps
        instr.write('VOLTage %f; CURRent %f; OUTPut 1' % (target_voltage, set_current))
    else:
        instr = pla
        instr.write('CURRent %f; OUTPut 1' % (-set_current))
    while True:
        time.sleep(1)
        voltage = vmult.query_ascii_values('MEASure:VOLTage?')[0]
        current = cmult.query_ascii_values('MEASure:VOLTage?')[0] / 0.0005
        elapsed = time.time() - start_time
        with open(output_file, 'a') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=' ', quotechar='|',
                                    quoting=csv.QUOTE_MINIMAL)
            datawriter.writerow([voltage] + [current] + [elapsed])
        print('Voltage: %f V, Current: %f A' % (voltage, current))
        if (set_current > 0 and voltage >= target_voltage or
                set_current <= 0 and voltage <= target_voltage):
            instr.write('OUTPut 0')
            return

def cv(set_voltage, target_current):
    if target_current >= 0:
        instr = sps
    else:
        # Not fully implemented yet, do not use!
        #instr = pla
        raise ValueError('{target_current} must be positive.')
    while True:
        instr.write('VOLTage %f; OUTPut 1' % (set_voltage))
        time.sleep(1)
        voltage = vmult.query_ascii_values('MEASure:VOLTage?')[0]
        current = cmult.query_ascii_values('MEASure:VOLTage?')[0] / 0.0005
        elapsed = time.time() - start_time
        with open(output_file, 'a') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=' ', quotechar='|',
                                    quoting=csv.QUOTE_MINIMAL)
            datawriter.writerow([voltage] + [current] + [elapsed])
        print('Measured: %f V, Config: %f V, Current: %f A' %
              (voltage, current))
        if current < target_current:
            instr.write('OUTPut 0')
            return


rm = visa.ResourceManager()
sps = rm.open_resource('GPIB0::4::INSTR')
pla = rm.open_resource('GPIB0::5::INSTR')
vmult = rm.open_resource('GPIB0::16::INSTR')
cmult =  rm.open_resource('GPIB0::21::INSTR')

# -------------------------------
# USER EDITABLE VALUES BEGIN HERE
# -------------------------------
output_file = '/home/abessman/data/scania_cell521_cycle_' + str(datetime.date.today()) + '.csv'
lowv, highv = 3.0, 4.1
current = 25.0
cycles = 50
# -------------------------------
# USER EDITABLE VALUES END HERE
# -------------------------------

try:
    start_time = time.time()
    for i in range(cycles):
        sps_voltage = cc(highv, current)
        cv(highv, current/10, sps_voltage)
        cc(lowv, -current)
except:
    sps.write('OUTPut 0')
    pla.write('OUTPut 0')
    raise
