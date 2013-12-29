# First up, lets test out implementation of the FA18 Processor.
# Step 0, the FA18 class should be importable and instanciatable

from FA18A import FA18A
lazyProcessor = FA18A()

# Alright, next up, we should be able to run any op code on a fresh processor
from FA18A_functions import allOpList

for op in allOpList:
    tester = FA18A()
    print op, op.requiresAddress
    print

    op.run(tester, 0)
