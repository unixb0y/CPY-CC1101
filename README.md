# README #

PYCC1101 a simple Python wrapper for the [CC1101](http://www.ti.com/product/CC1101) RF Transceiver from [Nahuel Sanchez](https://github.com/nahueldsanchez) which I have ported to CircuitPython so that it runs on Adafruits new CP-supporting devices. I've been using it with a [CC1101 Arduino module](https://www.amazon.com/Solu-Wireless-Transceiver-Antenna-Arduino/dp/B00XDL9838/ref=pd_sbs_147_6?_encoding=UTF8&psc=1&refRID=51K5G4WS9ZPJVE7HC2MW) connected trough SPI to an Adafruit Feather M4 Express.
The code is based on [PanStamp Arduino library ](https://github.com/panStamp/arduino_avr).

Example code for a transmitter:

```python
from cpycc1101.cpycc1101 import TICC1101
from digitalio import DigitalInOut
import board
import busio

mySPI = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs_pin = DigitalInOut(board.D9)
ticc1101 = TICC1101(cs=cs_pin, spi=mySPI)
ticc1101.reset()
ticc1101.selfTest()
ticc1101.setDefaultValues()
ticc1101.setFilteringAddress(0x0A)
ticc1101.setPacketMode("PKT_LEN_FIXED")
ticc1101.configureAddressFiltering("DISABLED")
ticc1101.setSyncMode(0)

ticc1101.sendData(prepare("1111111111111111000010000111000000"))

def prepare(string):
    one = 0b00000011
    zero = 0b00111111
    return list(map(lambda x: zero if x=='0' else one, list(string)))
```

This is a work in progress, so the current status is:

* Transmitting data works perfectly fine using TICC1101.sendData() and passing a list of bytes to send.
* The receiver part seems to work in terms of 'doing something' but I'm not sure whether it's fully configured properly yet and will try to get it up and running asap as well.

You can have multiple antennas because of some of my changes to the original code. For example, the SPI object has to be created in your `code.py` class and passed to the TICC1101 constructor, like following:

```python
mySPI = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs_a = DigitalInOut(board.D9)
cs_b = DigitalInOut(board.D6)
ticc1101_a = TICC1101(cs=cs_a, spi=mySPI)
ticc1101_b = TICC1101(cs=cs_b, spi=mySPI)

# then do stuff with either one of the antennas, but only AFTER creating both TICC1101 objects.

```