#!/usr/bin/python

import visa
import time
import csv
import os


def hppc():
    """High Power Pulse Characterization."""
    for target_soc in soc_list:
        set_soc(target_soc)
        time_start = time.time()
        for cycle in range(cycles):
            pulse_start = time.time()
            psupply.write('curr %f; output 1' % pulse_current)
            while True:
                measure_and_write_data(time_start)
                pulse_time = time.time() - pulse_start
                if pulse_time > pulse_period:
                    break
            psupply.write('curr 0; output 0')
            rest_start = time.time()
            while True:
                measure_and_write_data(time_start)
                rest_time = time.time() - rest_start
                if rest_time > rest_period:
                    break
            pulse_start = time.time()
            psink.write('curr %f; input 1' % pulse_current)
            while True:
                measure_and_write_data(time_start)
                pulse_time = time.time() - pulse_start
                if pulse_time > pulse_period:
                    break
            psink.write('curr 0; input 0')
            rest_start = time.time()
            while True:
                measure_and_write_data(time_start)
                rest_time = time.time() - rest_start
                if rest_time > rest_period:
                    break


def set_soc(target_soc):
    """Assuming state of charge (SOC) is directly proportional to cell voltage,
    charge or discharge cell until desired <target_soc> is reached using first
    constant current followed by pseudo-constant voltage."""
    state_of_charge = get_soc()
    if state_of_charge < 0 or state_of_charge > 1:
        reset_instruments()
        raise Error('Cell voltage outside acceptable limits!')
    if state_of_charge < target_soc:
        # The first loop through this for statement is a regular constant
        # current charge. Subsequent loops are meant to emulate a constant
        # voltage charging scheme; I don't trust the voltmeters built into the
        # power supply/sink instruments, so instead I divide the current by two
        # when the target voltage is reached.
        for current_modifier in range(1,10):
            psupply.write('curr %f; output 1' % (pulse_current / 
                          current_modifier))
            state_of_charge = get_soc()
            while state_of_charge < target_soc:
                state_of_charge = get_soc()
                time.sleep(1)
        psupply.write('curr 0; output 0')
    elif state_of_charge > target_soc:
        # The first loop through this for statement is a regular constant
        # current discharge. Subsequent loops are meant to emulate a constant
        # voltage discharging scheme; I don't trust the voltmeters built into
        # the power supply/sink instruments, so instead I divide the current by
        # two when the target voltage is reached.
        for current_modifier in range(1,10):
            psink.write('curr %f; input 1' % (pulse_current / current_modifier))
            state_of_charge = get_soc()
            while state_of_charge > target_soc:
                state_of_charge = get_soc()
                time.sleep(1)
        psink.write('curr 0; input 0')


def measure_and_write_data(time_start):
    voltage = dmm1.ask_for_values('meas:volt?')[0]
    current = dmm2.ask_for_values('meas:volt?')[0] / 0.0005
    elapsed = time.time() - time_start
    with open(data_file, 'a') as csvfile:
        datawriter = csv.writer(csvfile, delimiter=' ', quotechar='|',
                                        quoting=csv.QUOTE_MINIMAL)
        datawriter.writerow([voltage] + [current] + [elapsed])

def get_soc():
    voltage = dmm1.ask_for_values('meas:volt?')[0]
    # TODO: This is an extremely poor way to calculate SOC.
    state_of_charge = (voltage - voltage_lower_limit) / \
                      (voltage_upper_limit - voltage_lower_limit)
    return state_of_charge


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

# User set variables:
cycles = 2
data_file = '/home/TEK/Documents/Alexander/data/hppc.csv'
pulse_current = 10.0
pulse_period = 10
rest_period = 40
soc_list = [0.80, 0.60, 0.40, 0.20]
voltage_lower_limit = 2.5
voltage_upper_limit = 4.1

if os.path.isfile(data_file):
    os.remove(data_file)

reset_instruments()
psupply.write('volt 5') # Default is 2 Volts, which is too low.

hppc()

reset_instruments()
