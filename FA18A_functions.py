import inspect
import bitUtils as bu

# These Tiny classes take in a FA18 processor as an argumnet and
# emulate the memory and register changes that will
# take place given a certain opCode


class OpCode(object):
    requiresAddress = False

    def action(self, pi, addr):
        pass

    def after(self, pi, addr):
        pass

    def run(self, pInstance, addr=None):
        self.action(pInstance, addr)
        self.after(pInstance, addr)

    def minBitCount(self):
        if (self.code % 4) != 0:
            return 5
        else:
            return 3

    def getBitRep(self, nBits):
        assert nBits in [5, 3], "Derp"

        if nBits == 3:
            assert self.minBitCount() == 3, "Oh noes, 5/3 bit mixup!"
            return bu.intToBA(self.code, 5)[2:5]
        else:
            return bu.intToBA(self.code, 5)

    def __repr__(self):
        return self.strRep


# Arithmetic, Logic and Register Manipulation
class ARLMOp(OpCode):
    def getExecutionTime(self, pInstance):
        return 1.5


class MultStepOp(ARLMOp):
    # MRG TODO:
    # I am very unsure as to the correctness of the implementation of this function
    code = 0x10
    strRep = "+*"

    def action(self, pInstance, addr):
        # Fuse together the git rep of T and A
        # Signed Multiplicand is in S, unsigned multiplier in A, T=0 at start of a step sequence.
        # Uses T:A as a 36-bit shift register with multiplier in A. Does the following:

        A = pInstance.A
        T = pInstance.T
        S = pInstance.S

        cb = pInstance.carryBit

        if pInstance.isExtendedArithmeticMode():
            # 1. If bit A0 is zero, shifts the 36-bit register T:A right one bit arithmetically (T17 is not
            # changed and is copied into T16. T0 is copied to A17 and A0 is discarded.)
            ta = bu.intToBA(T, 18) + bu.intToBA(A, 18)
        else:
            # 2. If bit A0 is one, S and T are added as though they had both been extended to be
            # 19 bit signed numbers, and the 37-bit concatenation of this sum and A is shifted
            # right one bit to replace T:A. Overflow may occur if S and T are both nonzero and
            # their signs differ; this can only occur through improper initialization of T.

            # This instruction is affected in Extended Arithmetic Mode by including the latched carry in
            # the sum in case (2) above, and by latching the carry out from bit 17 of the sum, but
            # this is not a particularly useful effect and may be changed in later F18 versions.
            # You must arrange that the previously executed instruction has not changed the values of
            # S, T or P9. Use nop preceding Multiply Step if necessary to meet this condition.
            st_sum = S + T + cb
            ta = bu.intToBA(st_sum, 19) + bu.intToBA(A, 18)

        # This is the shared right shift as above
        ta[1] = ta[0]
        ta = ta[1:]
        ta.append(False)

        # Unpack the shared shift register into the two we store it as
        T[:] = bu.baToInt(ta[0:18])
        A[:] = bu.baToInt(ta[19:])


class LeftShiftOp(ARLMOp):
    code = 0x11
    strRep = "2*"

    def action(self, pInstance, addr):
        pInstance.T[:] = 1 << pInstance.T[:]


class RightShiftOp(ARLMOp):
    code = 0x12
    strRep = "2/"

    def action(self, pInstance, addr):
        pInstance.T[:] = 1 >> pInstance.T[:]


class NotOp(ARLMOp):
    code = 0x13
    strRep = "-"

    def action(self, pInstance, addr):
        pInstance.T[:] = ~pInstance.T[:]


class PlusOp(ARLMOp):
    code = 0x14
    strRep = "+"

    def action(self, pInstance, addr):
        sumOfRegs = pInstance.dataStack.pop() + pInstance.dataStack.pop()

        # Include the carry in the sum if necessary
        if pInstance.isExtendedArithmeticMode():
            sumOfRegs += pInstance.carryBit

        # Set the Carry Bit
        if pInstance.isExtendedArithmeticMode():
            pInstance.carryBit = bu.getBitAsBool(sumOfRegs, 19)

        # Push the sum back onto the stack after truncating to a word size
        pInstance.dataStack.push(bu.truncateToWord(sumOfRegs))


