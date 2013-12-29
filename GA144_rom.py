import numpy as np
import FA18A


def romFileLoader():
    '''Load the complete dump RAM+ROM+IO? and keep it in a Numpy array'''
    return np.fromfile(open("GA144.rom", "rb"), dtype="<u4").reshape((144, -1))


def romOnlyLoader():
    '''Load only the ROM, return it in a 144x64 array.'''
    dump = romFileLoader()
    return dump[:, 128:128 + 64]


GA144roms = romOnlyLoader()
GA144romsBlock = GA144roms.reshape((8, 18, -1))


def getROMByCoord(x, y):
    return GA144romsBlock[x, y, :]


def makeNodeByCoord(x, y):
    '''This is a quick function to make a processor
    instance based on the x, y location.  It instanciates
    a vanilla FA18A, then installs a ROM.'''
    newNode = FA18A.FA18A()
    newNode.installROM(getROMByCoord(x, y))
    return newNode
