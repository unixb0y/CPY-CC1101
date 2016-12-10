from pycc1101.pycc1101 import TICC1101
from struct import pack
import binascii
import time

ticc1101 = TICC1101()
ticc1101.reset()
ticc1101.selfTest()
ticc1101.setDefaultValues()
ticc1101.setFilteringAddress(0x0A)
#ticc1101.setPacketMode("PKT_LEN_VARIABLE")
ticc1101.setPacketMode("PKT_LEN_FIXED")
ticc1101.configureAddressFiltering("ENABLED_NO_BROADCAST")

count = 0

while True:
    data = pack('<I', count)
    toSend = [int(binascii.hexlify(x),16) for x in data]
    ticc1101.sendData(toSend)
    count += 1
    time.sleep(1)