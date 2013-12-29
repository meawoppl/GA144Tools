import heapq, uuid
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
