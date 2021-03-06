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

import visa
import time
import csv
import os
import datetime


def gitt(mode):
    """Galvanostatic Intermittent Titration Technique.

    :param mode:     Specifies mode of operation; must be either charge or
                     discharge.
    :return voltage: Most recent voltage level."""
    if mode == 'discharge':
        time_start = time.time()
        period_start = time.time()
        psink.write('curr %f; input 1' % setcurrent)
        voltage = dmm1.ask_for_values('meas:volt?')[0]
        while voltage > voltage_lower_limit:
            measure_and_write_data(time_start)
            elapsed = time.time() - period_start
            voltage = dmm1.ask_for_values('meas:volt?')[0]
            if elapsed >= period:
                toggle = psink.ask_for_values('input?')[0]
                if toggle == 0:
                    psink.write('input 1')
                else:
                    psink.write('input 0')
                period_start = time.time()
            time.sleep(1)
            if voltage < voltage_lower_failsafe:
                raise Exception('Cell voltage too low!')
        psink.write('curr 0; input 0')
        return voltage
    elif mode == 'charge':
        time_start = time.time()
        period_start = time.time()
        psupply.write('curr %f; output 1' % setcurrent)
        voltage = dmm1.ask_for_values('meas:volt?')[0]
        while voltage < voltage_upper_limit:
            measure_and_write_data(time_start)
            voltage = dmm1.ask_for_values('meas:volt?')[0]
            elapsed = time.time() - period_start
            if elapsed >= period:
                toggle = psupply.ask_for_values('output?')[0]
                if toggle == 0:
                    psupply.write('output 1')
                else:
                    psupply.write('output 0')
                period_start = time.time()
            time.sleep(1)
            if voltage > voltage_upper_failsafe:
                raise Exception('Cell voltage too high!')
        psupply.write('curr 0; output 0')
        return voltage
    else:
        raise Exception('Unknown mode of operation: %s' % mode)


def measure_and_write_data(time_start):
    voltage = dmm1.ask_for_values('meas:volt?')[0]
    current = dmm2.ask_for_values('meas:volt?')[0] / 0.0005
    elapsed = time.time() - time_start
    with open(data_file, 'a') as csvfile:
        datawriter = csv.writer(csvfile, delimiter=' ', quotechar='|',
                                        quoting=csv.QUOTE_MINIMAL)
        datawriter.writerow([voltage] + [current] + [elapsed])


def reset_instruments():
    """Issue SCPI commands *RST; STATus:PRESet; *CLS to a list of instruments.

    *RST configures the instrument to a known state optimized for remote
    operation.
    STATus:PRESet sets all registers and queues to device specific preset
    values, except those controlled by *CLS.
    *CLS clears all event status registers and queues."""
    for i in instruments:
        i.write('*rst; stat:pres; *cls')


# Assign names to instruments.
# After creating a visa.ResourceManager() object, use rm.list_resources() to get
# a list of all connected resources. If you are uncertain of which resource
# corresponds to which instrument, assign a temporary name to a resource with
# temp_resource = rm.get_instrument(<resource>) and issue
# temp_resource.ask('*IDN?') to get some useful information about it.
#
# DO NOT USE THE FOLLOWING CODE AS IS! You must find the correct GPIB addresses
# for *your* system, even if you are using the same instruments.
rm = visa.ResourceManager()
psupply = rm.get_instrument('GPIB0::4::INSTR')  # Amrel SPS8-150-K1E0
psink = rm.get_instrument('GPIB0::5::INSTR')    # Amrel PLA800-60-300
dmm2 = rm.get_instrument('GPIB0::16::INSTR')    # Keithley Digital Multimeter 2700
dmm1 = rm.get_instrument('GPIB0::21::INSTR')    # Keithley Digital Multimeter 2000
instruments = [dmm1, dmm2, psink, psupply]

# User set variables.
cycles = 3
data_file = '/home/TEK/Documents/Alexander/data/gitt.csv'
period = 600
setcurrent = 8.5
voltage_lower_limit = 2.5
voltage_lower_failsafe = voltage_lower_limit - 0.1
voltage_upper_limit = 4.1
voltage_upper_failsafe = voltage_upper_limit + 0.1
voltage_nominal = (voltage_lower_limit + voltage_upper_limit) / 2

if os.path.isfile(data_file):
    date = str(datetime.datetime.today())
    os.rename(data_file, data_file + date)

reset_instruments()
psupply.write('volt 5') # Default is 2 Volts, which is too low.
    
voltage = dmm1.ask_for_values('meas:volt?')[0]
for i in range(cycles):
    if voltage <= voltage_nominal and voltage > voltage_lower_failsafe:
        try:
            voltage = gitt('charge')
        except Exception as e:
            print(e)
            reset_instruments()
    elif voltage > voltage_nominal and voltage < voltage_upper_failsafe:
        try:
            voltage = gitt('discharge')
        except Exception as e:
            print(e)
            reset_instruments()
    else:
        reset_instruments()
        raise Exception('Cell voltage outside acceptable limits!')
    
reset_instruments()
