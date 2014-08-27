def amrelpla_constant_current(instrument, setcurrent=0, input_on=0):
    """Put Amrel PLA800-60-300 programmable power sink into constant current mode.

    :param instrument: Instrument object to control. Use get_instrument() function of
                       visa.ResourceManager() object to assign a name to an instrument.
    :param setcurrent: Sets the current (unit ampere). Defaults to 0.
    :param input_on:  Controls instrument input status, i.e. input_on=1 means the
                       instrument drawss current, input_on=0 means it does not. Defaults to 0.
    """
    instrument.write('CURRent %f; INPut %d' % (setcurrent, input_on))

def amrelpla_constant_voltage(instrument, setvoltage=0, input_on=0):
    """Put Amrel PLA800-60-300 programmable power sink into constant voltage mode.

    :param instrument: Instrument object to control. Use get_instrument() function of
                       visa.ResourceManager() object to assign a name to an instrument.
    :param setvoltage: Sets the voltage (unit volt). Defaults to 0.
    :param input_on:  Controls instrument input status, i.e. input_on=1 means the
                       instrument draws current, input_on=0 means it does not. Defaults to 0.
    """
    instrument.write('VOLTage %f; INPut %d' % (setvoltage, input_on))
