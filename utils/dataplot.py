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

import numpy as np
import matplotlib.pyplot as plt

# The data file should contain simple CSV text, with voltage in the first column,
# current in the second, and time in the third.
datapath = raw_input('Data location?\n>')
data = np.loadtxt(datapath)
capacity = np.cumsum(np.array(data[:,1]) *
                     np.diff(np.insert(data[:,2], 0, 0))) / 3600

# Find local extremes in capacity profile. These mark the boundaries between
# charge and discharge. Will not work with noise data, try using smooth() from
# scipy.signal first.
extremes_mask = np.r_[True, capacity[1:] > capacity[:-1]] & \
                np.r_[capacity[:-1] > capacity[1:], True] | \
                np.r_[True, capacity[1:] < capacity[:-1]] & \
                np.r_[capacity[:-1] < capacity[1:], True]
extremes = capacity[extremes_mask]

# Start counting from the first complete charge-discharge cycle.
extremes = extremes[1:]
if data[:,1][0] > 0:
    extremes = extremes[1:]
# Discard the final cycle if incomplete.
if data[:,1][-1] < 0 and data[:,0][-1] > 3:
    extremes = extremes[:-2]
elif data[:,1][-1] > 0:
    extremes = extremes[:-1]

# The difference between the upper and lower extremes is the amount of charge
# that has been inserted or recovered from the cell.
charge_capacity = np.diff(extremes)[::2]
discharge_capacity = abs(np.diff(extremes)[1::2])
coulombic_efficiency = (discharge_capacity / charge_capacity) * 100
cycles = range(1, len(charge_capacity) + 1)

plt.subplot(211)
plt.plot(data[:,2] / 3600, data[:,0])
plt.xlabel('Time [h]'); plt.ylabel('Cell voltage [V]')

ax1 = plt.subplot(212)
ax2 = ax1.twinx()
axes = [ax1, ax2]

p1, = ax1.plot(cycles, charge_capacity, label='Charge')
p2, = ax1.plot(cycles, discharge_capacity, label='Discharge')
p3, = ax2.plot(cycles, coulombic_efficiency, 'r', label='Coulombic efficiency')
lines = [p1, p2, p3]

ax1.set_xlabel('Cycle #')
ax1.set_ylabel('Capacity [Ah]')
ax2.set_ylabel('Coulombic efficiency [%]')
for ax in axes:
    ax.ticklabel_format(useOffset=False)

ax1.legend(lines, [l.get_label() for l in lines])

plt.show()
