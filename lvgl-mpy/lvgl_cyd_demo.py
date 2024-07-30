'''Custom Driver xpt2046_cyd and MPY build from
https://stefan.box2code.de/2023/11/18/esp32-grafik-mit-lvgl-und-micropython/

Custom MPY-Build 'lv_micropython-WROOM.zip'
Flashed with esptool

Running on cheap yellow display with TWO USB Ports
--> display is worse than the original cyd with only one USB port
see: https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display/blob/main/cyd.md


Source of demo script:
https://sim.lvgl.io/v8.3/micropython/ports/javascript/index.html?script_startup=
https://raw.githubusercontent.com/lvgl/lvgl/
4d96c27ce35dd2ea6b34926f24a647e7ea7c4b0c/examples/header.py&script=
https://raw.githubusercontent.com/lvgl/lvgl/
4d96c27ce35dd2ea6b34926f24a647e7ea7c4b0c/examples/widgets/btn/lv_example_btn_2.py
'''
import sys
import espidf as esp
from machine import *
import ili9XXX
import lvgl as lv
import time
from xpt2046_cyd import xpt2046
import gc

'''
import network
import espnow  <-- module doesn't exist?

>> ImportError: no module named 'espnow'
'''

try:
    '''Calibration commands for ili9341 display from:
    https://github.com/rdagger/micropython-ili9341

        MIRROR_ROTATE = {  # MADCTL configurations for rotation and mirroring
        (False, 0): 0x80,  # 1000 0000
        (False, 90): 0xE0,  # 1110 0000
        (False, 180): 0x40,  # 0100 0000
        (False, 270): 0x20,  # 0010 0000
        (True, 0): 0xC0,   # 1100 0000 <--- Mirroring in ls mode
        (True, 90): 0x60,  # 0110 0000
        (True, 180): 0x00,  # 0000 0000
        (True, 270): 0xA0  # 1010 0000
    }
    '''
    
    '''
    Correct calibration for display in landscape mode
    
    Upper left corner (where the USB ports are located) is touch = (0, 0)
    Custom MADCTL from other ili9341 driver for mirroring in landscape mode: rot = 0xC0
    
    Colors are wrong, swap_rgb565_bytes not available (due to build?)
    lv.PALETTE.BLUE --> Orange on screen
    '''
    disp = ili9XXX.ili9341(clk=14, cs=15,
                           dc=2, rst=12, power=23, miso=12,
                           mosi=13, width = 320, height = 240,
                           rot = 0xC0)
    
    spi2=SoftSPI(baudrate=2500000,sck=Pin(25),mosi=Pin(32),miso=Pin(39))
    
    # custom touch driver, see start of document
    touch = xpt2046(spi=spi2, cs=Pin(33), cal_x0 = 3700,
                cal_y0 = 3820, cal_x1 = 180, cal_y1 = 250, transpose=False)
    
    bgl = Pin(21, Pin.OUT) # Backlight initialized seperately for testing
    bgl(1)
    
    style = lv.style_t()
    style.init()

    style.set_radius(3)

    style.set_bg_opa(lv.OPA.COVER)
    style.set_bg_color(lv.palette_main(lv.PALETTE.BLUE))
    style.set_bg_grad_color(lv.palette_darken(lv.PALETTE.BLUE, 2))
    style.set_bg_grad_dir(lv.GRAD_DIR.VER)

    style.set_border_opa(lv.OPA._40)
    style.set_border_width(2)
    style.set_border_color(lv.palette_main(lv.PALETTE.GREY))

    style.set_shadow_width(8)
    style.set_shadow_color(lv.palette_main(lv.PALETTE.GREY))
    style.set_shadow_ofs_y(8)

    style.set_outline_opa(lv.OPA.COVER)
    style.set_outline_color(lv.palette_main(lv.PALETTE.BLUE))

    '''
    Originally lv.color_white() --> looks bad, text is barely visible
    '''
    style.set_text_color(lv.color_black())
    style.set_pad_all(10)

    # Init the pressed style
    style_pr = lv.style_t()
    style_pr.init()

    # Add a large outline when pressed
    style_pr.set_outline_width(30)
    style_pr.set_outline_opa(lv.OPA.TRANSP)

    style_pr.set_translate_y(5)
    style_pr.set_shadow_ofs_y(3)
    style_pr.set_bg_color(lv.palette_darken(lv.PALETTE.BLUE, 2))
    style_pr.set_bg_grad_color(lv.palette_darken(lv.PALETTE.BLUE, 4))

    # Add a transition to the outline
    trans = lv.style_transition_dsc_t()
    props = [lv.STYLE.OUTLINE_WIDTH, lv.STYLE.OUTLINE_OPA, 0]
    trans.init(props, lv.anim_t.path_linear, 300, 0, None)

    style_pr.set_transition(trans)

    btn1 = lv.btn(lv.scr_act())
    btn1.remove_style_all()  # Remove the style coming from the theme
    btn1.add_style(style, 0)
    btn1.add_style(style_pr, lv.STATE.PRESSED)
    btn1.set_size(lv.SIZE.CONTENT, lv.SIZE.CONTENT)
    btn1.center()

    label = lv.label(btn1)
    label.set_text("Button")
    label.center()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
#finally:
    bgl(0)
    gc.collect()
    disp.deinit()
    touch.deinit()