from digitalio import DigitalInOut
import board
import busio
import time
import math
from adafruit_bus_device.spi_device import SPIDevice

WRITE_SINGLE_BYTE = 0x00
WRITE_BURST = 0x40
READ_SINGLE_BYTE = 0x80
READ_BURST = 0xC0

IOCFG2 = 0x00  # GDO2 Output Pin Configuration
IOCFG1 = 0x01  # GDO1 Output Pin Configuration
IOCFG0 = 0x02  # self.GDO0 Output Pin Configuration
FIFOTHR = 0x03  # RX FIFO and TX FIFO Thresholds
SYNC1 = 0x04  # Sync Word, High Byte
SYNC0 = 0x05  # Sync Word, Low Byte
PKTLEN = 0x06  # Packet Length
PKTCTRL1 = 0x07  # Packet Automation Control
PKTCTRL0 = 0x08  # Packet Automation Control
ADDR = 0x09  # Device Address
CHANNR = 0x0A  # Channel Number
FSCTRL1 = 0x0B  # Frequency Synthesizer Control
FSCTRL0 = 0x0C  # Frequency Synthesizer Control
FREQ2 = 0x0D  # Frequency Control Word, High Byte
FREQ1 = 0x0E  # Frequency Control Word, Middle Byte
FREQ0 = 0x0F  # Frequency Control Word, Low Byte
MDMCFG4 = 0x10  # Modem Configuration
MDMCFG3 = 0x11  # Modem Configuration
MDMCFG2 = 0x12  # Modem Configuration
MDMCFG1 = 0x13  # Modem Configuration
MDMCFG0 = 0x14  # Modem Configuration
DEVIATN = 0x15  # Modem Deviation Setting
MCSM2 = 0x16  # Main Radio Control State Machine Configuration
MCSM1 = 0x17  # Main Radio Control State Machine Configuration
MCSM0 = 0x18  # Main Radio Control State Machine Configuration
FOCCFG = 0x19  # Frequency Offset Compensation Configuration
BSCFG = 0x1A  # Bit Synchronization Configuration
AGCCTRL2 = 0x1B  # AGC Control
AGCCTRL1 = 0x1C  # AGC Control
AGCCTRL0 = 0x1D  # AGC Control
WOREVT1 = 0x1E  # High Byte Event0 Timeout
WOREVT0 = 0x1F  # Low Byte Event0 Timeout
WORCTRL = 0x20  # Wake On Radio Control
FREND1 = 0x21  # Front End RX Configuration
FREND0 = 0x22  # Front End TX Configuration
FSCAL3 = 0x23  # Frequency Synthesizer Calibration
FSCAL2 = 0x24  # Frequency Synthesizer Calibration
FSCAL1 = 0x25  # Frequency Synthesizer Calibration
FSCAL0 = 0x26  # Frequency Synthesizer Calibration
RCCTRL1 = 0x27  # RC Oscillator Configuration
RCCTRL0 = 0x28  # RC Oscillator Configuration

# Configuration Register Details - Registers that Loose Programming in SLEEP State

FSTEST = 0x29  # Frequency Synthesizer Calibration Control
PTEST = 0x2A  # Production Test
AGCTEST = 0x2B  # AGC Test
TEST2 = 0x2C  # Various Test Settings
TEST1 = 0x2D  # Various Test Settings
TEST0 = 0x2E  # Various Test Settings

# Command Strobe Registers

SRES = 0x30  # Reset chip
SFSTXON = 0x31  # Enable and calibrate frequency synthesizer (if MCSM0.FS_AUTOCAL=1).
# If in RX (with CCA): Go to a wait state where only the synthesizer
# is running (for quick RX / TX turnaround).

SXOFF = 0x32  # Turn off crystal oscillator.
SCAL = 0x33  # Calibrate frequency synthesizer and turn it off.
# SCAL can be strobed from IDLE mode without setting manual calibration mode.

SRX = 0x34  # Enable RX. Perform calibration first if coming from IDLE and MCSM0.FS_AUTOCAL=1.
STX = 0x35  # In IDLE state: Enable TX. Perform calibration first
# if MCSM0.FS_AUTOCAL=1.
# If in RX state and CCA is enabled: Only go to TX if channel is clear.