class AndOp(ARLMOp):
    code = 0x15
    strRep = "and"

    def action(self, pInstance, addr):
        op1 = pInstance.dataStack.pop()
        op2 = pInstance.dataStack.pop()
        pInstance.dataStack.push(op1 & op2)


class XorOp(ARLMOp):
    code = 0x16
    strRep = "or"

    def action(self, pInstance, addr):
        op1 = pInstance.dataStack.pop()
        op2 = pInstance.dataStack.pop()

        pInstance.dataStack.push(op1 ^ op2)


class DropOp(ARLMOp):
    code = 0x17
    strRep = "drop"

    def action(self, pInstance, addr):
        # NB: not clear on this one
        pInstance.dataStack.pop()


class DupOp(ARLMOp):
    code = 0x18
    strRep = "dup"

    def action(self, pInstance, addr):
        pInstance.dataStack.push(pInstance.T)


class PopOp(ARLMOp):
    code = 0x19
    strRep = "pop"

    def action(self, pInstance, addr):
        pInstance.dataStack.push(pInstance.returnStack.pop())


class OverOp(ARLMOp):
    code = 0x1A
    strRep = "over"

    def action(self, pInstance, addr):
        op1 = pInstance.dataStack.pop()
        op2 = pInstance.dataStack.pop()

        pInstance.dataStack.push(op2)
        pInstance.dataStack.push(op1)
        pInstance.dataStack.push(op2)


class AFetchOp(ARLMOp):
    code = 0x1B
    strRep = "a"

    def action(self, pInstance, addr):
        pInstance.dataStack.push(pInstance.A)


class NoOp(ARLMOp):
    code = 0x1C
    strRep = "."

    def action(self, pInstance, addr):
        pass


class PushOp(ARLMOp):
    code = 0x1D
    strRep = "push"

    def action(self, pInstance, addr):
        pInstance.returnStack.push(pInstance.dataStack.pop())


class BStoreOp(ARLMOp):
    code = 0x1E
    strRep = "b!"

    def action(self, pInstance, addr):
        pInstance.B[:] = pInstance.dataStack.pop()


class AStoreOp(ARLMOp):
    code = 0x1F
    strRep = "a!"

    def action(self, pInstance, addr):
        pInstance.A[:] = pInstance.dataStack.pop()


# Memory, read, write, ops
class MRWOp(OpCode):
    def getExecutionTime(pInstance):
        # These actully need to inspect the processor and see if there
        # Is a matching r/w available.  If so, then 5.1 ns, otherwise
        # potentially infinite.
        return 5.1


def _fetch(pInstance, addr):
    pInstance.dataStack.push(pInstance.mem[addr])


class FetchPOp(MRWOp):
    code = 0x08
    strRep = "@p"

    def action(self, pInstance, addr):
        _fetch(pInstance, pInstance.P[0])


class FetchAPlus(MRWOp):
    code = 0x09
    strRep = "@+"

    def action(self, pInstance, addr):
        _fetch(pInstance, pInstance.A[0])
        pInstance.maybeIncrementAddress(pInstance.A)


class FetchBOp(MRWOp):
    code = 0x0A
    strRep = "@b"

    def action(self, pInstance, addr):
        _fetch(pInstance, pInstance.B[0])
        pInstance.maybeIncrementAddress(pInstance.B)


class FetchAOp(MRWOp):
    code = 0x0B
    strRep = "@"

    def action(self, pInstance, addr):
        _fetch(pInstance, pInstance.A[0])
        pInstance.maybeIncrementAddress(pInstance.A)


def _store(pInstance, addr):
    pInstance.mem[addr] = pInstance.dataStack.pop()


class StorePOp(MRWOp):
    code = 0x0C
    strRep = "!p"

    def action(self, pInstance, addr):
        _store(pInstance, pInstance.P[0])
        pInstance.maybeIncrementAddress(pInstance.P)


