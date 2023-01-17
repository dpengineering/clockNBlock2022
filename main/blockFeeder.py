#      ******************************************************************
#      *                                                                *
#      *                       Block Feeder Object                      *
#      *                                                                *
#      *            Arnav Wadhwa                   12/08/2022           *
#      *                                                                *
#      ******************************************************************

# To import from the other folders in project
import sys
sys.path.insert(0, "..")

from DPi_ClockNBlock_Python.DPiClockNBlock import DPiClockNBlock
from time import sleep

# More accurate timer
from timeit import default_timer as timer


BLOCK_SIZE = 31  # block side length in mm


class BlockFeeder:
    """Block Feeder object

    Controls block feeders by reading sensors and shuffling blocks around accordingly

    """
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
        """Constructor for blockFeeder

        Args:
            solenoid_side (int): Number on solenoid board to move the blocks sideways
            solenoid_up (int): Number on solenoid board to move the blocks up
            board_number (int): Which DPi_ClockNBlock board corresponds to this blockFeeder
            solenoidBoard (DPi_Solenoid): Gets the solenoid board object from the robotArm
        """
        self._SOLENOID_SIDE = solenoid_side
        self._SOLENOID_UP = solenoid_up
        self.BOARD_NUMBER = board_number
        self.dpiSolenoid = solenoidBoard
        self.dpiClockNBlock = DPiClockNBlock()

    def setup(self) -> bool:
        """Sets up the blockFeeders so they can be used

        Returns:
            bool: True if successful setup, False otherwise
        """
        self.dpiClockNBlock.setBoardNumber(self.BOARD_NUMBER)
        self.dpiSolenoid.setBoardNumber(0)

        if not self.dpiClockNBlock.initialize():
            # print("Communication with DPiClockNBlock board failed")
            return False

        self.initializeBlockFeeders()

        return True

    def initializeBlockFeeders(self) -> bool:
        """Shuffles a block to the displaying position for the first time

        Returns:
            bool: True if block makes it to the top, otherwise False
        """
        # print("initializing")
        # Check if block already at the top position
        if self.dpiClockNBlock.readExit():
            return True

        # Otherwise, cycle the blocks

        # Turn both solenoids off
        self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
        self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)

        # Wait for them to retract
        sleep(2)

        # If there is a block avaliable send it to ready position

        # Check if block exists and there isn't already a block that is ready to be pushed up
        if self.dpiClockNBlock.readFeed_1() and not self.dpiClockNBlock.readFeed_2():
            # Push the block over
            self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, True)

            # Wait for the block to be pushed over
            while not self.dpiClockNBlock.readFeed_2():
                sleep(0.1)

        # Check if block actually made it over
        if self.dpiClockNBlock.readFeed_2():
            # Push the block up
            self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, True)

            # Wait for the block to be at the top
            while not self.dpiClockNBlock.readExit():
                sleep(0.1)

            # Retract the side piston as it is not necessary for it to be pushed over anymore
            self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)

            # Set state machine to the ready state
            self.setState(self._STATE_READY)
            return True
        return False

    def process(self):
        """
        State machine for the blockFeeders
        """
        # print(f"Feeder State: {self.state}, NewState: {self.newState}, Board: {self.BOARD_NUMBER}")

        # Update arrow (on if the feeder isn't full, otherwise off)
        self.dpiClockNBlock.arrowToggle(not self.dpiClockNBlock.readEntrance())

        # Ready State
        #   This means the feeder is displaying a block for the robot to pick up
        # This state doesn't do anything
        # Waits for block to be picked up
        # Changes state to pull piston down
        if self.state == self._STATE_READY:
            if not self.dpiClockNBlock.readExit():
                # print(f"Board: {self.BOARD_NUMBER},block removed")
                self.setState(self._STATE_BLOCK_REMOVED)
                print('Moving on to State block removed')
                return
            return

        # Pulls piston down
        # Waits for it to be completely down
        # Changes state to push block over
        elif self.state == self._STATE_BLOCK_REMOVED:

            # Retract the up piston
            # print(f"Exit: {self.dpiClockNBlock.readExit()}")
            # Check if block is actually gone first
            if self.newState:
                print('Sleeping 5 seconds before dropping piston')
                sleep(5)
                # Testing purposes
                if self.dpiClockNBlock.readExit():
                    print('Misfire, going back to ready')
                    self.setState(self._STATE_READY)
                    return

                self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, False)
                # Starts timer
                self.start = timer()
                self.newState = False
                return

            # Checks if 2.5 seconds have elapsed
            elif timer() - self.start > 2:
                self.setState(self._STATE_FEED2)
                return

        # Pushes block up
        # Waits for block to reach the top
        # Changes state to ready
        elif self.state == self._STATE_FEED1:

            if self.newState:
                # Moves block up
                self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_UP, True)
                self.newState = False
                return

            # Checks if block is at the top
            elif self.dpiClockNBlock.readExit():
                self.setState(self._STATE_READY)
                # Moves side piston over
                self.dpiSolenoid.switchDriverOnOrOff(self._SOLENOID_SIDE, False)
                return
            return

        # Pushes block over
        # Waits for block to reach Feed 2
        # Changes state to push block up
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

        # State does nothing as there are no blocks in the feeder
        # Waits for block to be inputted
        # Changes state to push block over
        elif self.state == self._STATE_IDLE:
            # Wait for a block to be inserted then switch to feed 2
            if self.dpiClockNBlock.readFeed_1():
                self.setState(self._STATE_FEED2)
                return
            return

    def setState(self, nextState: int):
        """Helper function to set the state to a new state"""
        self.state = nextState
        self.newState = True




