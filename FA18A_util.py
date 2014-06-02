from bitUtils import *
from bitarray import bitarray
import FA18A_functions


# Semantic Sugar
def opNeedsAddress(op):
    return isinstance(op, (jumpOp, nextOp, ifOp, minusIfOp))

def loadNewWordAfterOp(op):
    return isinstance(op, (returnOp, executeOp, jumpOp, callOp, nextOp, ifOp, minusIfOp))

# Add the 5 bit of all functions
opCodeBitsToClass = { op.code : op for op in FA18A_functions.allOpList }

# lazy function to fetch a opCode class based on either
# The opcode (int)
# The bitarray representation there of
def getOp(rep):
    if isinstance(rep, bitarray):
        if rep.length() == 3:
            rep =  bitarray(rep + bitarray([False, False]))
        return opCodeBitsToClass[ baToInt(rep[::-1]) ]
    else:
        return opCodeBitsToClass[rep]

slotToJumpSpan = [ (0,  9), (0,  7), (0, 2) ]
slotToInstSpan = [(13, 17), (8, 12), (3, 7), (0,2) ]

slotMasks = [bitarray( [False, True, False, True, False] ),
             bitarray( [True, False, True, False, True ] ),
             bitarray( [False, True, False, True, False] ),
             bitarray( [True, False, True]               )]

def encodeDecode(ba, slotNumber):
    #print ba, slotMasks[ slotNumber ]
    return ba ^ slotMasks[ slotNumber ]

def packInstructionsToBits(instrList, encode=False):
    # Pack instructings into the 18 bit word format.
    # If the encode flag is set to true, return the xor of the word with 0x15555
    # Excluding the address of a jump etc

    slotNumberToBitLength = [5,5,5,3]

    ba = bitarray()
    for slotNumber, instruction in enumerate(instrList):

        if slotNumber == 3: assert instruction.minBitCount() == 3, "Last op needs to be 3 bits."

        # Lookup the maximum length that this instruction can be
        instrLength = slotNumberToBitLength[slotNumber]

        # Encode it into the bit array
        instrBits = instruction.getBitRep(instrLength)

        if encode:
            print repr(ba), slotNumber
            ba = encodeDecode(ba, slotNumber)

        ba += instrBits

        if instruction.requiresAddress:
            bitStart, bitStop = slotToAddressSpan[slotNumber]
            addrLength = bitStop - bitStart
            addressBits = intToBA(instrList[-1], addrLength)

            # Add the three bits of padding if necessary
            if slotNumber == 0:
                addressBits = bitarray([False, False, False]) + addressBits

            ba += addressBits
            break


    return ba

def unpackInstructionsFromBits(ba, decode=False):
    ops = []
    for slotNumber in range(4):
        startBit, stopBit = slotToInstSpan[slotNumber]
        opBits =  ba[startBit:stopBit+1][::-1]

        if decode:
            opBits = encodeDecode(opBits, slotNumber)

        opCode = getOp(opBits)

        #print "Segment", slotNumber, opBits, opCode
        ops.append(opCode)

        # Decode the address as the last thing and break
        if opCode.requiresAddress:
            addressStart, addressStop = slotToJumpSpan[slotNumber]
            address =  baToInt( ba[addressStart:addressStop+1] )
            ops.append(address)
            break

    return ops

def unpackInstructionsFromUI32(ui32, decode=False):
    return unpackInstructionsFromBits( intToBA(ui32, 18), decode = decode )

def packInstructionsToUI32(ops, encode=False):
    return baToInt(  packInstructionsToBits(ops, encode = encode) )

def doJumpArithmetic(currentP, jumpz, jumpOpAddressSlot):
    assert jumpOpAddressSlot in [0, 1, 2], "Jumpin Jesus!"
    # Comments below from DB002-110705-G144A12.pdf:
    # The destination address field simply replaces the low order bits of the current (incremented) value of P at the time the
    # jump instruction executes. Thus the scope of a slot 2 jump is very limited while a slot 0 jump can reach any addressable
    # destination, and can control P9 to explicitly enable or disable Extended Arithmetic Mode. Slot 1 and 2 jumps have no
    # effect upon P9, so its selection is unchanged as these jumps are executed. In the F18A, slot 1 and 2 jumps additionally
    # force P8 to zero. This means the destination of any slot 1 or 2 jump may never be in I/O space.
    jumpBitLength = {0:10, 1:8, 2:3}[jumpOpAddressSlot]

    p_ba = intToBA(currentP, 10)
    j_ba = intToBA(jumpz, 10)

    # print
    # print "Jump From:", currentP, jumpz, jumpOpAddressSlot
    # print "\tp", p_ba[::-1], currentP
    # print "\tj", j_ba[::-1], jumpz

    for bitNumber in range(jumpBitLength):
        p_ba[bitNumber] = j_ba[bitNumber]

    # Knock out bit 8 spec'ed in the above comment
    if jumpOpAddressSlot in [1,2]:
        p_ba[8] = 0

    # print "\tf", p_ba[::-1], baToInt(p_ba)

    # Return the new actual offset
    return baToInt(p_ba)



# My best crack at what I think the multiport execute looks like
["@P", "ex", 0]


# opCodeToName = {code : func.__name__ for code, func in opCodeToC.items() }

