# ----------------------------------------------------------------
# Двочастотний генератор прямокутних імпульсів
# ----------------------------------------------------------------
# Діапазон частот 0 - 2,00 кГц
# Крок встановлення частот 0,01 Гц
# На одному виході - імпульси першої частоти - безперервно,
# на іншому - періодично, 15 сек. імпульси першої частоти, потім 15 сек. - імпульси другої частоти.
# Тривалість наявності імпульсів на виходах задається таймером
#   в діапазоні 10 - 25 хв. з кроком 0,5 хв.
# Встановлення чатот та таймера енкодером типу KY-040
# Для індикації - 16х2 LCD дисплей з інтерфейсом I2C
# ----------------------------------------------------------------
# Author: Alex Teteria
# v0.5
# 04.06.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license


import machine, time
from machine import Pin, I2C
import uasyncio
from frequency_generator import Two_frequencies
from DIYables_MicroPython_LCD_I2C import LCD_I2C
from rotary_irq_rp2 import RotaryIRQ


#initialization LCD
I2C_ADDR = 0x27  # Use the address found using the I2C scanner
LCD_COLS = 16
LCD_ROWS = 2
i2c=I2C(1, scl=Pin(27),sda=Pin(26))
lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)

gen_enable = False
btn_stop = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
btn_run = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
switch_modes = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
btn_oled = machine.Pin(8, machine.Pin.IN)
led = machine.Pin(20, machine.Pin.OUT)
beep_out = machine.Pin(18, machine.Pin.OUT)

def generator_stop():
    global gen_enable
    if not btn_stop():
        led.value(0)
        gen_enable = False
    return gen_enable

async def run_task():
    while True:
        out.run()
        await uasyncio.sleep(0.04)      
        
async def generator_run():
    global gen_enable, timer
    while True:
        if not btn_run():
            text_timer = '{:04.1f}'.format(timer)
            led.value(1)
            if text_timer[3] == '0':
                timer_value = 60_000 * int(text_timer[:2])
            else:
                timer_value = 60_000 * int(text_timer[:2]) + 30_000
            tim.init(period=timer_value, callback=tim_run, mode=machine.Timer.ONE_SHOT)
            out.set_f1(f1)
            out.set_f2(f2)
            print('f1=', f1)
            print('f2=', f2)
            print('time=', text_timer)
            gen_enable = True
        await uasyncio.sleep(0.04)      

def blank_symbol(num, num_display):
    if num_display == 0:
        lcd.set_cursor(num + 5, 0)
        lcd.print(' ')
    elif num_display == 1:
        lcd.set_cursor(num + 5, 1)
        lcd.print(' ')
        

def blank_symbol_timer(num):
    lcd.set_cursor(num + 7, 0)
    lcd.print(' ')

async def blink_symbol():
    while True:
        text_f1 = '{:07.2f}'.format(f1)
        text_f2 = '{:07.2f}'.format(f2)
        if display_cnt == 0 or display_cnt == 1:
            draw_frequency(text_f1, text_f2)
            d = {0: (text_f1, 0), 1: (text_f2, 1), 2: None}
            blank_symbol(current_digit, display_cnt)
            time.sleep(0.2)
            text_f, h = d[display_cnt]
            lcd.set_cursor(5 + current_digit, h)
            lcd.print(text_f[current_digit])
        await uasyncio.sleep(0.2)

async def blink_timer():
    digit_set_1 = {0, 3}
    digit_set_2 = {1, 5}
    while True:
        text_timer = '{:04.1f}'.format(timer)
        if display_cnt == 2:
            if current_digit in digit_set_1:
                timer_digit = 0
            elif current_digit in digit_set_2:
                timer_digit = 1
            else:
                timer_digit = 3    
            draw_timer(text_timer)
            blank_symbol_timer(timer_digit)
            time.sleep(0.2)
            draw_timer(text_timer)
        await uasyncio.sleep(0.2)    

