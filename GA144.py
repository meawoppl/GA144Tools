import heapq, itertools, uuid
import GA144_rom

# A quick UUID lambda to get a hex string uuid
newUUID = lambda: uuid.uuid4().hex


class OperationSched(object):
    '''This is a class designed to run simulated events,
    each of which may or may not schedule additional event(s)
    in the future.'''
    def __init__(self):
        self.time = 0
        self.events = {}
        self.schedule = []

    def passTime(self, deltaTime):
        assert deltaTime >= 0, "No Time Travel Please!"
        self.time += deltaTime

    def whatTime(self):
        return self.time

    def enter(self, deltaTime, functionToCall, args=tuple(), kwargs=dict()):
        # Make a uuid for this event
        idee = newUUID()

        # Archive the function, args and kwargs
        self.events[idee] = (functionToCall, args, kwargs)

        # Enter the UUID in the heap
        eventTuple = (self.whatTime() + deltaTime, idee)
        heapq.heappush(self.schedule, eventTuple)

        return idee

    def runEvent(self):
        # Execute a single event
        eventTime, eventID = heapq.heappop(self.schedule)
        functionToCall, args, kwargs = self.events.pop(eventID)

        functionToCall(*args, **kwargs)

    def getNextEventTime(self):
        return self.schedule[0][0]

    def run(self, maxTime=float("inf"), maxEventCount=float("inf")):
        eventsRun = 0
        timePassed = 0

        # Actual Run Loop
        while (timePassed < maxTime) and (eventsRun < maxEventCount):
            # Give up if we run out of events
            if len(self.schedule) == 0:
                break

            # Move time forward as necessary
            theFuture = self.getNextEventTime() - self.whatTime()
            self.passTime(theFuture)

            # Run the event
            self.runEvent()

            # Update our semaphores for completion
            eventsRun += 1
            timePassed += theFuture


def maybeScheduleStep(pInstance, schedular):
    nextTime = pInstance.getNextStepTime()
    # Waiting/Blocked on IO
    if nextTime is None:
        return
    # Resechedule next operation to be run
    schedular.enter(nextTime, runStepAndMaybeSchedule, (pInstance, schedular))


def runStepAndMaybeSchedule(pInstance, schedular):
    '''This function is called when a operation is schedulaed to finish.
    It runs the state update step, then possibly schedules another operation
    to take place based on whether there is a known run-time.'''
    print(pInstance.nextOp)
    pInstance.runStep()

    maybeScheduleStep(pInstance, schedular)


class GA144(object):
    '''The goal of this module is to emulate a GA144 processor,
    comprising of 144 FA18A nodes.  To do this we:
    0) Write some infrastructure code to feed the others
    1) Make a schedular to deal with all the async handling
    2) Invoke and populate the 144 nodes with their respective ROM's
    3) Register all their IO read deps
    4) Run (fake) one or more boot streams
    5) Let the schedular take over'''

    def __init__(self, romFile="GA144.rom"):
        # Now create a python schedular that inteacts with the handles provided
        self.scheduler = OperationSched()

        # Make an iterator that has the array geometry of 8 x 18
        cooridinateIterator = itertools.product(range(8), range(18))

        # Map the iterator over the coordinates, making new nodes
        self.cores = {coord: GA144_rom.makeNodeByCoord(*coord) for coord in cooridinateIterator}

        print([str(core) for core in self.cores.items()])

        # Put them in their starting locations
        [node.jumpToWarm() for node in self.cores.values()]

        # Fake the boot stream, for now just based on the 2 wire async boot
        # asyncNode = self.cores[(7, 8)]

        # asyncNode.fakeBootStream()
        # MRG TODO: during boot stream, all nodes are actully already
        # running the jump to get get to the right port read pattern
        # More accurate to start the schedular earlier, the fake the
        # boot stream as an event in it.

        # Register all the nodes in the schedular
        [maybeScheduleStep(node, self.scheduler) for node in self.cores.values()]

        self.scheduler.run()


if __name__ == "__main__":
    p = GA144()
    p.run()
