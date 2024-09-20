from machine import SoftSPI, Pin
import ili9XXX
from xpt2046_cyd import xpt2046

''' Initialize CYD
    LVGL is initialized via display driver '''
disp = ili9XXX.ili9341(clk=14, cs=15,
                       dc=2, rst=12, power=23, miso=12,
                       mosi=13, width = 320, height = 240,
                       rot = 0xC0, colormode=ili9XXX.COLOR_MODE_RGB,
                                double_buffer = False, factor = 16)

spiTouch = SoftSPI(baudrate = 2500000, sck = Pin(25),
                    mosi = Pin(32), miso = Pin(39))

touch = xpt2046(spi = spiTouch, cs = Pin(33), cal_x0 = 3700,
            cal_y0 = 3820, cal_x1 = 180, cal_y1 = 250, transpose=False)

''' Backlight may be controlled via PWM to adjust brightness '''
backlight = Pin(21, Pin.OUT)
backlight(1)