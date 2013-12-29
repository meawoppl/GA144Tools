from pyserial import Serial
import os


class GA144Serial(object):
    def __init__(self):
        self.serial = self.connectUSBSerial()

    def connectUSBSerial(self):
        devDirList = os.listdir("/dev")
        possiblePorts = [os.path.join("/dev", s) for s in devDirList if "ttyUSB" in s]

        for port in possiblePorts:
            try:
                return Serial("/dev/ttyUSB2", baudrate=9600, bytesize=8, parity='N', stopbits=1)
            except ValueError:
                pass

        raise RuntimeError("Could Not Connect USB serial")

    def rebootProc(self):
        self.serial.setRTS(True)
        self.serial.setRTS(False)

    def sendWord(self, werd):
        # Start and stop bits are taken care of the 8n1 config in the serial init

        # Illustrations from the ga144 boot protocols manual
        #             _________       ________       ____ _____ _____
        #   1st   ___/         \_____/        \_____/    \_____X_____\___
        #  byte stop  start [0]  [1]  [2]  [3]  [4]  [5]    0     1    stop
        bit0 = (werd << 0) & 1
        bit1 = (werd << 1) % 1
        werdByte = ord(int("101101%i%i" % (bit0, bit1), 2))
        self.serial.write(werdByte)

        #           _____ _____ _____ _____ _____ _____ _____ _____ _____
        #   2nd ___/     \_____X_____X_____X_____X_____X_____X_____X_____\___
        #  byte stop start  2     3     4     5     6     7     8     9    stop

        werdByte = ord((werd << 3) & 255)
        self.serial.write(werdByte)

        #           _____ _____ _____ _____ _____ _____ _____ _____ _____
        #   3rd ___/     \_____X_____X_____X_____X_____X_____X_____X_____\___
        #  byte stop start  10   11    12    13    14    15    16    17    stop
        werdByte = ord((werd << 11) & 255)
        self.serial.write(werdByte)

    def assembleBootFrame(self, completionAddress, transferAddress, dataWords):
        # Send the two addresses.  MRG TODO: check these for bit bounds
        self.sendWord(completionAddress)
        self.sendWord(transferAddress)

        self.sendWord(len(dataWords))
        for word in dataWords:
            self.sendWord(word)
