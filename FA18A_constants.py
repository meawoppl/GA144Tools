opCodeToSymbol = {}

# "Transfer of program control"
opCodeToSymbol[ 0x00 ] = ";"
opCodeToSymbol[ 0x01 ] = "ex"
opCodeToSymbol[ 0x02 ] = "name;"
opCodeToSymbol[ 0x03 ] = "name"

opCodeToSymbol[ 0x04 ] = "unext"
opCodeToSymbol[ 0x05 ] = "next"
opCodeToSymbol[ 0x06 ] = "if"
opCodeToSymbol[ 0x07 ] = "-if"

# "Memory read and write" - 5.1 ns
opCodeToSymbol[ 0x08 ] = "@p"
opCodeToSymbol[ 0x09 ] = "@+"
opCodeToSymbol[ 0x0A ] = "@b"
opCodeToSymbol[ 0x0B ] = "@"

opCodeToSymbol[ 0x0C ] = "!p"
opCodeToSymbol[ 0x0D ] = "!+"
opCodeToSymbol[ 0x0E ] = "!b"
opCodeToSymbol[ 0x0F ] = "!"

# "Arithmetic, Logic and Register Manipulation" - 1.5 ns
opCodeToSymbol[ 0x10 ] = "+*"
opCodeToSymbol[ 0x11 ] = "2*"
opCodeToSymbol[ 0x12 ] = "2/"
opCodeToSymbol[ 0x13 ] = "-"

opCodeToSymbol[ 0x14 ] = "+"
opCodeToSymbol[ 0x15 ] = "and"
opCodeToSymbol[ 0x16 ] = "or"
opCodeToSymbol[ 0x17 ] = "+*"

opCodeToSymbol[ 0x18 ] = "dup"
opCodeToSymbol[ 0x19 ] = "pop"
opCodeToSymbol[ 0x1A ] = "over"
opCodeToSymbol[ 0x1B ] = "a"

opCodeToSymbol[ 0x1C ] = "."
opCodeToSymbol[ 0x1D ] = "push"
opCodeToSymbol[ 0x1E ] = "b!"
opCodeToSymbol[ 0x1F ] = "a!*"


# From "F18A Technology Reference" pg 11
ioPorts = [("io"  , 0x15D),
           ("data", 0x141),
           ("---u", 0x145),
           ("--l-", 0x175),
           ("--lu", 0x165),
           ("-d--", 0x115),
           ("-d-u", 0x105),
           ("-dl-", 0x135),
           ("-dlu", 0x125),
           ("r---", 0x1D5),
           ("r--u", 0x1C5),
           ("r-l-", 0x1F5),
           ("r-lu", 0x1E5),
           ("rd--", 0x195),
           ("rd-u", 0x185),
           ("rdl-", 0x1B5),
           ("rdlu", 0x1A5)]

# MRG TODO: figure out the bit-bang logic for the above
# ioAddresses = [v for k, v in ioAddresses.items()]
# ioAddresses.sort()
# print array(ioAddresses)
# print diff(array(ioAddresses))


# Semantic Sugar 
ioNameToAddress = {}
ioAddressToName = {}

for ioName, ioAddr in ioPorts:
    ioNameToAddress[ioName] = ioAddr
    ioAddressToName[ioAddr] = ioName
