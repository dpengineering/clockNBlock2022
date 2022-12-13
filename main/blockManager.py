#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *            Brian Vesper                   12/03/2022           *
#      *                                                                *
#      ******************************************************************

from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiSolenoid import DPiSolenoid
from DPiClockNBlock import DPiClockNBlock
from dpeaDPi.DPiStepper import DPiStepper

import queue

dpiRobot = DPiRobot()
dpiSolenoid = DPiSolenoid()
dpiClockNBlock = DPiClockNBlock()
dpiStepper = DPiStepper()


class blockManager:
    _STATE_READY = 0
    _STATE_MOVE = 1
    _STATE_GRAB = 2
    _STATE_RELEASE = 3

    _STATE_NO_BLOCK = 4
    _STATE_HAS_BLOCK = 5

    currentAction = []
    nextAction = []

    state = 4
    newState = False

    actions = queue.Queue()

    def __int__(self):
        pass

    def setup(self):
        pass

    def process(self):
        #Gets the next feed location(still need to write function and logic
        #but should return the coords for the feed where the next block should be picked up).
        #Then sets an action to move to the feed and then one more to grab the block before changing states.
        if self.state == self._STATE_NO_BLOCK:
            pos = self.getFeed()
            action = [self._STATE_MOVE,pos]
            self.actions.put(action)
            action[0] = self._STATE_GRAB
            self.actions.put(action)
            self.state = self._STATE_HAS_BLOCK

        #TODO: Not sure how to do this one cuz might be multiple moves to get place block.
        #Should probably que one action per state so it doesnt que a bazillion actions.
        #Maybe have function that creates a list of the moves needed and then this just adds one each time
        if self.state == self._STATE_HAS_BLOCK:
            pass

    #TODO: Write getFeed(). Should return coords of a feeder with a block. IDK what logic to use to choose which feed yet.

    def getNextState(self):
        return self.nextAction[0]

    def getNextPos(self):
        return self.nextAction[1]

    def cycleAction(self):
        self.currentAction = self.nextAction
        self.nextAction = self.actions.get()
