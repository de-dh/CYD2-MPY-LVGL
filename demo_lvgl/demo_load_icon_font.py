''' /font folder must be uploaded to the esp32 via Thonny '''
import lvgl as lv
import time
import display_driver
import fs_driver # important



def utf8Bytes(hexStr):
    ''' Used for custom icon fonts
        Returns six digit utf8 bytecode from four digit hex code
        as shown on font awesome website e.g.
        'F287' -> b'\0xEF\0x8A\0x87'
        
        Use: obj.set_text(utf8Bytes('F287'))'''
    
    hexCode = int(hexStr, 16)
    unicodeStr= chr(hexCode)
    utf8Bytecode = unicodeStr.encode('utf-8')
    return utf8Bytecode


# Register file system driver
fs_drive_letter = 'S' # Can be any letter
fs_font_driver = lv.fs_drv_t()
fs_driver.fs_register(fs_font_driver, fs_drive_letter)

# Multiple fonts may be loaded after fs driver is set up
# Icon font, containing five icons: e801 - e804
font_icons = lv.font_load('S:' + 'fonts/Symbols_40.bin')

# Get reference to active screen for drawing
scr = lv.scr_act()
scr.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

# Create label with custom font
iconLbl1 = lv.label(scr)
iconLbl1.set_style_text_font(font_icons, 0)
iconLbl1.set_text(utf8Bytes('e801'))
iconLbl1.align(lv.ALIGN.TOP_MID, 0, 30)

iconLbl2 = lv.label(scr)
iconLbl2.set_style_text_font(font_icons, 0)
iconLbl2.set_text(utf8Bytes('e802'))
iconLbl2.align(lv.ALIGN.TOP_MID, 0, 100)

while True:
    time.sleep(1)