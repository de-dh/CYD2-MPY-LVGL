import uasyncio as asyncio
from machine import Pin, PWM, RTC, SoftSPI
import time
import lv_utils
import lvgl as lv
from xpt2046_cyd import xpt2046
import ili9XXX
import gc

class Updater:
    def __init__(self, app):
        self.app = app
        self.rtc = RTC()
        self.idle_state = 0
        self.min_old = -1
        self.day_old = -1
        
        self.time = None
        self.date = None
    
    def update_time(self, now):
        self.min_old = now[6]
        self.time = '{:02d}:{:02d}:{:02d}'.format(now[4], now[5], now[6])
        self.app.update_ui('Time', self.time)

    def update_date(self, now):
        self.day_old = now[2]
        self.date = '{:02d}.{:02d}.{:04d}'.format(now[2], now[1], now[0])
        self.app.update_ui('Date', self.date)
    
    async def update(self):
        try:
            while True:
                now = self.rtc.datetime()

                # Update time every minute
                if self.min_old != now[6]:
                    self.update_time(now)
                    
                # Update date every day
                if self.day_old != now[2]:
                    self.update_date(now)
                    
                # Power off display when idle for 60s
                idle_time = lv.disp_get_default().get_inactive_time()
                if idle_time > (60 * 1000) and self.idle_state == 0:
                    self.idle_state = 1
                    self.app.backlight.duty(0)
                elif idle_time < (2 * 1000) and self.idle_state == 1:
                    self.idle_state = 0
                    self.app.backlight.duty(1023)
                    
                # Main loop delay
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print('Updater task cancelled.')


