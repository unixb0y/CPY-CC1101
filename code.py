from cpc.cpc import *

myspi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.D9)
gdo0 = DigitalInOut(board.D10)

rx = CC1101(myspi, cs, gdo0, 50000, 434400000, "666A")
rx.setupRX()
while True:
	rx.receiveData(0x19)