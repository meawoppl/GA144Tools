
# This is the embodiment of a node-node interconnect
# There are several considerations to getting this class "correct"
# that span this file and the GA144 embodiment


class NodeInterConnect(object):
    def __init__(self, f18Instance1, f18Instance2):
        self.pi_A = f18Instance1
        self.pi_B = f18Instance2

        # Make sure the nodes are adjacent
        self.checkNodeConnectionValidity()

        # Make the ordering consistant
        self.normalizeNodes()

        # Wire in the calls to be made
        self.registerIOCalls()

        # Storage of the current data werd
        self.currentData = None

    def normalizeNodes(self):
        '''We have now arranged things such that nodeA is either
        Above, or to the Right of node B.  This makes the later
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

    # These will return true only when a node is blocking to
    # Write on the interconnect
    def isBeingReadFrom(self):
        pass

    def isBeingWrittenTo(self):
        pass

    def isCurrentlyWritable(self):
        pass

    def isCurrentlyReadable(self):
        pass

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
