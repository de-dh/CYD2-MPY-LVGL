'''
Modified xpt2046 driver for use with lvgl on ESP32-2432S028
aka CYD with two usb ports.

Original source: Stefan Scholz,
https://stefan.box2code.de/2023/11/18/esp32-grafik-mit-lvgl-und-micropython/

Modified by D. Hennig for use in portrait mode.
'''
from machine import SPI
import lvgl as lv
import espidf as esp

class xpt2046:
    CMD_X_READ  = const(0x90)
    CMD_Y_READ  = const(0xd0)
    CMD_Z1_READ = const(0xb8)
    CMD_Z2_READ = const(0xc8)

    MAX_RAW_COORD = const((1<<12) - 1)

    def __init__(self, spi, cs, max_cmds=16, cal_x0 = 3783, cal_y0 = 3948, cal_x1 = 242, cal_y1 = 423,
                 transpose = True, samples = 3, portrait = False):

        # Initializations

        if not lv.is_initialized():
            lv.init()
        
        self.portrait = portrait
        
        disp = lv.disp_t.__cast__(None)
        
        self.screen_width = 240 if self.portrait else 320
        self.screen_height = 320 if self.portrait else 240
        
        self.spi = spi
        self.cs = cs
        self.recv = bytearray(3)
        self.xmit = bytearray(3)

        self.max_cmds = max_cmds
        self.cal_x0 = cal_x0
        self.cal_y0 = cal_y0
        self.cal_x1 = cal_x1
        self.cal_y1 = cal_y1
        self.transpose = transpose
        self.samples = samples

        self.touch_count = 0
        self.touch_cycles = 0

        indev_drv = lv.indev_drv_t()
        indev_drv.init()
        indev_drv.type = lv.INDEV_TYPE.POINTER
        indev_drv.read_cb = self.read
        indev_drv.register()

    def calibrate(self, x0, y0, x1, y1):
        self.cal_x0 = x0
        self.cal_y0 = y0
        self.cal_x1 = x1
        self.cal_y1 = y1

    def deinit(self):
        print('Deinitializing XPT2046...')

    def touch_talk(self, cmd, bits):
        if self.cs is not None:
            self.cs(0)
        self.xmit[0] = cmd
        self.spi.write_readinto(self.xmit, self.recv)
        if self.cs is not None:
            self.cs(1)
        return (self.recv[1] * 256 + self.recv[2]) >> (15 - bits)

    # @micropython.viper
    def xpt_cmds(self, cmds):
        result = []
        for cmd in cmds:
            value = self.touch_talk(cmd, 12)
            if value == int(self.MAX_RAW_COORD):
                value = 0
            result.append(value)
        return tuple(result)

    # @micropython.viper
    def get_med_coords(self, count : int):
        mid = count//2
        values = []
        for i in range(0, count):
            values.append(self.xpt_cmds([self.CMD_X_READ, self.CMD_Y_READ]))
        x_values = sorted([x for x,y in values])
        y_values = sorted([y for x,y in values])
        if int(x_values[0]) == 0 or int(y_values[0]) == 0 : return None
        #print(x_values[mid], y_values[mid])
        return x_values[mid], y_values[mid]

    # @micropython.viper
    def get_coords(self):
        med_coords = self.get_med_coords(int(self.samples))
        if not med_coords: return None
        if self.transpose:
            raw_y, raw_x = med_coords
        else:
            raw_x, raw_y = med_coords

        if int(raw_x) != 0 and int(raw_y) != 0:
            if self.portrait:
                x = self.screen_width - (((int(raw_y) - int(self.cal_y0)) * int(self.screen_width)) // (int(self.cal_y1) - int(self.cal_y0)))
                y = ((int(raw_x) - int(self.cal_x0)) * int(self.screen_height)) // (int(self.cal_x1) - int(self.cal_x0))
            else:
                x = ((int(raw_x) - int(self.cal_x0)) * int(self.screen_width)) // (int(self.cal_x1) - int(self.cal_x0))
                y = ((int(raw_y) - int(self.cal_y0)) * int(self.screen_height)) // (int(self.cal_y1) - int(self.cal_y0))
            return x,y
        else: return None

    # @micropython.native
    def get_pressure(self, factor : int) -> int:
        z1, z2, x = self.xpt_cmds([self.CMD_Z1_READ, self.CMD_Z2_READ, self.CMD_X_READ])
        if int(z1) == 0: return -1
        return ( (int(x)*factor) / 4096)*( int(z2)/int(z1) - 1)

    start_time_ptr = esp.C_Pointer()
    end_time_ptr = esp.C_Pointer()
    cycles_in_ms = esp.esp_clk_cpu_freq() // 1000

    # @micropython.native
    def read(self, indev_drv, data) -> int:

        esp.get_ccount(self.start_time_ptr)
        coords = self.get_coords()
        #print(coords)
        esp.get_ccount(self.end_time_ptr)

        if self.end_time_ptr.int_val > self.start_time_ptr.int_val:
            self.touch_cycles +=  self.end_time_ptr.int_val - self.start_time_ptr.int_val
            self.touch_count += 1

        if coords:
            data.point.x ,data.point.y = coords
            data.state = lv.INDEV_STATE.PRESSED
            return False
        data.state = lv.INDEV_STATE.RELEASED
        return False

    def stat(self):
        return self.touch_cycles / (self.touch_count * self.cycles_in_ms)