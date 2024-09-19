# CYD2-MPY-LVGL

## Introduction

<img align="right"  src="img/CYD2_Back.jpg" width="300" height="auto" />

The [Cheap Yellow Display](https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display/tree/main) (CYD) is a low-cost device comprised of a ESP32-WROOM equipped with a
ILI9431 2.4' Display and a xpt2046 touch pad and some more peripherals. It can be found on AliExpress for 7$ - 15$ depending on the seller and available promotions.

[Two similar versions of CYD are available](https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display/blob/main/cyd.md). The first version has one USB port (i call this "CYD") and the second version
features two USB ports (i call this "CYD-2"). Although the remaining components are identical, there is a difference in the display drivers color management.

## Color Mode for CYD2
Those changes are neccessary for correct color-display on CYD2.
During display initialization in pure Micropython, bgr-mode needs to be disabled:

```python
Display(self.spi_display, dc=Pin(2), cs=Pin(15), rst=Pin(15), width = 320, height = 240, bgr = False)
```

When using LVGL on CYD2, the colormode needs to be set during initialization of the display driver.

```python
disp = ili9XXX.ili9341(clk=14, cs=15, dc=2, rst=12, power=23, miso=12, mosi=13, width = 320, height = 240,
rot = 0xC0, colormode=ili9XXX.COLOR_MODE_RGB, double_buffer = False, factor = 16)
```

## CYD2 and MicroPython

<img align="right"  src="img/CYD2_MPY.jpg" width="300" height="auto" />

The standard release of ESP32 MPY-Firmware can be installed on the CYD-2 as described [here](https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display/blob/main/Examples/Micropython/Micropython.md).
The ILI9431 and xpt2046 drivers are also linked on the site.

A working demo and the drivers can be found in the `/mpy` folder.
The folder also contains a PinMap. The demo and the PinMap is based on [this demo](https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display/blob/main/Examples/Micropython/demo.py).


## LVGL + MPY

<img align="right"  src="img/CYD2_LVGL.jpg" width="300" height="auto" />

After getting CYD2 to work with standard MPY firmware and the corresponding drivers,
I figured that the display driver is slow and has very limited capabilities for use.

Therefore, I tried to get [MicroPython LVGL](https://github.com/lvgl/lv_micropython) to work on this display.
Fortunately, a [prebuild version of the lvgl firmware](https://stefan.box2code.de/2023/11/18/esp32-grafik-mit-lvgl-und-micropython/) is provided for download by Stefan Scholz.
A modified xpt2046 driver is required and it is available for download on the same site.

Again, it cost me a lot of time to get a working demo.
It can found in the `/lvgl-mpy` folder.

The prebuild version of the MPY-LVGL firmware and the modified xpt2046 driver need to be downloaded
from the aforementioned site. I didn't upload them since I don't hold the copyright.
