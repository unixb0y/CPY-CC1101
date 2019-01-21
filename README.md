# README #

CPY-CC1101 is a simple Python library for the [CC1101](http://www.ti.com/product/CC1101) RF Transceiver written for [CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython/what-is-circuitpython) so that it runs on Adafruits new CircuitPython-supporting devices like the Feather M0 and M4.
I use it on an Adafruit Feather M4 Express with a [CC1101 Arduino module](https://www.amazon.com/Solu-Wireless-Transceiver-Antenna-Arduino/dp/B00XDL9838/ref=pd_sbs_147_6?_encoding=UTF8&psc=1&refRID=51K5G4WS9ZPJVE7HC2MW) connected trough SPI.

Example code for a receiver:

```python
from cpc.cpc import *

myspi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.D9)
gdo0 = DigitalInOut(board.D10)

rx = CC1101(myspi, cs, gdo0, 50000, 434400000, "666A")
# SPI object, Chip Select Pin, baudrate, frequency in Hz, Syncword

rx.setupRX()
while True:
	rx.receiveData(0x19)
```

Example code for a transmitter:
```python
from cpc.cpc import *

myspi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.D9)
gdo0 = DigitalInOut(board.D10)

rx = CC1101(myspi, cs, gdo0, 50000, 434400000, "666A")
# SPI object, Chip Select Pin, baudrate, frequency in Hz, Syncword

rx.setupTX()
rx.sendData("0000111100001111", "666A")
```

* Transmitting data is done through the `sendData(bitstring, syncword)` function. It takes a string of payload data bits to transmit and a sync word of 16 bits that is prepended to the payload data. The file `code_tx.py` is some simple bare-bones code that just does TX and also works fine, but I would just use `cpc.py`.
* The receiver works easily as well, like shown above with `receiveData(length)`. You should simply pass the length of the data that should be received as a number.

* **TO DO:** Actually use the baudrate parameter of the constructor, right now it doesn't do anything and the rate is hardcoded in `MDMCFG4` and `MDMCFG3`.

You can have multiple antennas by just using a single SPI object and passing it to the various CC1101 objects.

```python
myspi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs_a = DigitalInOut(board.D9)
cs_b = DigitalInOut(board.D6)
rx = CC1101(myspi, cs_a, gdo0_a, 50000, 434400000, "666A")
tx = CC1101(myspi, cs_b, gdo0_b, 50000, 434400000, "666A")

# then do stuff with either one of the antennas, but only AFTER creating both CC1101 objects.

```

For more details or questions, feel free to contact me, open an issue and first of all, have a look at the [official documentation / datasheet](http://www.ti.com/lit/ds/symlink/cc1101.pdf)!  

Resources for RollJam, which can be implemented with this library:  
https://www.rtl-sdr.com/tag/rolljam/  
http://spencerwhyte.blogspot.com/2014/03/delay-attack-jam-intercept-and-replay.html?m=1  
https://samy.pl/defcon2015/