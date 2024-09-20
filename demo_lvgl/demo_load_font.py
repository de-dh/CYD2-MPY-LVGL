''' /font folder must be uploaded to the esp32 via Thonny '''
import lvgl as lv
import time
import display_driver
import fs_driver # important


# Register file system driver
fs_drive_letter = 'S' # Can be any letter
fs_font_driver = lv.fs_drv_t()
fs_driver.fs_register(fs_font_driver, fs_drive_letter)

# Multiple fonts may be loaded after fs driver is set up
# Text font
custom_font = lv.font_load(fs_drive_letter + ':' + 'fonts/montserrat-22.bin')

# LCD display font, contains only numbers 0 - 9 and :
# I use it to display time of day
LCD_font = lv.font_load(fs_drive_letter + ':' + 'fonts/LCD_Font_120.bin')
# Get reference to active screen for drawing
scr = lv.scr_act()
scr.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

# Create label with custom font
customFontLbl = lv.label(scr)
customFontLbl.set_style_text_font(custom_font, 0)
customFontLbl.set_text('Custom Text Font')
customFontLbl.align(lv.ALIGN.TOP_MID, 0, 30)

LCDFontLbl = lv.label(scr)
LCDFontLbl.set_style_text_font(LCD_font, 0)
LCDFontLbl.set_text('12:00')
LCDFontLbl.align(lv.ALIGN.TOP_MID, 0, 80)


while True:
    time.sleep(1)