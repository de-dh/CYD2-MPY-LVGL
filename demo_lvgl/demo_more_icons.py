''' /font folder must be uploaded to the esp32 via Thonny '''
import lvgl as lv
import time
import display_driver
import fs_driver



def convert_to_utf8_bytes(hex_str):
    code_point = int(hex_str, 16)
    unicode_str = chr(code_point)
    utf8_bytes = unicode_str.encode('utf-8')
    return utf8_bytes

try:
    
    style = lv.style_t()
    style.init()
    style.set_border_width(1)
    style.set_border_color(lv.palette_main(lv.PALETTE.ORANGE))
    style.set_pad_all(2)
    
    fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(fs_drv, 'S')
    font_custom = lv.font_load('S:' + 'fonts/font_awesome_18.bin')
    
    style.set_text_color(lv.color_black())        
    style.set_text_font(font_custom)
    
    
    spans = lv.spangroup(lv.scr_act())
    spans.set_width(320)
    spans.set_height(240)
    spans.center()
    spans.add_style(style, 0)
    
    spans.set_align(lv.TEXT_ALIGN.LEFT)
    spans.set_overflow(lv.SPAN_OVERFLOW.CLIP)
    spans.set_indent(20)
    spans.set_mode(lv.SPAN_MODE.BREAK)
    
    glyphs = ['shutdown', 'gear', 'menue', 'file', 'folder', 'gears', 'keyboard',
              'fileText','eyeOpen','eyeStrikeThrough','floppyDisk','calendarMonths','bell',
              'calendarEmpty','clock','world','letter','eyeStrikeThrough2','user',
              'image','message','camera','redo','pieChart','language','wifi','download',
              'upload','arrowLeftLong','confirm','close','trash','arrowLeft',
              'bar','arrowRight','menue2','chain','lock','key','lockOpen','deny',
              'lightbulb','birthdayCake']
    
    chars = ['f011','f013','f0c9','f15b','f07b','f085','f11c','f15c','f06e',
             'f070','f0c7','f073','f0f3','f133','f017','f0ac','f0e0','f070',
             'f007','f03e','f075','f030','f064','f200','f1ab','f1eb','f019',
             'f093','f178','f00c','f00d','f1f8','f178','f068','f177','f141',
             'f0c1','f023','f084','f09c','f05e','f0eb','f1fd']
    
    print(len(glyphs), len(chars))
    
    def getGlyph(name):
        global glyphs, chars
        
        for i, glyph in enumerate(glyphs):
            if name == glyph:
                return convert_to_utf8_bytes(chars[i])
        
        print('Glyph not found!')
        return convert_to_utf8_bytes('f05e')

         
    for char in chars:
         span = spans.new_span()
         span.set_text(convert_to_utf8_bytes(char))

    
    spans.refr_mode()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print('Exiting...')
#finally:
    bgl(0)
    disp.deinit()
    touch.deinit()
    spi2.deinit()
    