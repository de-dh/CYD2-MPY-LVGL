'''Custom Driver xpt2046_cyd and MPY-LVGL build from
https://stefan.box2code.de/2023/11/18/esp32-grafik-mit-lvgl-und-micropython/

Running on cheap yellow display with TWO USB Ports
--> https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display/blob/main/cyd.md
'''
import lvgl as lv
import time
import display_driver

num = 0 # Used for callback

def enable(el):
    if el.has_state(lv.STATE.DISABLED):
        el.clear_state(lv.STATE.DISABLED)

def disable(el):
    if not el.has_state(lv.STATE.DISABLED):
        el.add_state(lv.STATE.DISABLED)

def largeFont(el):
    el.set_style_text_font(lv.font_montserrat_16, 0)

def callback(s):
    global num
    if s == 'Prev':
        num -= 1
    elif s == 'Next':
        num += 1
    valueLbl.set_text('Count: ' + str(num))





''' Get reference to active screen for drawing '''
scr = lv.scr_act()
scr.set_style_bg_color(lv.color_white(), lv.PART.MAIN)


''' Create label and center it on screen '''
valueLbl = lv.label(scr)
largeFont(valueLbl)
valueLbl.set_text('Count: ' + str(num))
valueLbl.center()


''' Create Button with icon and text and add callback '''
prevBtn = lv.btn(scr)
prevBtn.set_size(80, 40)
prevBtn.align_to(valueLbl, lv.ALIGN.OUT_LEFT_MID, -20, 0)
prevBtn.add_event_cb(lambda e: callback('Prev'), lv.EVENT.CLICKED, None)
''' Assign label to button '''
prevBtnLbl = lv.label(prevBtn)
prevBtnLbl.set_text(lv.SYMBOL.PREV + ' Prev')
prevBtnLbl.center()


nextBtn = lv.btn(scr)
nextBtn.set_size(80, 40)
nextBtn.align_to(valueLbl, lv.ALIGN.OUT_RIGHT_MID, 20, 0)
nextBtn.add_event_cb(lambda e: callback('Next'), lv.EVENT.CLICKED, None)

nextBtnLbl = lv.label(nextBtn)
nextBtnLbl.set_text('Next ' + lv.SYMBOL.NEXT)
nextBtnLbl.center()


while True:
    time.sleep(1)