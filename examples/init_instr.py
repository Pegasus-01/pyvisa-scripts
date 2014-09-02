#!/usr/bin/python

import visa

rm = visa.ResourceManager()
psupply = rm.get_instrument('GPIB0::4::INSTR')  # Amrel SPS8-150-K1E0
psink = rm.get_instrument('GPIB0::5::INSTR')    # Amrel PLA800-60-300
dmm2 = rm.get_instrument('GPIB0::16::INSTR')    # Keithley Digital Multimeter 2700
dmm1 = rm.get_instrument('GPIB0::21::INSTR')    # Keithley Digital Multimeter 2000
instruments = [dmm1, dmm2, psink, psupply]
