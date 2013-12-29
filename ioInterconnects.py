import numpy as np
# This is the embodiment of a node-node interconnect
# There are several considerations to getting this class "correct"
# that span this file and the GA144 embodiment

# Setup for Scenarios described below
# (Node 1) >---> Interconnect <---< (Node 2)

# Scenario 1
# Node 1 is about to execute a store command to node 2
# Node 2 is doing somethign else
# --- Flag the ionterconnect as ongoing write
# --- Reschedule  n1 after n2 reads

# Scenario 2
# Node 1 is about to execute a read  command to node 2
# Node 2 is doing something else
# --- Flag the ionterconnect as ongoing read
# --- Reschedule n1 after n2 writes

# Scenario 3
# Node 1 is about to execute a store command to node 2
# Node 2 is already reading
# --- Reschedule both immdiately

# Scenario 4
# Node 1 is about to execute a read  command to node 2
# Node 2 is already writing
# --- Reschedule both immdiately


class NodeInterConnect(object):
    def __init__(self, f18Instance1, f18Instance2, debug=True):
        self.pi_A = f18Instance1
        self.pi_B = f18Instance2

        self.debug = debug

        # Make sure the nodes are adjacent
        self.checkNodeConnectionValidity()

        # Make the ordering consistant
        self.normalizeNodes()

        # Wire in the calls to be made
        self.registerIOCalls()

        # Clear the buffers and interconnect flags
        self.reset()

    def reset(self):
        # Internal Flags
        self.isAnyNodeWriting = False
        self.isAnyNodeReading = False

        # Storage of the current data werd
        self.currentData = None

    def normalizeNodes(self):
        '''We have now arranged things such that node A is either
        above, or to the right of node B.  This makes the later
        logic more sensible.'''
        # Compute the delta
        dx, dy = self.computeNodeDelta()
        # Make it necessarily positive
        if dx + dy > 0:
            self.pi_A, self.pi_B = self.pi_B, self.pi_A

    def computeNodeDelta(self):
        # Compute the interconnect's nature (up/down)/(left/right)
        cA = self.pi_A.getCoordiantes()
        cB = self.pi_B.getCoordiantes()

        # Diff the positions
        dx = cA[0] - cB[0]
        dy = cA[1] - cB[1]

        return dx, dy

    def _warn(self, incons):
        # MRG TODO: add node numbers here
        if self.debug:
            print("Warning -- " + incons)

    # GA144 uses these to determine jump runtimes
    def canWriteImmidiately(self):
        return self.isAnyNodeReading

    def canReadImmidiately(self):
        return self.isAnyNodeWriting

    def registerCallAfterTransaction(self, call):
        pass

    def startWriting(self, pInstance, werd):
        if self.isAnyNodeWriting:
            self._warn("Both Nodes Writing!")

        self.isAnyNodeWriting = True
        self.currentData = werd[:]

        if self.isAnyNodeReading:
            self.transact()

    def finishWriting(self, pInstance):
        self.isAnyNodeWriting = False
        # Reschedule Next Op on writer Node

        # Nuke the Current Data
        cd = self.currentData
        self.currentData = None
        return cd

    def doRead(self):
        return self.currentData

    def doWrite(self, data):
        self.currentData = np.array(data)

    def startReading(self, pInstance):
        if self.isAnyNodeReading:
            self._warn("Both Nodes Reading!")
        self.isAnyNodeReading = True

    def finishReading(self, pInstance):
        self.isAnyNodeReading = False

    def transact():
        pass

    def updateProcFlags(self):
        pass

    def checkNodeConnectionValidity(self):
        dx, dy = self.computeNodeDelta()

        # Manhattan metric between the nodes should be exactly 1
        mm = abs(dx) + abs(dy)
        assert mm == 1, "Time to check your node geometry bro!"

    def registerIOCalls(self):
        # Compute the node delta
        dx, dy = self.computeNodeDelta()

        # Top/Bottom node Configuration
        if dx == 1:
            pass

        if dy == 1:
            # Assign LR calls
            pass
