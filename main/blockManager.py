#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *            Brian Vesper                   12/03/2022           *
#      *                                                                *
#      ******************************************************************
from blockFeeder import BlockFeeder
from clockHands import Clock

class BlockManager:

    # TODO: Figure out how to not repeat this code
    #
    # pin assignments show how the pistons are wired to the DPiSolenoid board
    #
    _BLOCK_FEEDER0__FIRST_PISTON__DRIVER_NUM = 6
    _BLOCK_FEEDER0__SECOND_PISTON__DRIVER_NUM = 7
    _BLOCK_FEEDER1__FIRST_PISTON__DRIVER_NUM = 4
    _BLOCK_FEEDER1__SECOND_PISTON__DRIVER_NUM = 3
    _BLOCK_FEEDER2__FIRST_PISTON__DRIVER_NUM = 9
    _BLOCK_FEEDER2__SECOND_PISTON__DRIVER_NUM = 8
    _BLOCK_FEEDER3__FIRST_PISTON__DRIVER_NUM = 0
    _BLOCK_FEEDER3__SECOND_PISTON__DRIVER_NUM = 1

    _NUMBER_OF_BLOCK_FEEDERS = 4

    # For the ClockNBlock boards
    blockFeeder0 = BlockFeeder(_BLOCK_FEEDER0__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER0__SECOND_PISTON__DRIVER_NUM, 0)
    blockFeeder1 = BlockFeeder(_BLOCK_FEEDER1__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER1__SECOND_PISTON__DRIVER_NUM, 1)
    blockFeeder2 = BlockFeeder(_BLOCK_FEEDER2__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER2__SECOND_PISTON__DRIVER_NUM, 2)
    blockFeeder3 = BlockFeeder(_BLOCK_FEEDER3__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER3__SECOND_PISTON__DRIVER_NUM, 3)

    blockFeeder0.setPosition(345, -0.906, -62)

    # TODO: Change these to the actual values once we train them
    blockFeeder1.setPosition(345, -0.906, -62)
    blockFeeder2.setPosition(345, -0.906, -62)

    blockFeeder3.setPosition(340, 0.661, -63)
    blockFeeders = [blockFeeder0, blockFeeder1, blockFeeder2, blockFeeder3]

    # Middle of build positions arranged in r, theta, Z
    Build0 = (422, -0.134, -44)
    Build1 = (419, -1.696, -45)
    Build2 = (426, 2.998, -42)
    Build3 = (420, 1.437, -42)
    _BUILD_POS = [Build0, Build1, Build2, Build3]

    # Block Feeder positions
    Feed0 = (345, -0.906, -62)

    # TODO: Change these to the actual values once we train them
    Feed1 = (345, -0.906, -62)
    Feed2 = (345, -0.906, -62)

    Feed3 = (340, 0.661, -63)

    feederPos = [Feed0, Feed1, Feed2, Feed3]

    # Constants
    _BLOCK_SIZE = 31 #Block size in mm

    # Objects we need to talk to


    # TODO: Implement these functions
    #  getNextFeeder() returns list feeder coordinates we want to go to
    #  placeBlock() returns list the build site coordinates we want to go to
    #  goToReady() returns path to go to ready position

    previousFeeder = 3
    def getNextFeeder(self):
        nextFeeder = self.nextFeeder()
        if not self.blockFeeders[nextFeeder].isReady():
            nextFeeder = self.nextFeeder()
        else:


    # Private helper functions
    def nextFeeder(self):
        nextFeeder = (self.previousFeeder + 1) % 4
        self.previousFeeder = nextFeeder
        return nextFeeder

    def isClockTooClose(self, position: float):
        _MINUTE_HAND = 1
        distanceFromPosition = 
        if


