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

    # Start timer
    start = 0

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
        print("initalizing")
        # Check if block already at the top position
        if dpiClockNBlock.readExit():
            return True

        # Otherwise, cycle the blocks
        dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
        dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)
        sleep(1)
        # If there is a block send it to ready position
        if dpiClockNBlock.readFeed_1() and not dpiClockNBlock.readFeed_2():
            dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, True)
            while not dpiClockNBlock.readFeed_2():
                sleep(0.1)
        if dpiClockNBlock.readFeed_2():
            dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, True)
            while not dpiClockNBlock.readExit():
                sleep(0.1)
            dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)
            self.setState(self._STATE_READY)
            return True
        return False

    def process(self):
        # Check if arrow needs to be turned on
        if dpiClockNBlock.readEntrance():
            self.toggleArrow(False)
        else:
            self.toggleArrow(True)

        if self.state == self._STATE_READY:
            # Check if it is actually ready, if not switch state to block removed
            if not dpiClockNBlock.readExit():
                self.setState(self._STATE_BLOCK_REMOVED)
            return

        elif self.state == self._STATE_BLOCK_REMOVED:

            # Retract the up piston
            print(f"Newstate: {self.newState}")
            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
                self.start = timer()
                print(f"start: {self.start}")
                print("Started timer")
                self.newState = False
                return
            elif timer() - self.start > 2:
                self.setState(self._STATE_FEED2)
                return
            else:
                print(f"start - timer: {self.start - timer()}")

        elif self.state == self._STATE_FEED1:

            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, True)
                self.newState = False
                return
            elif dpiClockNBlock.readExit():
                self.setState(self._STATE_READY)
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)
                return
            return

        elif self.state == self._STATE_FEED2:
            # Check if we have a block at Feed 1, if not set state to idle
            if not dpiClockNBlock.readFeed_1():
                self.setState(self._STATE_IDLE)
                print(f"going to idle, newState: {self.newState}")
                return
            # Push the block over
            print(f"newState: {self.newState}")
            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, True)
                self.newState = False
                return
            # Wait for block to arrive at the side
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
        else:
            print("nothing happening")

    def isBLockAvailable(self) -> bool:
        return self.state == self._STATE_READY

    def setState(self, nextState: int):
        self.state = nextState
        self.newState = True

    def toggleArrow(self, onOffValue: bool):

        if onOffValue:
            dpiClockNBlock.arrowOn()
        else:
            dpiClockNBlock.arrowOff()

