# README #

CPY-CC1101 is a simple Python wrapper for the [CC1101](http://www.ti.com/product/CC1101) RF Transceiver written for [CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython/what-is-circuitpython) so that it runs on Adafruits new CircuitPython-supporting devices like the Feather M0 and M4.
I use it on an Adafruit Feather M4 Express with a [CC1101 Arduino module](https://www.amazon.com/Solu-Wireless-Transceiver-Antenna-Arduino/dp/B00XDL9838/ref=pd_sbs_147_6?_encoding=UTF8&psc=1&refRID=51K5G4WS9ZPJVE7HC2MW) connected trough SPI.

Example code for a receiver:

```python
from cpc.cpc import *

myspi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.D9)
gdo0 = DigitalInOut(board.D10)

rx = CC1101(myspi, cs, gdo0, 50000, 434400000, "666A")
rx.setupRX()
while True:
	rx.receiveData()
```

This is a work in progress, so the current status is:

* Transmitting data is proven to work fine with the code in `code_tx.py` but I didn't try it with the cpc library yet.
* The receiver works either using `code_rx.py` (and adapting it to what is needed) or simply through the `cpc.py` library like shown above.

You can have multiple antennas by just using a single SPI object and passing it to the various CC1101 objects.

```python
myspi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs_a = DigitalInOut(board.D9)
cs_b = DigitalInOut(board.D6)
rx = CC1101(myspi, cs_a, gdo0_a, 50000, 434400000, "666A")
tx = CC1101(myspi, cs_b, gdo0_b, 50000, 434400000, "666A")

# then do stuff with either one of the antennas, but only AFTER creating both CC1101 objects.

```