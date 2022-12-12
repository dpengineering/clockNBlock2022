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
    state = 0x00
    newState = False

    # Constants
    _STATE_READY = 0x00
    _STATE_FEED1 = 0x01
    _STATE_PRESENT_BLOCK = 0x02
    _STATE_DISPLAYING_BLOCK = 0x03
    _STATE_IDLE = 0x04

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
        if dpiClockNBlock.readFeed_2():
            return True

        # Otherwise, cycle the blocks
        dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
        dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)

        # If there is a block send it to ready position
        if dpiClockNBlock.readFeed_1():
            dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, True)
            while not dpiClockNBlock.readFeed_2():
                sleep(0.1)
            self.state = 0x00
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
            if not dpiClockNBlock.readFeed_2():
                self.setState(self._STATE_FEED1)
            return

        if self.state == self._STATE_FEED1:
            # Check if we have a block to push over, if not set state to idle
            if not dpiClockNBlock.readFeed_1():
                self.state = self._STATE_IDLE
                return
            # If we haven't pushed over the side piston, do it now
            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, True)
                newState = False
                return
            # Wait for side piston to be fully over, then change state to ready
            if dpiClockNBlock.readFeed_2():
                self.setState(self._STATE_READY)
                return
            return

        if self.state == self._STATE_PRESENT_BLOCK:
            # Check if we have a block at Feed 2, if not set state to _FEED_1
            if not dpiClockNBlock.readFeed_2():
                self.setState(self._STATE_FEED1)
                return
            # Push the block up
            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, True)
                return
            # Wait for block to arrive at the top, then switch state and retract side piston
            if dpiClockNBlock.readExit():
                self.setState(self._STATE_DISPLAYING_BLOCK)
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)
                return
            return

        if self.state == self._STATE_DISPLAYING_BLOCK:
            # Start a timer, doesn't really matter that its before we retract the piston
            start = timer()
            # Nothing to do in this state, so we check if it is over
            if not dpiClockNBlock.readExit() and self.newState:
                # Retract piston
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
                self.newState = False
                return
            else:
                # Check if timer is elapsed then go to FEED_1 state
                if timer() - start >= 2:
                    self.setState(self._STATE_FEED1)
                    return

    def isBLockAvailable(self) -> bool:
        return self.state == self._STATE_READY

    def presentBlock(self) -> bool:

        if not self.isBLockAvailable():
            return False
        else:
            self.setState(self._STATE_PRESENT_BLOCK)
            return True

    def setState(self, nextState: int):
        self.state = nextState
        newState = True

    def toggleArrow(self, onOffValue: bool):

        if onOffValue:
            dpiClockNBlock.arrowOn()
        else:
            dpiClockNBlock.arrowOff()

