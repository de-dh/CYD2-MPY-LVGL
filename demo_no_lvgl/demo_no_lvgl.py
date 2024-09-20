"""ILI9341 XPT2046 touch demo for cheap yellow display."""
from ili9341 import Display, color565
from xpt2046 import Touch
from machine import Pin, SPI, PWM 
import time
    
    
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
        self.mark_touch = True # True, False --> Show touch coordinates
        self.Touch_items = []
        self.Touch_callbacks = []
        
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
        
        # Assign touch callbacks and draw elements on screen
        self.draw()

    
    def draw(self):
        ''' Draw text and assign a callback to touch event at rectangular area '''
        
        text = 'Touch Area 1'
        self.Screen.draw_text8x8(108, 108, text,
                                 color565(0, 0, 0), color565(255, 255, 255))
        item = self.TouchArea(self, 100, 100, 15 + 8 * len(text), 20, True)
        self.addTouchItem(item, lambda x: print('Area 1'))
        
        
        text = 'Touch Area 2'
        self.Screen.draw_text8x8(168, 168, text,
                                 color565(0, 0, 0), color565(255, 255, 255))
        item2 = self.TouchArea(self, 160, 160, 15 + 8 * len(text), 20, True)
        self.addTouchItem(item2, lambda x: print('Area 2'))
        
        
        ''' Draw shutdown icon and bind callback to it '''
        a = 5    # Move the icon
        b = 190	 # Move the icon
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
        
        if self.mark_touch:
            self.Screen.fill_circle(x, y, 4, color_rgb(155, 155, 155))
            self.Screen.draw_circle(x, y, 4, color_rgb(255, 255, 255))
        
        
        if len(self.Touch_items) > 0:
            for i, item in enumerate(self.Touch_items):
                if x in item.TouchX and y in item.TouchY:
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
        
        ''' Draw the outline of the touch area '''
        def draw(self):
            self.color = color_rgb(70, 0, 0)
            
            for i in range(2):
                self.parent.Screen.draw_rectangle(self.x+i, self.y+i,
                                               self.width-2*i, self.height-2*i,
                                               color_rgb(255, 0, 0))        


try:
    x = TouchScreen()
    
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nCtrl-C pressed.  Cleaning up and exiting...")
#finally:
    x.shutdown()
        


