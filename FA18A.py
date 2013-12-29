import numpy as np
from pylab import pcolor, figure, subplot, show
import random

import bitUtils as bu
import FA18A_constants, FA18A_util


def visualizeMemory(proc):
    memShape = (-1, 16)
    figure()
    subplot(1, 2, 1)
    pcolor(proc.mem.reshape(memShape))

    subplot(1, 2, 2)
    pcolor(proc.memType.reshape(memShape))

    show()


class ArrayBasedStack(object):
    def __init__(self, sArray):
        self.sArray = sArray

    def _rollArray(self, n):
        self.sArray[:] = np.roll(self.sArray, n)

    def push(self, value):
        self._rollArray(-1)
        self.sArray[0]

    def pop(self):
        self._rollArray(1)
        return self.sArray[-1]


class FA18A(object):
    def __init__(self, nodeName=None, rom=None):
        self.initInterpState()
        self.initMem()

        if rom is not None:
            self.installROM(rom)

        self.name = nodeName
        self.intefaces = {}

        self.reset()

    def initInterpState(self):
        self.slotNumber = 0
        self.opList = []

    def reset(self):
        # Set P to multiport execute
        self.jumpToWarm()

        # io is set to the state it would have after a program wrote x15555 into the register.
        self.mem[FA18A_constants.ioNameToAddress["io"]] = 0x15555

        # B is set to the address of io.
        self.B[:] = FA18A_constants.ioNameToAddress["io"]

        # The carry latch is not affected by reset and its state on power-up is unpredictable.
        self.carryBit = np.random.choice([0, 1])

    def initMem(self):
        # This call initialized the memory and allocated the various places
        # on the chip that are known to be occupied

        self.mem = np.zeros(512, dtype=np.uint32)

        self.memType = np.zeros_like(self.mem)
        self.memNameToID = {}

        # Ram + ROM
        self.ram = self.reserveMem(0, 128, "RAM")
        self.rom = self.reserveMem(128, 128, "ROM")

        # IO/Register Land
        for arrdName, addr in FA18A_constants.ioNameToAddress.items():
            self.commPorts = self.reserveMem(addr, 1, "IO")

        # NB: Offsets below are 100% made up.

        # Return Stack
        returnStackStart = 279
        self.returnStackArray = self.reserveMem(returnStackStart, 8, "RET")
        self.returnStack = ArrayBasedStack(self.returnStackArray)
        self.R = self.reserveMem(returnStackStart + 8, 1, "RET")

        # Data Stack
        dataStackStart = 310
        self.dataStackArray = self.reserveMem(dataStackStart, 10, "Data")
        self.dataStack = ArrayBasedStack(self.dataStackArray)

        # These registers done with the following ackward convention in insure array views
        self.T = self.mem[dataStackStart + 0:dataStackStart + 1]
        self.S = self.mem[dataStackStart + 1:dataStackStart + 2]

        # General Registers
        miscRegStart = 471
        self.A = self.reserveMem(miscRegStart, 1, "REG")
        self.B = self.reserveMem(miscRegStart + 2, 1, "REG")   # Write only?

        # Instruction Register
        self.I = self.reserveMem(miscRegStart + 4, 1, "REG")

        # Program Counter
        self.P = self.reserveMem(miscRegStart + 6, 1, "PC")

        # MRG TODO: this survives reset? (0, 1, unk?)
        self.carryBit = 0

    def reserveMem(self, segStart, segLength, segName):
        for offset in range(segStart, segStart + segLength):
            if self.memType[offset] != 0:
                s = "Reservation requested for %i, 0x%x." % (offset, offset)
                raise RuntimeError(s)

        self.memNameToID[segName] = self.memNameToID.get(segName, len(self.memNameToID) + 1)
        self.memType[segStart:segStart + segLength] = self.memNameToID[segName]

        return self.mem[segStart:segStart + segLength]

    def _getAddressValue(self, addr):
        # x000 x03F RAM, 64 words
        # x040 x07F RAM x000-x03F repeated
        if addr <= 127:
            return self.ram(addr % 64)

        elif (addr > 127) and (addr < 255):
            return self.rom(128 + (addr % 128))
        elif (addr >= 256):
            return self._getIO(addr)

    def _setAddressValue(self, addr, value):
        if addr <= 127:
            self.ram[addr % 64] = value

        elif (addr > 127) and (addr < 255):
            raise RuntimeError("Writing to ROM iist VERBOTEN!")
        elif addr >= 265:
            self._setIO(addr, value)
        else:
            raise RuntimeError("Trying to write to address %i 0x%05X = %i" % (addr, addr, value))

    def registerInterface(self, interfaceName, interface):
        self.interfaces[interfaceName] = interface

    def _derefAddrToInterfaces(self, addr):
        assert addr in FA18A_constants.ioAddressToName, "WTF Not an io address"

        addressName = FA18A_constants.ioAddressToName[addr]
        if addressName in ["data", "io"]:
            raise NotImplemented("TODO!")

        # Get a list of the interfaces we are trying currently
        return [self.interfaces[iName] for iName in addressName.replace("-", "")]

    def _isAddrGettable(self, addr):
        interfaces = self._derefAddrToInterfaces(addr)
        [i.startReading() for i in interfaces]
        return any([i.canReadImmidiately() for i in interfaces])

    def _isAddrSettable(self, addr):
        interfaces = self._derefAddrToInterfaces(addr)
        [i.startWriting() for i in interfaces]
        return any([i.canWriteImmidiately() for i in interfaces])

    def _getIO(self, addr):
        '''NB: Confusing.  This function is only called when there
        is by definition a readable interface.'''
        # Get all the interfaces that are referenced by this address
        interfaces = self._derefAddrToInterfaces(addr)

        # filter for the ones that are readable
        availableToRead = [i for i in interfaces if i.canReadImmidiately()]

        # There should be are least 1 that can read
        assert len(availableToRead) > 0, "Consistancy Failure"

        # We can only read one, so:
        luckyInterface = random.choice(availableToRead)

        result = luckyInterface.doRead()
        [i.finishReading() for i in interfaces]
        return result

    def _setIO(self, addr, value):
        '''NB: Confusing.  This function is only called when there
        is by definition a writable interface.'''
        # Get all the interfaces that are referenced by this address
        interfaces = self._derefAddrToInterfaces(addr)

        # filter for the ones that are readable
        availableToWrite = [i for i in interfaces if i.canWriteImmidiately()]

        # There should be are least 1 that can read
        assert len(availableToWrite) > 0, "Consistancy Failure"

        # We can to all the available so:
        [i.doWrite(value) for i in availableToWrite]
        [i.finishWriting() for i in interfaces]

    def installROM(self, rom):
        assert len(rom) == 64, "You wrong is the ROM size."
        self.rom[0:64] = rom[:]

    def _readIOBit(self, bitNumber):
        memEntry = self.mem[FA18A_constants.ioNameToAddress["io"]]
        return (memEntry << bitNumber) & 1

    def _writeIOBit(self, bitNumber, value):
        self.mem[FA18A_constants.ioNameToAddress["io"]] |= value >> (1 * bitNumber)

    @classmethod
    def maybeIncrementAddress(self, addr):
        # All comments below straight from the manual (except where noted)
        # Address incrementing, when applied to A or P, continues
        # from x03F to x040 but wraps from x07F to x000.
        if addr[0] == 0x07F:
            addr[0] -= 0x07F              # MRG: -= used to avoid clobbering bits 8/9
        # The same process occurs with addresses in the ROM space.
        elif addr[0] == 0x0FF:
            addr[0] -= 0x07F              # MRG: -= used to avoid clobbering bits 8/9
        elif addr[0] > 0x0FF:
            # Incrementing does not occur at all when the address lies
            # in the region of I/O ports and registers. Incrementing
            # never affects bits P8 or P9. P9 has no effect on memory
            # decoding; it simply enables the Extended Arithmetic
            # Mode when set.
            pass
        else:
            addr[0] += 1

    def doJump(self, address):
        self.P[:] = address
        self.loadNextWord()
        self.queueNextOp()

    def jumpToWarm(self):
        self.doJump(0xa9)

    def isExtendedArithmeticMode(self):
        # The 9th bit of the instruction pointer
        # Sets whether Extended arithmetic is used.
        return bu.getBitAsBool(self.P, 9)

    def fakeBootStream(self, completionAddress, transferAddress, dataWords):
        if transferAddress > 64:
            raise NotImplemented("Fake Boot stream can only be in RAM for now.")

        # Copy the transfered code into RAM:
        for wordNumber, word in enumerate(dataWords):
            # MRG TODO: use self._setAddr() here to emulate port activities
            self.mem[transferAddress + wordNumber] = word

        self.doJump(completionAddress)

    # MRG TODO: name cleanup below:
    def triggerNextWordLoad(self):
        self.loadNextWord()

    def loadNextWord(self):
        # Retrieve the instruction into I
        self.I[:] = self.mem[self.P[0]]
        self.opList = FA18A_util.unpackInstructionsFromUI32(self.I[0])
        self.slotNumber = 0

    def nextSlot(self):
        self.slotNumber += 1

    def maybeNextWord(self):
        if self.slotNumber == 4:
            self.loadNextWord()

    def popOp(self):
        self.maybeNextWord()
        op = self.opList[self.slotNumber]
        self.slotNumber += 1
        return op

    def getNextOp(self):
        # Return either one op, or an op and an address
        op = self.popOp()
        addr = self.popOp() if op.requiresAddress else None
        return op, addr

    def queueNextOp(self):
        self.nextOp, self.nextAddr = self.getNextOp()

    def runNextOp(self):
        self.nextOp.run(self, self.nextAddr)

    def getNextStepTime(self):
        return self.nextOp.getExecutionTime()

    def runStep(self):
        self.runNextOp()
        self.queueNextOp()

    def run(self, maxTime=np.inf, maxOpCount=np.inf):
        usedTime, opExedCount = 0, 0

        # Processor run loop
        while (usedTime < maxTime) and (opExedCount < maxOpCount):
            self.runStep()

            nextOpTime = self.nextOp.getExecutionTime()
            if nextOpTime is None:
                break

            # Increment the time and executed inscturction count
            usedTime += nextOpTime
            self.opExedCount += 1

        return opExedCount, usedTime

    def __str__(self):
        return "FA18A Node: %s" % self.name

if __name__ == "__main__":
    p = FA18A()
    visualizeMemory(p)
