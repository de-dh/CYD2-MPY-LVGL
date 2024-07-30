"""ILI9341 demo (simple touch demo)."""
from ili9341 import Display, color565
from xpt2046 import Touch
from machine import idle, Pin, SPI, PWM 
import time
import os
import sys

    
    
def color_rgb(r, g, b):
    return color565(r, g, b)

'''
TouchScreen (0, 0) = corner diagonal to usb port 
'''

class TouchScreen(object):
    """Touchscreen simple demo."""
    CYAN = color_rgb(0, 255, 255)
    PURPLE = color_rgb(255, 0, 255)
    WHITE = color_rgb(255, 0, 0)
    
    def __init__(self):
        self.spi_display = SPI(1, baudrate=10000000,
                        sck=Pin(14), mosi=Pin(13))
        
        self.Screen = Display(self.spi_display, dc=Pin(2), cs=Pin(15),
                              rst=Pin(15), width = 320, height = 240,
                              bgr = False, gamma = True)
        
        self.backlight = Pin(21, Pin.OUT)
        self.backlight.on()
        
        self.spi_touch = SPI(2, baudrate=1000000, sck=Pin(25),
                        mosi=Pin(32), miso=Pin(39))

        self.Touch = Touch(self.spi_touch, cs=Pin(33), int_pin=Pin(36),
                           int_handler=self.touchscreen_press)
        
        self.Screen.clear(color565(255,255,255))
        
        #self.backlightPWM = PWM(self.backlight, freq=5000, duty_u16=32768)
        
        
        
        self.Touch_items = []
        self.Touch_callbacks = []
        
        self.draw()

    
    def draw(self):
        item = self.TouchArea(self, 100, 100, 50, 50, True)
        self.addTouchItem(item, lambda x: print('Test'))
        
        item2 = self.TouchArea(self, 160, 160, 50, 50, True)
        self.addTouchItem(item2, lambda x: print('Test2'))
        
        a = 5
        b = 190
        self.Screen.fill_circle(300 - a, 220 - b, 18, color565(0, 0, 0))
        self.Screen.fill_circle(300 - a, 220 - b, 15, color565(255, 255, 255))
        self.Screen.fill_rectangle(295 - a, 197 - b, 10, 20, color565(255, 255, 255))
        self.Screen.fill_rectangle(298 - a, 197 - b, 4, 20, color565(0, 0, 0))
        
        
        item3 = self.TouchArea(self, 300 - a - 20, 220 - b - 20, 40, 40)
        self.addTouchItem(item3, lambda x: self.shutdown())
        
        
    def addTouchItem(self, item, cb):
        self.Touch_items.append(item)
        self.Touch_callbacks.append(cb)
        
    def shutdown(self):
        print('Shutdown.')
        self.spi_touch.deinit()
        #self.backlightPWM.deinit()
        self.backlight.off()
        self.Screen.cleanup()
        sys.exit(0)
        
    def touchscreen_press(self, x, y):
        """Process touchscreen press events."""
        x, y = y, x
        #print('Touch', x, y)
        self.Screen.fill_circle(x, y, 4, color_rgb(155, 155, 155))
        self.Screen.draw_circle(x, y, 4, color_rgb(255, 255, 255))
        
        
        if len(self.Touch_items) > 0:
            for i, item in enumerate(self.Touch_items):
                if x in item.TouchX and y in item.TouchY:
                    item.press()
                    self.Touch_callbacks[i](i)
                    
    class TouchArea:
        ''' Bind callback to rectangular touch area'''
        def __init__(self, parent, x, y, w, h, draw = False):
            self.parent = parent
            self.x = x
            self.y = y
            self.width = w
            self.height = h
            
            self.TouchX = range(self.x, self.x + self.width)
            self.TouchY = range(self.y, self.y + self.height)
            
            if draw is True:
                self.draw()
            
        def draw(self):
            self.color = color_rgb(70, 0, 0)
            
            for i in range(2):
                self.parent.Screen.draw_rectangle(self.x+i, self.y+i,
                                               self.width-2*i, self.height-2*i,
                                               color_rgb(255, 0, 0))        
        def press(self):
            pass
            
            
        



try:
    x = TouchScreen()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nCtrl-C pressed.  Cleaning up and exiting...")
#finally:
    x.shutdown()
        


