#      ******************************************************************
#      *                                                                *
#      *                       Block Feeder Object                      *
#      *                                                                *
#      *            Arnav Wadhwa                   12/08/2022           *
#      *                                                                *
#      ******************************************************************

# To import the DPiClockNBlock library
import sys
sys.path.insert(0, "..")

from DPi_ClockNBlock_Python.DPiClockNBlock import DPiClockNBlock
from time import sleep

# More accurate timer
from timeit import default_timer as timer


BLOCK_SIZE = 31  # block side length in mm


class BlockFeeder:

    # Constants
    dpiClockNBlock = DPiClockNBlock()

    # For state function
    state = 0
    newState = False

    # Start timer
    start = 0

    # Constants
    _STATE_READY =           0
    _STATE_BLOCK_REMOVED =   1
    _STATE_FEED1 =           2
    _STATE_FEED2 =           3
    _STATE_IDLE =            4

    def __init__(self, solenoid_side: int, solenoid_up: int, board_number: int, solenoidBoard):
        self._SOLENOID_SIDE = solenoid_side
        self._SOLENOID_UP = solenoid_up
        self.BOARD_NUMBER = board_number
        self.dpiSolenoid = solenoidBoard

    def setup(self) -> bool:

        self.dpiClockNBlock.setBoardNumber(self.BOARD_NUMBER)
        self.dpiSolenoid.setBoardNumber(0)

        if not self.dpiClockNBlock.initialize():
            print("Communication with DPiClockNBlock board failed")
            return False

        self.initializeBlockFeeders()

        return True

    # To be run while everything is homing
    def initializeBlockFeeders(self) -> bool:
        print("initializing")
        # Check if block already at the top position
        if self.dpiClockNBlock.readExit():
            return True

        # Otherwise, cycle the blocks
        self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
        self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)
        sleep(2)
        # If there is a block send it to ready position
        if self.dpiClockNBlock.readFeed_1() and not self.dpiClockNBlock.readFeed_2():
            self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, True)
            while not self.dpiClockNBlock.readFeed_2():
                sleep(0.1)
        if self.dpiClockNBlock.readFeed_2():
            self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, True)
            while not self.dpiClockNBlock.readExit():
                sleep(0.1)
            self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)
            self.setState(self._STATE_READY)
            return True
        return False

    def process(self):

        print(f"State: {self.state}, NewState: {self.newState}, Board: {self.BOARD_NUMBER}")

        # Check if arrow needs to be turned on
        self.dpiClockNBlock.arrowToggle(self.dpiClockNBlock.readEntrance())

        if self.state == self._STATE_READY:
            # Check if it is actually ready, if not switch state to block removed
            if not self.dpiClockNBlock.readExit():
                self.setState(self._STATE_BLOCK_REMOVED)
            return

        elif self.state == self._STATE_BLOCK_REMOVED:

            # Retract the up piston
            if self.newState:
                self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
                self.start = timer()
                self.newState = False
                return
            elif timer() - self.start > 2:
                self.setState(self._STATE_FEED2)
                return

        elif self.state == self._STATE_FEED1:

            if self.newState:
                self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, True)
                self.newState = False
                return
            elif self.dpiClockNBlock.readExit():
                self.setState(self._STATE_READY)
                self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)
                return
            return

        elif self.state == self._STATE_FEED2:
            # Check if we have a block at Feed 1, if not set state to idle
            if not self.dpiClockNBlock.readFeed_1():
                self.setState(self._STATE_IDLE)
                return
            # Push the block over
            if self.newState:
                self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, True)
                self.newState = False
                return
            # Wait for block to arrive at the side
            if self.dpiClockNBlock.readFeed_2():
                self.setState(self._STATE_FEED1)
                return
            return

        elif self.state == self._STATE_IDLE:
            # Wait for a block to be inserted then switch to feed 2
            if self.dpiClockNBlock.readFeed_1():
                self.setState(self._STATE_FEED2)
                return
            return

    def isBLockAvailable(self) -> bool:
        return self.state == self._STATE_READY

    def setState(self, nextState: int):
        self.state = nextState
        self.newState = True

    def isReady(self):
        if self._STATE_READY:
            return True
        else:
            return False