class App(Updater):
    screens = {}
    screen_order = [] 

    @classmethod
    def register_screen(cls, order):
        '''Decorator function to register a screen with a navigation order.'''
        def decorator(screen_cls):
            cls.screens[screen_cls.__name__] = screen_cls
            cls.screen_order.append((order, screen_cls.__name__))
            cls.screen_order.sort(key=lambda x: x[0])
            
            original_init = screen_cls.__init__

            def new_init(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                self.set_style_bg_color(lv.color_white(), lv.PART.MAIN)
                app = args[0]

                screen_names = [screen[1] for screen in cls.screen_order]
                current_idx = screen_names.index(screen_cls.__name__)

                # Add Next button if not the last screen
                if current_idx < len(screen_names) - 1:
                    next_screen = screen_names[current_idx + 1]
                    next_btn = lv.btn(self)
                    next_btn.set_size(30, 30)
                    next_btn.align(lv.ALIGN.BOTTOM_RIGHT, -5, -5)
                    next_btn_lbl = lv.label(next_btn)
                    next_btn_lbl.set_text(lv.SYMBOL.RIGHT)
                    next_btn_lbl.center()
                    next_btn.add_event_cb(lambda e: app.load_screen(next_screen), lv.EVENT.CLICKED, None)

                # Add Previous button if not the first screen
                if current_idx > 0:
                    prev_screen = screen_names[current_idx - 1]
                    prev_btn = lv.btn(self)
                    prev_btn.set_size(30, 30)
                    prev_btn.align(lv.ALIGN.BOTTOM_LEFT, 5, -5)
                    prev_btn_lbl = lv.label(prev_btn)
                    prev_btn_lbl.set_text(lv.SYMBOL.LEFT)
                    prev_btn_lbl.center()
                    prev_btn.add_event_cb(lambda e: app.load_screen(prev_screen), lv.EVENT.CLICKED, None)

            # Replace the original __init__ with the new one
            screen_cls.__init__ = new_init

            return screen_cls
        return decorator
    
    def __init__(self):
        super().__init__(self)
        self.act_screen = None
        self.prev_screen = None
        self.act_screen_id = None
        
        try:
            self.disp = ili9XXX.ili9341(clk=14, cs=15,
                                       dc=2, rst=12, power=23, miso=12,
                                       mosi=13, width=320, height=240,
                                       rot=0xC0, colormode=ili9XXX.COLOR_MODE_RGB,
                                       double_buffer=False, factor=16, asynchronous=True)
        except Exception as e:
            print(f'Display initialization failed: {e}')

        try:
            self.spiTouch = SoftSPI(baudrate=2500000, sck=Pin(25),
                                    mosi=Pin(32), miso=Pin(39))
            self.touch = xpt2046(spi=self.spiTouch, cs=Pin(33), cal_x0=3700,
                                 cal_y0=3820, cal_x1=180, cal_y1=250, transpose=False)
        except Exception as e:
            print(f'Touch initialization failed: {e}')

        try:
            self.backlight = PWM(Pin(21), freq=1000)
            self.backlight.duty(1023)
        except Exception as e:
            print(f'Backlight initialization failed: {e}')

        self.group = lv.group_create()
        self.group.set_default()

        # Load the initial screen
        self.load_screen('ScreenMain')

    def update_ui(self, element_id, text):
        elements = {'Time': 'timeLbl',
                    'Date': 'dateLbl'}
        
        if not (element_id in elements):
            print(f'Label {element_id} is not registered for update.')
            return False
        
        try:
            attr = getattr(self.act_screen, elements[element_id])
        except AttributeError:
            attr = None
        finally:
            if attr is not None:
                attr.set_text(str(text))
            
    def load_screen(self, scr_id):
        #Loads a screen by its class name provided as string
        gc.collect()
        print(f'Loading screen {scr_id}\nFree memory: {gc.mem_free()}')

        if scr_id not in self.screens:
            print('Unknown screen!')
            return False

        if self.prev_screen is not None:
            self.prev_screen.del_async()
            gc.collect()

        if self.act_screen is not None:
            self.prev_screen = self.act_screen

        try:
            # Get the screen class from the scr_id and instantiate it
            self.act_screen = self.screens[scr_id](self)
            self.act_screen_id = scr_id
            lv.scr_load(self.act_screen)
            gc.collect()
        except Exception as e:
            print(f'Error loading screen {scr_id}: {e}')
            gc.collect()



# Screens defined and registered via the @App.register_screen decorator
@App.register_screen(1)
class ScreenMain(lv.obj):
    def __init__(self, app, *args, **kwds):
        self.app = app
        super().__init__(*args, **kwds)
        
        self.titleLbl = lv.label(self)
        self.titleLbl.set_style_text_font(lv.font_montserrat_16, 0)
        self.titleLbl.set_style_text_color(lv.color_black(), 0)
        self.titleLbl.set_text('Main Screen')
        self.titleLbl.center()

        self.timeLbl = lv.label(self)
        t = '-' if self.app.time is None else self.app.time
        self.timeLbl.set_text(t)
        self.timeLbl.align(lv.ALIGN.TOP_LEFT, 255, 3)
    
        self.dateLbl = lv.label(self)
        d = '-' if self.app.date is None else self.app.date
        self.dateLbl.set_text(d)
        self.dateLbl.align(lv.ALIGN.TOP_LEFT, 5, 3)


@App.register_screen(2)
class ScreenChart(lv.obj):
    def __init__(self, app, *args, **kwds):
        self.app = app
        super().__init__(*args, **kwds)
        
        file_path = 'log/counter_log.csv'
        x_data, y_data = read_csv(file_path)
        

        chart = lv.chart(self)
        chart.set_size(275, 150)
        chart.align(lv.ALIGN.TOP_LEFT, 35, 30)

        chart.set_style_line_width(0, lv.PART.ITEMS)   # Remove the lines
        chart.set_style_line_width(0, lv.PART.MAIN)
        chart.set_type(lv.chart.TYPE.SCATTER)

        #lv_chart_set_axis_tick(chart, axis, major_len, minor_len, major_cnt, minor_cnt, label_en, draw_size)
        chart.set_axis_tick(lv.chart.AXIS.PRIMARY_X, 5, 2, 7, 5, True, 30)
        chart.set_axis_tick(lv.chart.AXIS.PRIMARY_Y, 10, 5, 4, 5, True, 30)

        chart.set_range(lv.chart.AXIS.PRIMARY_X, x_data[0], x_data[0] + 29)
        chart.set_range(lv.chart.AXIS.PRIMARY_Y, 1, 30)

        chart.set_point_count(len(x_data))

        ser = chart.add_series(lv.palette_main(lv.PALETTE.RED), lv.chart.AXIS.PRIMARY_Y)

        ser.x_points = x_data
        ser.y_points = y_data
        
        yLbl = lv.label(self)
        yLbl.set_text('d / km')
        yLbl.align_to(chart, lv.ALIGN.OUT_TOP_LEFT, -30, 0)

        xLbl = lv.label(self)
        xLbl.set_text('t / days')
        xLbl.align_to(chart, lv.ALIGN.OUT_BOTTOM_MID, 0, 25)
        print(f'Chart loaded \nFree memory: {gc.mem_free()}')



@App.register_screen(3)
class Screen3(lv.obj):
    def __init__(self, app, *args, **kwds):
        self.app = app
        super().__init__(*args, **kwds)
        
        self.title = lv.label(self)
        self.title.set_style_text_font(lv.font_montserrat_16, 0)
        self.title.set_style_text_color(lv.color_black(), 0)
        self.title.set_text('Screen 3')
        self.title.center()


def calculate_distance(meters):
    distance = meters / 1000
    return distance

def parse_timestamp(timestamp_str):
    date_str = timestamp_str.split(' ')[0]
    year, month, day = [int(x) for x in date_str.split('-')]
    return year, month, day


'''Read data from .csv-file and parse data for display in chart

    - counter_log.csv contains a timestamp and a measured distance in meters
    - the distance is converted to km
    - the timestamps are compared and the days elapsed since the first
        timestamp are shown in the diagram
    '''
def read_csv(file_path):
    x_values = []
    y_values = []
    max_values = 30

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
            first_line = lines[0].strip().split(',')
            first_timestamp_str = first_line[0]
            
            first_year, first_month, first_day = parse_timestamp(first_timestamp_str)
            first_date = time.mktime((first_year, first_month, first_day, 0, 0, 0, 0, 0))
            
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    timestamp_str = parts[0]
                    distance_str = parts[1]
                    
                    year, month, day = parse_timestamp(timestamp_str)
                    date = time.mktime((year, month, day, 0, 0, 0, 0, 0))
                    
                    days_since_first = int((date - first_date) / (24 * 3600)) + 1
                    
                    # Calculate distance in km and round it
                    distance = int(round(calculate_distance(int(distance_str))))
                    
                    x_values.append(days_since_first)
                    y_values.append(distance)
            
         
        if len(x_values) > max_values:
            x_values = x_values[-max_values:]
            y_values = y_values[-max_values:]
            
        return x_values, y_values
    except Exception as e:
        print('Error loading file: ', e)


async def main():
    app = App()
    gc.collect()
    
    update_task = asyncio.create_task(app.update())
    
    if not lv_utils.event_loop.is_running():
        eventloop = lv_utils.event_loop(asynchronous=True)

    loop = asyncio.get_event_loop()
    loop.run_forever()

asyncio.run(main())