SIDLE = 0x36  # Exit RX / TX, turn off frequency synthesizer and exit Wake-On-Radio mode if applicable.
SWOR = 0x38  # Start automatic RX polling sequence (Wake-on-Radio)
# as described in Section 19.5 if WORCTRL.RC_PD=0.

SPWD = 0x39  # Enter power down mode when CSn goes high.
SFRX = 0x3A  # Flush the RX FIFO buffer. Only issue SFRX in IDLE or RXFIFO_OVERFLOW states.
SFTX = 0x3B  # Flush the TX FIFO buffer. Only issue SFTX in IDLE or TXFIFO_UNDERFLOW states.
SWORRST = 0x3C  # Reset real time clock to Event1 value.
SNOP = 0x3D  # No operation. May be used to get access to the chip status byte.

PATABLE = 0x3E  # PATABLE
TXFIFO = 0x3F  # TXFIFO
RXFIFO = 0x3F  # RXFIFO

# Status Register Details

PARTNUM = 0xF0  # Chip ID
VERSION = 0xF1  # Chip ID
FREQEST = 0xF2  # Frequency Offset Estimate from Demodulator
LQI = 0xF3  # Demodulator Estimate for Link Quality
RSSI = 0xF4  # Received Signal Strength Indication
MARCSTATE = 0xF5  # Main Radio Control State Machine State
WORTIME1 = 0xF6  # High Byte of WOR Time
WORTIME0 = 0xF7  # Low Byte of WOR Time
PKTSTATUS = 0xF8  # Current GDOx Status and Packet Status
VCO_VC_DAC = 0xF9  # Current Setting from PLL Calibration Module
TXBYTES = 0xFA  # Underflow and Number of Bytes
RXBYTES = 0xFB  # Overflow and Number of Bytes
RCCTRL1_STATUS = 0xFC  # Last RC Oscillator Calibration Result
RCCTRL0_STATUS = 0xFD  # Last RC Oscillator Calibration Result

