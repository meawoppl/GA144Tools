from bitarray import bitarray
import numpy as np

# MRG TODO: assertions on input/output of all of these


def baToInt(ba):
    assert ba.length() <= 32, "too long!  Tee hee hee."

    i = 0
    for n, bit in enumerate(ba):
        if not bit:
            continue
        i += 2 ** n
    return i


def intToBA(integer, nbits):
    ba = bitarray()
    for x in range(nbits):
        ba.append(((integer >> x) & 1) == 1)
    return ba


def intToBA5(integer):
    return intToBA(integer, 5)

def intToBA3(integer):
    return intToBA(integer, 3)


# Grab N bits
def unpackBits(werd, start=0, stop=18, reverse=False):
    # Unpack and trim bits
    ba = bitarray(0)
    ba.fromstring(werd.tostring())
    ba = ba[start:stop]
    # Reverse the bits if requested
    if reverse:
        ba = ba[::-1]

    # Pad it to 32 bits
    ba = bitarray(32 - len(ba)) + ba
    # Convert back to a uint32
    return np.fromstring(ba.tobytes(), dtype=np.uint32)


# Random utility functions
def truncateToWord(werd):
    return unpackBits(werd, 0, 18)


def getBitAsBool(werd, bitNum):
    ba = bitarray(0)
    ba.frombytes(werd.tostring())
    return ba[bitNum]


def setBit(integer, bitNum, state):
    # Nuke that bit to 0
    bitMask = 2 ** bitNum
    integer[:] = (integer[:] & ~bitMask) | (bitMask * state)
