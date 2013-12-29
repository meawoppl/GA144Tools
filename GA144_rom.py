import numpy as np


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
    return GA144roms[x, y, :]
