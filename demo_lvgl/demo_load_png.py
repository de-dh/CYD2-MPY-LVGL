''' /img folder must be uploaded to the esp32 via Thonny '''
import lvgl as lv
import lv_utils
import time
import display_driver


# Create Image decoder
from imagetools import get_png_info, open_png
decoder = lv.img.decoder_create()
decoder.info_cb = get_png_info
decoder.open_cb = open_png


# Simple class for loading images
class ImgSimple(lv.img):
    def __init__(self, parent, src, w, h):
        super().__init__(parent)

        try:
            with open(src, 'rb') as f:
                png_data = f.read()
        except:
            print('Image not found.')
            #sys.exit()

        img_data = lv.img_dsc_t({
            'data_size': len(png_data),
            'data': png_data
        })

        self.set_src(img_data)
        self.set_size(w, h)
        

scr = lv.scr_act()
scr.set_style_bg_color(lv.color_white(), lv.PART.MAIN)

# Load image
hamsterImg = ImgSimple(scr, 'img/hamster.png', 50, 34)
hamsterImg.align(lv.ALIGN.CENTER, -70, 0)

# Create label next to image
hamsterLbl = lv.label(scr)
hamsterLbl.set_style_text_color(lv.color_black(), 0)
hamsterLbl.set_style_text_font(lv.font_montserrat_16, 0)
hamsterLbl.set_text("It's a Hamster!")
hamsterLbl.align_to(hamsterImg, lv.ALIGN.OUT_RIGHT_MID, 10, 0)


while True:
    time.sleep(1)