from micropython import const

LDR = const(34)

RGB_LED_R = const(4)
RGB_LED_G = const(16)
RGB_LED_B = const(17)

TOUCH_CS = const(33)
TOUCH_INT = const(36)

TOUCH_SPI_SLOT = const(2)
TOUCH_SPI_SCK = const(25)
TOUCH_SPI_MOSI = const(32)
TOUCH_SPI_MISO = const(39)

TFT_WIDTH = const(320)
TFT_HEIGHT = const(240)

TFT_BLK = const(21)
TFT_DC = const(2)
TFT_CS = const(15)
TFT_RST = const(15)

TFT_SPI_SLOT = const(1)
TFT_SPI_SCK = const(14)
TFT_SPI_MOSI = const(13)

SD_SLOT = const(2)
SD_CS = const(5)
SD_SCK = const(18)
SD_MISO = const(19)
SD_MOSI = const(23)