def get_timer_digit(set_1, set_2):
    if current_digit in set_1:
        timer_digit = 2
    elif current_digit in set_2:
        timer_digit = 3
    else:
        timer_digit = 5
    return timer_digit    


def count_timer(direction, digit):
    global timer
    if digit == 5:
        delta = 0.5 if direction == 1 else -0.5
    else:
        delta = direction * multiplier[digit]
    if timer + delta > 25:
        timer = 25.0
    elif timer + delta < 10:
        timer = 10.0
    else:
        timer = round(timer + delta, 1)


def count_f(direction):
    global f1, f2   
    f = f1 if display_cnt == 0 else f2
    delta = direction * multiplier[current_digit]
    if f + delta > 2000:
        f = 2000.0
    elif f + delta < 0:
        f = 0.0
    else:
        f += delta
    if display_cnt == 0:
        f1 = round(f, 2)
    else:
        f2 = round(f, 2)
    

def draw_frequency(text_1, text_2):
    #lcd.backlight_on()
    #lcd.clear()
    lcd.set_cursor(1, 0)
    lcd.print('F1: ' + text_1 + ' Hz')
    lcd.set_cursor(1, 1)
    lcd.print('F2: ' + text_2 + ' Hz')

def draw_timer(text):
    lcd.set_cursor(1, 0)
    lcd.print('Time: ' + text + ' min')
    lcd.set_cursor(1, 1)
    lcd.print('              ')


async def change_mode():
    while True:
        if switch_modes.value() == 1:
            machine.reset()
        await uasyncio.sleep(0.01)    

def callback():
    event.set()

async def main():
    r.add_listener(callback)
    digit_set_1 = {0, 3}
    digit_set_2 = {1, 5}
    val_old = r.value()
    
    uasyncio.create_task(run_task())
    uasyncio.create_task(generator_run())
    uasyncio.create_task(blink_symbol())
    uasyncio.create_task(blink_timer())
    uasyncio.create_task(change_mode())
    uasyncio.create_task(wait_button())
    while True:
        await event.wait()
        val_new = r.value()
        if val_old < val_new:
            direction = 1
        else:
            direction = -1
        val_old = val_new
        if display_cnt == 2:
            count_timer(direction, get_timer_digit(digit_set_1, digit_set_2))
        else:
            count_f(direction)
        event.clear()


async def wait_button():
    global display_cnt, current_digit
    while True:
        btn_prev = btn_oled.value()
        while btn_oled.value() == 1 or btn_oled.value() == btn_prev:
            btn_prev = btn_oled.value()
            await uasyncio.sleep(0.04)
            
        await uasyncio.sleep(1)
        if btn_oled.value() == 0:
            display_cnt = (display_cnt + 1) % 3
        else:
            current_digit = 5 if (current_digit + 1) % 7 == 4 else (current_digit + 1) % 7
                 

def tim_run(t):
    global gen_enable
    gen_enable = False
    led.value(0)
    beep()

def beep():
    for i in range(16000):
        beep_out.toggle()
        time.sleep_us(130)
    beep_out.value(0)    

try:
    with open('value.txt') as file:
        f1 = float(file.readline().rstrip())
except:
    f1 = 1234.00

f2 = 1234.00
timer = 10.0
display_cnt = 0
current_digit = 2
multiplier = {0: 1000, 1: 100, 2: 10, 3: 1, 5: 0.1, 6: 0.01}

draw_frequency('{:07.2f}'.format(f1), '{:07.2f}'.format(f2))
draw_timer('{:04.1f}'.format(timer))
out = Two_frequencies(f1, f2, enable=generator_stop, pin_1=16, pin_2=17)
tim = machine.Timer()

r = RotaryIRQ(pin_num_clk=6, 
              pin_num_dt=7, 
              # min_val=0, 
              # max_val=9, 
              reverse=True, 
              #range_mode=RotaryIRQ.RANGE_WRAP
              #range_mode=RotaryIRQ.RANGE_BOUNDED
              range_mode=RotaryIRQ.RANGE_UNBOUNDED
              )
event = uasyncio.Event()
uasyncio.run(main())


    
    
