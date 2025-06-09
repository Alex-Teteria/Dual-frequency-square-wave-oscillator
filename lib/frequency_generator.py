# ----------------------------------------------------------------
# Модуль двочастотного генератора прямокутних імпульсів
# ----------------------------------------------------------------
# На одному виході - імпульси першої частоти - безперервно,
# на іншому - періодично, 15 сек. імпульси першої частоти, потім 15 сек. - імпульси другої частоти.
# ----------------------------------------------------------------
# Author: Alex Teteria
# v0.4
# 30.05.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import machine, time


class Two_frequencies():
    
    def __init__(self, freq_1, freq_2, enable=lambda: True, pin_1=16 , pin_2=25):
        self.freq_1 = freq_1
        self.freq_2 = freq_2
        self.out_1 = machine.Pin(pin_1, machine.Pin.OUT)
        self.out_2 = machine.Pin(pin_2, machine.Pin.OUT)
        self.tim_1 = machine.Timer(freq=self.freq_1*2, mode=machine.Timer.PERIODIC, callback=self.f_1)
        self.tim_2 = machine.Timer(freq=self.freq_2*2, mode=machine.Timer.PERIODIC, callback=self.f_2)
        self.enable = enable
        self.tim_mode = machine.Timer(period=15_000, mode=machine.Timer.PERIODIC, callback=self.f_mode)
        self.mode = True
        self.gen_1 = 0
        self.gen_2 = 0
        
    def f_1(self, t):
        self.gen_1 = not self.gen_1 

    def f_2(self, t):
        self.gen_2 = not self.gen_2           

    def f_mode(self, t):
        self.mode = not self.mode   

    def run(self):
        
        while self.enable():
            self.out_1.value(self.gen_1)
            if self.mode:
                self.out_2.value(self.gen_1)
            else:
                self.out_2.value(self.gen_2)
        self.gen_1 = False
        self.gen_2 = False
        self.out_1.value(0)
        self.out_2.value(0)
    
    def set_f1(self, freq):
        if freq < 0.01:
            freq = 0.01
        self.tim_1.init(freq=freq*2, mode=machine.Timer.PERIODIC, callback=self.f_1)

    def set_f2(self, freq):
        if freq < 0.01:
            freq = 0.01
        self.tim_2.init(freq=freq*2, mode=machine.Timer.PERIODIC, callback=self.f_2)


if __name__ == '__main__':
    button_run = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
    out_1 = Two_frequencies(5.0, 10.01, enable=button_run, pin_1=16, pin_2=25)
    while True:
        out_1.run()
        if not button_run():
            out_1.set_f1(20.0)
            out_1.set_f2(0.0)