class StorePlusOp(MRWOp):
    code = 0x0D
    strRep = "!+"

    def action(self, pInstance, addr):
        _store(pInstance, pInstance.A[0])
        pInstance.maybeIncrementAddress(pInstance.A)


class StoreBOp(MRWOp):
    code = 0x0E
    strRep = "!b"

    def action(self, pInstance, addr):
        _store(pInstance, pInstance.B[0])


class StoreAOp(MRWOp):
    code = 0x0F
    strRep = "!"

    def action(self, pInstance, addr):
        _store(pInstance, pInstance.A[0])


class FCOp(OpCode):
    @classmethod
    def getExecutionTime(pInstance):
        return 5.1


class ReturnOp(FCOp):
    code = 0x00
    strRep = ";"

    def action(self, pInstance, addr):
        pInstance.P[:] = pInstance.R[:]

    def after(self, pInstance, addr):
        pInstance.triggerNextWordLoad()


class ExecuteOp(FCOp):
    code = 0x01
    strRep = "ex"

    def action(self, pInstance, addr):
        pInstance.R[:], pInstance.P[:] = pInstance.P[:], pInstance.R[:]

    def after(self, pInstance, addr):
        pInstance.triggerNextWordLoad()


class JumpOp(FCOp):
    code = 0x02
    strRep = "name ;"
    requiresAddress = True

    def action(self, pInstance, addr):
        pInstance.P[:] = addr

    def after(self, pInstance, addr):
        pInstance.triggerNextWordLoad()


class CallOp(FCOp):
    code = 0x03
    strRep = "name"
    requiresAddress = True

    def action(self, pInstance, addr):
        pInstance.R[:] = pInstance.P[:]


class UnextOp(FCOp):
    code = 0x04
    strRep = "unext"

    def action(self, pInstance, addr):
        if pInstance.R[0] == 0:
            pInstance.maybeIncrementAddress(pInstance.P)
        else:
            pInstance.R[0] -= 1

    @classmethod
    def getExecutionTime(pInstance):
        return 2.1


class NextOp(FCOp):
    code = 0x05
    strRep = "next"
    requiresAddress = True

    def action(self, pInstance, addr):
        if pInstance.R == 0:
            pInstance.maybeIncrementAddress(pInstance.P)
        else:
            pInstance.R -= 1
            pInstance.P[:] = addr
            pInstance.triggerNextWordLoad()


class IfOp(FCOp):
    code = 0x06
    strRep = "if"
    requiresAddress = True

    def action(self, pInstance, address):
        if pInstance.T[0] != 0:
            pInstance.maybeIncrementAddress(pInstance.P)
        else:
            pInstance.P[0] = address
            pInstance.triggerNextWordLoad()


class UnlessOp(FCOp):
    code = 0x07
    strRep = "-if"
    requiresAddress = True

    def action(self, pInstance, address):
        if bu.getBitAsBool(pInstance.T[0], 17):
            pInstance.maybeIncrementAddress(pInstance.P)
        else:
            pInstance.P[0] = address
            pInstance.triggerNextWordLoad()


# A quick tool for gathering the classes above and instanciating one of each
def gatherOpsOfSubclass(ofClass, namespace=locals()):
    opCollection = [op for name, op in namespace.items() if (inspect.isclass(op) and issubclass(op, ofClass))]

    # Issubclass is valid for self to self?!?!? (whatevs)
    opCollection.remove(ofClass)
    # Instanciate all and return
    return [op() for op in opCollection]

# Gather the different types
ARLMOpList = gatherOpsOfSubclass(ARLMOp)
FCOpList = gatherOpsOfSubclass(FCOp)
MRWOpList = gatherOpsOfSubclass(MRWOp)

# All operations sorted by code number
allOpList = sorted(ARLMOpList + FCOpList + MRWOpList, cmp=lambda a, b: cmp(a.code, b.code))

# Print some diagnostic schlock
for op in allOpList:
    print "0x%02X " % op.code, op.requiresAddress, op.minBitCount(), "--", op.__class__.__name__.ljust(10),
    print
