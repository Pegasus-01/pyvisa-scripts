def keithley2xxx_measure_voltage(instrument):
    voltage = instrument.ask_for_values('MEASure:VOLTage?')[0]
    return voltage

def keithley2xxx_measure_current(instrument):
    current = instrument.ask_for_values('MEASure:CURRent?')[0]
    return current
