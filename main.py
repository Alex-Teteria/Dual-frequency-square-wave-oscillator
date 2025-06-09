
switch_modes = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

if switch_modes.value() == 1:
    import oscillator
else:
    import medical_oscillator
    