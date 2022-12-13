#      ******************************************************************
#      *                                                                *
#      *                       Block Feeder Object                      *
#      *                                                                *
#      *            Arnav Wadhwa                   12/08/2022           *
#      *                                                                *
#      ******************************************************************

from DPiClockNBlock import DPiClockNBlock
from dpeaDPi.DPiSolenoid import DPiSolenoid
from time import sleep

# More accurate timer
from timeit import default_timer as timer

# Constants
dpiClockNBlock = DPiClockNBlock()
dpiSolenoid = DPiSolenoid()


class BlockFeeder:

    _SOLENOID_UP = 0
    _SOLENOID_SIDE = 0
    BOARD_NUMBER = 0

    # For state function
    state = 0
    newState = False

    # Constants
    _STATE_READY =           0
    _STATE_BLOCK_REMOVED =   1
    _STATE_FEED1 =           2
    _STATE_FEED2 =           3
    _STATE_IDLE =            4

    def __init__(self, solenoid_side: int, solenoid_up: int, board_number: int):
        self._SOLENOID_SIDE = solenoid_side
        self._SOLENOID_UP = solenoid_up
        self.BOARD_NUMBER = board_number

    def setup(self) -> bool:

        dpiClockNBlock.setBoardNumber(self.BOARD_NUMBER)
        dpiSolenoid.setBoardNumber(0)

        if not dpiClockNBlock.initialize():
            print("Communication with DPiClockNBlock board failed")
            return False

        if not dpiSolenoid.initialize():
            print("Communication with DPiSolenoid board failed")
            return False

        self.initializeBlockFeeders()

        return True

    # To be run while everything is homing
    def initializeBlockFeeders(self) -> bool:

        # Check if block already at the bottom position
        if dpiClockNBlock.readExit():
            return True

        # Otherwise, cycle the blocks
        dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
        dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)

        # If there is a block send it to ready position
        if dpiClockNBlock.readFeed_1():
            dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, True)
            while not dpiClockNBlock.readFeed_2():
                sleep(0.1)
            dpiSolenoid.switchDriverOnOrOff((self._SOLENOID_UP, True))
            while not dpiClockNBlock.readExit():
                sleep(0.1)
            self.state = 0
            return True
        return False

    def process(self):
        # Check if arrow needs to be turned on
        if dpiClockNBlock.readEntrance():
            self.toggleArrow(True)
        else:
            self.toggleArrow(False)

        if self.state == self._STATE_READY:
            # Check if it is actually ready, if not switch state to Feed 1
            if not dpiClockNBlock.readExit():
                self.setState(self._STATE_BLOCK_REMOVED)
            return

        elif self.state == self._STATE_BLOCK_REMOVED:
            # To be in this state, we need to have no block at the exit and no block at feed 2 sensor
            if dpiClockNBlock.readExit():
                self.setState(self._STATE_READY)
                return
            if dpiClockNBlock.readFeed_2():
                self.setState(self._STATE_FEED1)
                return
            # Now, retract the up piston
            start = timer()
            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
                return
            elif start - timer() > 2:
                self.setState(self._STATE_FEED2)
                return

        elif self.state == self._STATE_FEED1:
            # Check if we have a block to push up, otherwise send to Feed 2
            if not dpiClockNBlock.readFeed_2():
                self.setState(self._STATE_FEED2)
                return

            # If we haven't pushed over the side piston, do it now
            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, True)
                newState = False
                return
            # Wait for side piston to be fully over, then change state to ready
            elif dpiClockNBlock.readExit():
                self.setState(self._STATE_READY)
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)
                return
            return

        elif self.state == self._STATE_FEED2:
            # Check if we have a block at Feed 1, if not set state to idle
            if not dpiClockNBlock.readFeed_2():
                self.setState(self._STATE_IDLE)
                return
            # Push the block over
            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, True)
                return
            # Wait for block to arrive at the top, then switch state and retract side piston
            if dpiClockNBlock.readFeed_2():
                self.setState(self._STATE_FEED1)
                return
            return

        elif self.state == self._STATE_IDLE:
            # Wait for a block to be inserted then switch to feed 2
            if dpiClockNBlock.readFeed_1():
                self.setState(self._STATE_FEED2)
                return
            return

    def isBLockAvailable(self) -> bool:
        return self.state == self._STATE_READY

    def setState(self, nextState: int):
        self.state = nextState
        newState = True

    def toggleArrow(self, onOffValue: bool):

        if onOffValue:
            dpiClockNBlock.arrowOn()
        else:
            dpiClockNBlock.arrowOff()