PA_TABLE = [0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

class CC1101:
    def __init__(self, spi, cs, gdo0, baudrate, frequency, syncword, offset=0): #optional frequency offset in Hz
        self.gdo0 = gdo0
        self.device = SPIDevice(spi, cs, baudrate=baudrate, polarity=0, phase=0)
        self.strobe(SRES) # reset

        self.setFrequency(frequency, offset)

        assert len(syncword) == 4
        self.writeSingleByte(SYNC1, int(syncword[:2], 16))
        self.writeSingleByte(SYNC0, int(syncword[2:], 16))

        self.writeBurst(PATABLE, PA_TABLE)      
        self.strobe(SFTX) # flush TX FIFO
        self.strobe(SFRX) # flush RX FIFO

    def setFrequency(self, frequency, offset):
        frequency_hex = hex(int(frequency * (pow(2,16) / 26000000)+offset))

        byte2 = (int(frequency_hex, 16) >> 16) & 0xff;
        byte1 = (int(frequency_hex) >>  8) & 0xff;
        byte0 = int(frequency_hex) & 0xff;

        self.writeSingleByte(FREQ2, byte2)
        self.writeSingleByte(FREQ1, byte1)
        self.writeSingleByte(FREQ0, byte0)  
       
    def getSampleRate(self, freq_xosc = 26000000):
        drate_mantissa = self.readSingleByte(MDMCFG3)
        drate_exponent = self.readSingleByte(MDMCFG4) & 0xF
        sample_rate = (256 + drate_mantissa) * \
            pow(2, drate_exponent - 28) * freq_xosc
        return sample_rate
    
    def setSampleRate_4000(self):
        self.writeSingleByte(MDMCFG3, 0x43)
        
   def setSampleRate(self):
        pass

    def setupRX(self):
        self.writeSingleByte(IOCFG2, 0x29)    
        self.writeSingleByte(IOCFG1, 0x2E)    
        self.writeSingleByte(IOCFG0, 0x06)    
        self.writeSingleByte(FIFOTHR, 0x47)   
        self.writeSingleByte(PKTCTRL1, 0x00)  
        self.writeSingleByte(PKTCTRL0, 0x00)  
        self.writeSingleByte(ADDR, 0x00)
        self.writeSingleByte(CHANNR, 0x00)
        self.writeSingleByte(FSCTRL1, 0x08)   
        self.writeSingleByte(FSCTRL0, 0x00)           
        self.writeSingleByte(MDMCFG4, 0xF7)    
        self.writeSingleByte(MDMCFG3, 0x10)    
        self.writeSingleByte(MDMCFG2, 0x32)   
        self.writeSingleByte(MDMCFG1, 0x22)   
        self.writeSingleByte(MDMCFG0, 0xF8)
        self.writeSingleByte(DEVIATN, 0x00)   
        self.writeSingleByte(MCSM2, 0x07)
        self.writeSingleByte(MCSM1, 0x30)     
        self.writeSingleByte(MCSM0, 0x18)
        self.writeSingleByte(FOCCFG, 0x16)
        self.writeSingleByte(BSCFG, 0x6C)
        self.writeSingleByte(AGCCTRL2, 0x06)  
        self.writeSingleByte(AGCCTRL1, 0x00)  
        self.writeSingleByte(AGCCTRL0, 0x95)
        self.writeSingleByte(WOREVT1, 0x87)
        self.writeSingleByte(WOREVT0, 0x6B)
        self.writeSingleByte(WORCTRL, 0xFB)
        self.writeSingleByte(FREND1, 0xB6)    
        self.writeSingleByte(FREND0, 0x11)    
        self.writeSingleByte(FSCAL3, 0xE9)
        self.writeSingleByte(FSCAL2, 0x2A)
        self.writeSingleByte(FSCAL1, 0x00)
        self.writeSingleByte(FSCAL0, 0x1F)
        self.writeSingleByte(RCCTRL1, 0x41)
        self.writeSingleByte(RCCTRL0, 0x00)
        self.writeSingleByte(FSTEST, 0x59)
        self.writeSingleByte(PTEST, 0x7F)   
        self.writeSingleByte(AGCTEST, 0x3F)
        self.writeSingleByte(TEST2, 0x81)     
        self.writeSingleByte(TEST1, 0x35)     
        self.writeSingleByte(TEST0, 0x09)

    def setupTX(self):
        self.writeSingleByte(IOCFG2, 0x29)    
        self.writeSingleByte(IOCFG1, 0x2E)    
        self.writeSingleByte(IOCFG0, 0x06)    
        self.writeSingleByte(FIFOTHR, 0x47)   
        self.writeSingleByte(PKTCTRL1, 0x00)  
        self.writeSingleByte(PKTCTRL0, 0x00)  
        self.writeSingleByte(ADDR, 0x00)
        self.writeSingleByte(CHANNR, 0x00)
        self.writeSingleByte(FSCTRL1, 0x06)   
        self.writeSingleByte(FSCTRL0, 0x00)   
        self.writeSingleByte(MDMCFG4, 0xE7)    
        self.writeSingleByte(MDMCFG3, 0x10)    
        self.writeSingleByte(MDMCFG2, 0x30)    #. 32 would be 16/16 sync word bits .#
        self.writeSingleByte(MDMCFG1, 0x22)   
        self.writeSingleByte(MDMCFG0, 0xF8)
        self.writeSingleByte(DEVIATN, 0x15)   
        self.writeSingleByte(MCSM2, 0x07)
        self.writeSingleByte(MCSM1, 0x20)     
        self.writeSingleByte(MCSM0, 0x18)
        self.writeSingleByte(FOCCFG, 0x14)
        self.writeSingleByte(BSCFG, 0x6C)
        self.writeSingleByte(AGCCTRL2, 0x03)  
        self.writeSingleByte(AGCCTRL1, 0x00)  
        self.writeSingleByte(AGCCTRL0, 0x92)
        self.writeSingleByte(WOREVT1, 0x87)
        self.writeSingleByte(WOREVT0, 0x6B)
        self.writeSingleByte(WORCTRL, 0xFB)
        self.writeSingleByte(FREND1, 0x56)    
        self.writeSingleByte(FREND0, 0x11)    
        self.writeSingleByte(FSCAL3, 0xE9)
        self.writeSingleByte(FSCAL2, 0x2A)
        self.writeSingleByte(FSCAL1, 0x00)
        self.writeSingleByte(FSCAL0, 0x1F)
        self.writeSingleByte(RCCTRL1, 0x41)
        self.writeSingleByte(RCCTRL0, 0x00)
        self.writeSingleByte(FSTEST, 0x59)
        self.writeSingleByte(PTEST, 0x7F)   
        self.writeSingleByte(AGCTEST, 0x3F)
        self.writeSingleByte(TEST2, 0x81)     
        self.writeSingleByte(TEST1, 0x35)     
        self.writeSingleByte(TEST0, 0x0B)

    def writeSingleByte(self, address, byte_data):
        databuffer = bytearray([WRITE_SINGLE_BYTE | address, byte_data])
        with self.device as d:
            d.write(databuffer)

    def readSingleByte(self, address):
        databuffer = bytearray([READ_SINGLE_BYTE | address, 0x00])
        
        with self.device as d:
            d.write(databuffer, end=1)
            d.readinto(databuffer, end=2)
        return databuffer[0]

    def readBurst(self, start_address, length):        
        databuffer = []
        ret = bytearray(length+1)

        for x in range(length + 1):
            addr = (start_address + (x*8)) | READ_BURST
            databuffer.append(addr)

        with self.device as d:
            d.write_readinto(bytearray(databuffer), ret)
        return ret

    def writeBurst(self, address, data):
        temp = list(data)
        temp.insert(0, (WRITE_BURST | address))
        with self.device as d:
            d.write(bytearray(temp))

    def strobe(self, address):
        databuffer = bytearray([address, 0x00])
        with self.device as d:
            d.write(databuffer, end=1)
            d.readinto(databuffer, end=2)
        return databuffer

    def setupCheck(self):
        self.strobe(SFRX)
        self.strobe(SRX)
        print("ready to detect data")

    def receiveData(self, length):
        self.writeSingleByte(PKTLEN, length)
        self.strobe(SRX)
        print("waiting for data")

        while self.gdo0.value == False:
            pass 
        #detected rising edge

        while self.gdo0.value == True:
            pass
        #detected falling edge

        data_len = length#+2 # add 2 status bytes
        data = self.readBurst(RXFIFO, data_len)
        dataStr = ''.join(list(map(lambda x: "{0:0>8}".format(x[2:]), list(map(bin, data)))))
        newStr = dataStr[8:]
        print("Data: ", newStr)
        self.strobe(SIDLE)
        while (self.readSingleByte(MARCSTATE) != 0x01):
            pass
        self.strobe(SFRX)
        return newStr

    def sendData(self, bitstring, syncword):
        print("TXBYTES before sendData:", self.readSingleByte(TXBYTES))
        paddingLen = math.floor((512-16-len(bitstring))/8) # 16 Bits sync word
        bitstring = paddingLen*"10101010"+"{0:0>16}".format(bin(int(syncword, 16))[2:])+bitstring

        #print("the bitstring is", len(bitstring), "bits long")

        data = []
        for i in range(0,len(bitstring)/8):
            data.append(int(bitstring[i*8:i*8+8], 2))

        self.writeSingleByte(PKTLEN, len(data))
        
        self.strobe(SIDLE)
        while (self.readSingleByte(MARCSTATE) & 0x1F != 0x01): # wait for CC to enter idle state
            pass
        self.strobe(SFTX) # flush TX FIFO
        time.sleep(0.05)

        #print(''.join(list(map(lambda x: "{0:0>8}".format(str(bin(x)[2:])), data))))
        #print("Sending packet of", len(data), "bytes")
        #print("Data in TXFIFO:\n", self.readBurst(TXFIFO, 64), "\nTXBYTES:", self.readSingleByte(TXBYTES))
        self.writeBurst(TXFIFO, data)
        #print("Data in TXFIFO:\n", self.readBurst(TXFIFO, 64), "\nTXBYTES:", self.readSingleByte(TXBYTES))
        self.strobe(STX)

        remaining_bytes = self.readSingleByte(TXBYTES) & 0x7F
        while remaining_bytes != 0:
            time.sleep(0.1)
            print("Waiting until all bytes are transmited, remaining bytes: %d" % remaining_bytes)
            remaining_bytes = self.readSingleByte(TXBYTES) & 0x7F

        self.strobe(SFTX)
        self.strobe(SFRX)
        time.sleep(0.05)

        if (self.readSingleByte(TXBYTES) & 0x7F) == 0:
            print("Packet sent!\n\n")
            return True

        else:
            print(self.readSingleByte(TXBYTES) & 0x7F)
            return False
