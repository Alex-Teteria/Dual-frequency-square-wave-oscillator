# ----------------------------------------------------------------
# Генератор прямокутних імпульсів
# ----------------------------------------------------------------
# Діапазон частот 0 - 2,00 кГц
# Крок встановлення частот 0,01 Гц
# Встановлення чатот енкодером типу KY-040
# Для індикації - 16х2 LCD дисплей з інтерфейсом I2C
# ----------------------------------------------------------------
# Author: Alex Teteria
# v0.4
# 31.05.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import machine, time
from machine import Pin, I2C
from rotary_irq_rp2 import RotaryIRQ
from DIYables_MicroPython_LCD_I2C import LCD_I2C
import uasyncio as asyncio


#initialization LCD
I2C_ADDR = 0x27  # Use the address found using the I2C scanner
LCD_COLS = 16
LCD_ROWS = 2
i2c=I2C(1, scl=Pin(27),sda=Pin(26))
lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)

led = machine.Pin(25, machine.Pin.OUT)
f1_out = machine.Pin(16, machine.Pin.OUT)
btn_current_digit = machine.Pin(8, machine.Pin.IN)
switch_modes = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

def callback():
    event.set()

async def main():
    r.add_listener(callback)
    val_old = r.value()
    
    asyncio.create_task(blink_symbol())
    asyncio.create_task(set_current_digit())
    asyncio.create_task(change_mode())
    while True:
        await event.wait()
        val_new = r.value()
        if val_old < val_new:
            direction = 1
        else:
            direction = -1
        val_old = val_new
        count_f(direction)
        # print('result =', r.value(), direction)
        set_f1(f1)
        event.clear()


async def change_mode():
    while True:
        if switch_modes.value() == 0:
            with open('value.txt', 'w') as file_out:
                text_f = '{:07.2f}'.format(f1)
                print(text_f, file=file_out)
            machine.reset()
        await asyncio.sleep(0.01)    

async def set_current_digit():
    global current_digit
    while True:
        btn_prev = btn_current_digit.value()
        while btn_current_digit.value() == 1 or btn_current_digit.value() == btn_prev:
            btn_prev = btn_current_digit.value()
            await asyncio.sleep(0.01)
        current_digit = 5 if (current_digit + 1) % 7 == 4 else (current_digit + 1) % 7

def count_f(direction):
    global f1
    delta = direction * multiplier[current_digit]
    if f1 + delta > 2000:
        f1 = 2000.0
    elif f1 + delta < 0:
        f1 = 0.0
    else:
        f1 += delta
    f1 = round(f1, 2)
    

def draw_frequency_table(text_f):
    lcd.set_cursor(5, 0)
    lcd.print(text_f)
    

def draw_frequency(text_f):
    lcd.backlight_on()
    lcd.clear()
    lcd.set_cursor(1, 0)
    lcd.print('F1: ' + text_f + ' Hz')

async def blink_symbol():
    while True:
        text_f = '{:07.2f}'.format(f1)
        draw_frequency_table(text_f)
        blank_symbol(current_digit)
        time.sleep(0.2)
        lcd.set_cursor(5 + current_digit, 0)
        lcd.print(text_f[current_digit])
        await asyncio.sleep(0.2)

def blank_symbol(num):
        lcd.set_cursor(num + 5, 0)
        lcd.print(' ')
        
def f_1(t):
    f1_out.toggle()

def set_f1(freq):
    if freq < 0.01:
        freq = 0.01
    tim_1.init(freq=freq*2, mode=machine.Timer.PERIODIC, callback=f_1)

r = RotaryIRQ(pin_num_clk=6,
              pin_num_dt=7,
              reverse=True,
              #min_val=0,
              #max_val=9,
              #range_mode=RotaryIRQ.RANGE_WRAP
              range_mode=RotaryIRQ.RANGE_UNBOUNDED
              )

f1 = 1234.00
current_digit = 2
draw_frequency('{:07.2f}'.format(f1))
multiplier = {0: 1000, 1: 100, 2: 10, 3: 1, 5: 0.1, 6: 0.01}

tim_1 = machine.Timer(freq=f1*2, mode=machine.Timer.PERIODIC, callback=f_1)

event = asyncio.Event()
asyncio.run(main())
