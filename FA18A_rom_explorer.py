import numpy as np
import bitarray as ba
import struct
from pylab import text, show, figure, pcolor

import FA18A_functions
import FA18A_util
from FA18A_util import unpackInstructionsFromUI32
from GA144_rom import romFileLoader


def groupsOfN(iterbl, groupSize):
    assert (len(iterbl) % groupSize) == 0, "Iterable is not divisable into groups of %i" % groupSize

    intermediate = []
    for n, element in enumerate(iterbl):
        intermediate.append(element)
        if len(intermediate) == groupSize:
            yield tuple(intermediate)
            intermediate = []


def figureOutDecoding():
    # Open the file
    romFile = open("GA144.rom", "rb").read()
    romFile = [struct.unpack("<B", e)[0] for e in romFile]

    # Group the rom into tuples of 4 words
    wordGroups = groupsOfN(romFile, 4)
    concated = []

    # Sanity check all the words
    for wordNumber, werd in enumerate(wordGroups):
        blockStr = " ".join(["%03i" % bi for bi in werd])

        b0, b1, b2, b3 = werd
        smashedDown = b0 + (b1 << 8) + (b2 << 16)

        bits = ba.bitarray()
        if wordNumber < 128:
            for b in werd:
                bits.frombytes(chr(b))
                bits.fill()
            print "%03i" % wordNumber, "|", blockStr, "0x%05x" % smashedDown, bits

        assert(b3) == 0, "There should be no bits here! " + str(b3)
        assert(b2) < 4, "WTF bits."

        concated.append(smashedDown)

    assert (len(concated) % 144) == 0, "Needs to be equal rom size for all 144 procs ^^"

    return np.array(list(groupsOfN(concated, 512)))


def prettyFormatWerdIntoOps(werd, offset):
    ops = unpackInstructionsFromUI32(werd)

    asIntAndHex = lambda i: "%i-0x%03x" % (i, i)

    # Calculate the real address being jumped to
    if ops[-1] not in FA18A_functions.allOpList:
        codedAddr = ops[-1]
        pAtOpTime = offset + 1
        jumpDest = FA18A_util.doJumpArithmetic(pAtOpTime, codedAddr, len(ops) - 2)
        ops[-1] = "\t\t" + ("\t" * (4 - len(ops))) + asIntAndHex(codedAddr) + " (" + asIntAndHex(jumpDest) + ")"

    # stringify them together
    return "".join([str(op).ljust(8) for op in ops])


def printROMOps(dataz):
    for n, werd in enumerate(dataz):
        memOffset = n + 128
        dMemOffset = memOffset + 64
        print "%i & %i | 0x%03x & 0x%03x | 0x%05x |" % (memOffset, dMemOffset, memOffset, dMemOffset, werd), prettyFormatWerdIntoOps(werd, memOffset)


def getAllWarmJumpsAddr():
    romz = romFileLoader()
    jumpAddrs = []
    for cpuNumber in range(144):
        newLocation = unpackInstructionsFromUI32(romz[cpuNumber, 0xa9])[1]
        jumpAddrs.append(newLocation)
    return jumpAddrs


def plotAllWarmJumps():
    jumpAddrs = np.array(getAllWarmJumpsAddr()).reshape((8, 18))
    figure()
    pcolor(jumpAddrs)
    for (x, y), v in np.ndenumerate(jumpAddrs):
        text(y + 0.125, x + 0.5, "0x%03x" % v)
    show()


def doubleCheckDecoders():
    a = figureOutDecoding()
    print a.shape

    b = romFileLoader()
    print b.shape

    print "Decoders check out:", np.all(a == b)
