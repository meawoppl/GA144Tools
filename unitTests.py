# Alright, this is how we regression test our little fake processor
# We startup a new (blank slate each time)
# Run a couple of commands, then make sure the output makes sense

def over18Bit(number):
    if number > 2**18:
        raise RuntimeError("Failure to maintain word size")


from bitUtils import *



def testConversions():
    # Test bit array conversion functions
    print "Testing Bit Conversions"
    i = 0
    for i in xrange(2**18):
        assert i == baToInt(intToBA(i, 32)), "wtf!"
        i += 1

    print "Success"

# Arithmatic operations can be run at any time,
# with any stack state, so lets generate all the possible combinations
import itertools
import FA18A_functions

# Woah this line is hairy.  Make all possible arithmatic/logic op combos
allArithmaticCombos = itertools.combinations_with_replacement(FA18A_functions.ARLMOpList, 4)
allValidArithmaticCombos = filter(lambda ops: ops[3].minBitCount() == 3, allArithmaticCombos)

allValidArithmaticCombos += list(itertools.combinations_with_replacement(FA18A_functions.ARLMOpList, 3))
allValidArithmaticCombos += list(itertools.combinations_with_replacement(FA18A_functions.ARLMOpList, 2))
allValidArithmaticCombos += list(itertools.combinations_with_replacement(FA18A_functions.ARLMOpList, 1))


# import random
# random.shuffle(allArithmaticCombos)

print "Testing All arithmatic combos (%i):" % len(allValidArithmaticCombos)
for n, opList in enumerate(allValidArithmaticCombos[::-1]):

    # For each one, it should serialize and deserizlize back to the correct bitstream
    packedBits = FA18A_functions.packInstructionsToBits(opList)

    newOpList =  FA18A_functions.unpackInstructionsFromBits(packedBits)

    if len(opList) == 2:
        print "packed to %i bits:" % len(packedBits), packedBits
        print n, [op.code for op in opList]
        print " ".join([str(op) for op in opList])

        print opList
        print newOpList

    assert all( [op1 == op2 for op1, op2 in zip(opList, newOpList)] ), "Op serializtion failure!"
