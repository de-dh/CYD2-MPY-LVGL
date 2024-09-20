from machine import SoftSPI, Pin
import lvgl as lv
import time
import ili9XXX
from xpt2046_cyd import xpt2046
        
try:
    lv.init()
    
    spiTouch = SoftSPI(baudrate = 2500000, sck = Pin(25),
                        mosi = Pin(32), miso = Pin(39))
    
    
    ''' Set Display Orientation:
            DISP_PORTRAIT = True --> Portrait Mode
            DISP_PORTRAIT = False --> Landscape Mode
            
            The following parameters need to be adjusted according
            to the selected display orientation:
            disp: rot, width, height
            touch: width, height, transpose, portrait, (calibration)
    '''
    DISP_PORTRAIT = True
    #DISP_PORTRAIT = False
    
    if DISP_PORTRAIT:
        ''' Portrait Mode '''
        disp = ili9XXX.ili9341(clk=14, cs=15,
                               dc=2, rst=12, power=23, miso=12,
                               mosi=13, width = 240, height = 320,
                               rot = 0xA0, colormode=ili9XXX.COLOR_MODE_RGB,
                                double_buffer = False, factor = 16)

        touch = xpt2046(spi = spiTouch, cs = Pin(33), cal_x0 = 3722,
                    cal_y0 = 3738, cal_x1 = 250, cal_y1 = 245, portrait = True, transpose = False)
    else:
        ''' Landscape Mode '''
        disp = ili9XXX.ili9341(clk=14, cs=15,
                               dc=2, rst=12, power=23, miso=12,
                               mosi=13, width = 320, height = 240,
                               rot = 0xC0, colormode=ili9XXX.COLOR_MODE_RGB,
                               double_buffer = False, factor = 16)
        
        
        touch = xpt2046(spi = spiTouch, cs = Pin(33), cal_x0 = 3700,
                    cal_y0 = 3820, cal_x1 = 180, cal_y1 = 250, transpose=False)
    
    backlight = Pin(21, Pin.OUT)
    backlight(1)

    group = lv.group_create()
    group.set_default()
    
    ''' Create Screen Object '''
    scr = lv.obj()
    scr.set_style_bg_color(lv.color_white(), lv.PART.MAIN)
    
    
    ''' Add Screen Content '''
    statusLbl = lv.label(scr)
    statusLbl.set_text('Portrait Mode' if DISP_PORTRAIT else 'Landscape Mode')
    statusLbl.center()
    
    testBtn = lv.btn(scr)
    testBtn.set_size(110, 40)
    testBtn.align_to(statusLbl, lv.ALIGN.OUT_BOTTOM_MID, 0, 5)
    
    testBtnLbl = lv.label(testBtn)
    testBtnLbl.set_text(lv.SYMBOL.RIGHT + ' Click Me! ' + lv.SYMBOL.LEFT)
    testBtnLbl.center()
    
    testBtn.add_event_cb(lambda e: statusLbl.set_text('Mid Button clicked!'), lv.EVENT.CLICKED, None)
    
    testBtn2 = lv.btn(scr)
    testBtn2.align(lv.ALIGN.TOP_LEFT, 5, 5)
    
    testBtnLbl2 = lv.label(testBtn2)
    testBtnLbl2.set_text('TOP LEFT')
    testBtnLbl2.center()
    
    testBtn2.add_event_cb(lambda e: statusLbl.set_text('Top Button clicked!'), lv.EVENT.CLICKED, None)
    
    
    testBtn3 = lv.btn(scr)
    testBtn3.align(lv.ALIGN.BOTTOM_RIGHT, -5, -5)
    
    testBtnLbl3 = lv.label(testBtn3)
    testBtnLbl3.set_text('BOTTOM RIGHT')
    testBtnLbl3.center()
    
    testBtn3.add_event_cb(lambda e: statusLbl.set_text('Bottom Button clicked!'), lv.EVENT.CLICKED, None)
    
    ''' Load Screen '''
    lv.scr_load(scr)
    
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print('Programm terminated by user.')
#finally: