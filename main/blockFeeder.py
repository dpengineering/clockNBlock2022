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

# Constants
dpiClockNBlock = DPiClockNBlock()
dpiSolenoid = DPiSolenoid()


class BlockFeeder:

    _SOLENOID_UP = 0
    SOLENOID_SIDE = 0
    BOARD_NUMBER = 0

    def __init__(self, solenoid_side: int, solenoid_up: int, board_number: int):
        self.SOLENOID_SIDE = solenoid_side
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

        return

    # To be run while everything is homing
    def initializeBlockFeeders(self) -> bool:

        # Check if block already at the bottom position
        if dpiClockNBlock.readFeed_2():
            return True

        # Otherwise, cycle the blocks
        dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
        dpiSolenoid.switchDriverOnOrOff(self.SOLENOID_SIDE, False)

        # If there is a block send it up
        if dpiClockNBlock.readFeed_1():
            dpiSolenoid.switchDriverOnOrOff(self.SOLENOID_SIDE, True)
            while not dpiClockNBlock.readFeed_2():
                sleep(0.1)
            return True
        return False

    # Returns True if block is displayed.
    # This is for the robot to know if it can pick up a block from this feeder.
    # TODO: Check if all states are accounted for
    #   Also, the switching states might end up being too fast.
    #   i.e. while the up piston is moving down the side piston might fire. Not sure how to check for this
    def process(self) -> bool:

        # Check if arrow needs to be turned on
        if dpiClockNBlock.readEntrance():
            self.toggleArrow(True)
        else:
            self.toggleArrow(False)

        # Check if block is displayed, if so do nothing
        if dpiClockNBlock.readExit():
            self.state = "idle"
            return True

        # Check if block is at Feed 2, if so push it up
        if dpiClockNBlock.readFeed_2():
            # if we can read a block at Feed_2, it means that the up piston must be down
            dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, True)
            # Also, the side piston must be activated
            dpiSolenoid.switchDriverOnOrOff(self.SOLENOID_SIDE, False)
            self.state = "up"
            return False

        if dpiClockNBlock.readFeed_1() and self.state == "idle":
            # Pull the up piston down
            dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
            self.state = "down"
            return False

        if dpiClockNBlock.readFeed_1() and self.state == "down":
            # Push the block over
            dpiSolenoid.switchDriverOnOrOff(self.SOLENOID_SIDE, True)
            self.state = "over"
            return False

        if not dpiClockNBlock.readFeed_1():
            # We are waiting for a block
            dpiSolenoid.switchDriverOnOrOff(self.SOLENOID_SIDE, False)
            dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
            self.state = "idle"
            return False

    def toggleArrow(self, onOffValue: bool):

        if onOffValue:
            dpiClockNBlock.arrowOn()
        else:
            dpiClockNBlock.arrowOff()

