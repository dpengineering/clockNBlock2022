import time
from time import sleep
from DPi_ClockNBlock_Python.DPiClockNBlock import DPiClockNBlock


class BlockFeeder:

    # States
    _STATE_READY         = 0
    _STATE_BLOCK_REMOVED = 1
    _STATE_PUSH_OVER     = 2
    _STATE_PUSH_UP       = 3
    _STATE_IDLE          = 4

    def __init__(self, feederLocation, solenoidNumbers, dpiClockNBlockNumber, dpiSolenoid):
        self.feederLocation = feederLocation
        self.sidePiston = solenoidNumbers[0]
        self.upPiston = solenoidNumbers[1]
        self.dpiClockNBlock = DPiClockNBlock()
        self.dpiClockNBlock.setBoardNumber(dpiClockNBlockNumber)
        self.dpiSolenoid = dpiSolenoid

        if not self.dpiClockNBlock.initialize():
            raise Exception(f"ClockNBlock initialization failed {dpiClockNBlockNumber}")

        # Flags
        self.isReadyFlg = False

        # State machine
        self.state = self._STATE_READY
        self.newState = True
        self.start = None

    def setup(self):
        """Sets up block feeder and moves the block to the ready position"""

        # Check top position
        if self.dpiClockNBlock.readExit():
            self.isReadyFlg = True
            return True

        # Check if there isn't a block
        if not self.dpiClockNBlock.readFeed_1():
            return True

        # Otherwise, cycle the blocks.
        # First turn both solenoids off
        self.dpiSolenoid.switchDriverOnOrOff(self.sidePiston, False)
        self.dpiSolenoid.switchDriverOnOrOff(self.upPiston, False)

        # Wait for them to retract
        sleep(2)

        # Check if a block is ready to be pushed over, and there isn't a block already pushed over
        if self.dpiClockNBlock.readFeed_1() and not self.dpiClockNBlock.readFeed_2():
            # Push the block over
            self.dpiSolenoid.switchDriverOnOrOff(self.sidePiston, True)

            # Wait for the block to be pushed over
            while not self.dpiClockNBlock.readFeed_2():
                sleep(0.1)

        # Check if block actually made it
        if self.dpiClockNBlock.readFeed_2():
            # Push the block up
            self.dpiSolenoid.switchDriverOnOrOff(self.upPiston, True)

            # Wait for the block to be at the top
            while not self.dpiClockNBlock.readExit():
                sleep(0.1)

            # Retract the side piston as it is not necessary for it to be pushed over anymore
            self.dpiSolenoid.switchDriverOnOrOff(self.sidePiston, False)

            # Set ready flag
            self.isReadyFlg = True

            # Set state machine to the ready state
            self.setState(self._STATE_READY)
            return True

        return False


    def process(self, minuteHandPosition=None):


        self.dpiClockNBlock.toggleArrow(not self.dpiClockNBlock.readEntrance())

        # Update the ready flag
        #   The if else statement is for testing purposes
        if minuteHandPosition is not None:
            self.updateReadyFlg(minuteHandPosition)
        else:
            if self.state == self._STATE_READY:
                self.isReadyFlg = True

        # State machine
        # This state just waits for the block to be removed
        if self.state == self._STATE_READY:
            if not self.dpiClockNBlock.readExit():
                self.setState(self._STATE_BLOCK_REMOVED)
                return

        if self.state == self._STATE_BLOCK_REMOVED:
            if self.newState:
                if self.dpiClockNBlock.readExit():
                    self.setState(self._STATE_READY)

                # Pull piston down
                self.dpiSolenoid.switchDriverOnOrOff(self.upPiston, False)
                self.start = time.time()
                self.newState = False
                return

            if time.time() - self.start > 1.5:
                self.setState(self._STATE_PUSH_OVER)
                return

        if self.state == self._STATE_PUSH_OVER:
            if self.newState:
                # Check if we have a block at feed 1, if not set to idle
                if not self.dpiClockNBlock.readFeed_1():
                    self.setState(self._STATE_IDLE)
                    self.dpiClockNBlock.blinkArrow()
                    return

                # Push the block over
                self.dpiSolenoid.switchDriverOnOrOff(self.sidePiston, True)
                self.newState = False
                return

            # wait for block to arrive
            if self.dpiClockNBlock.readFeed_2():
                self.setState(self._STATE_PUSH_UP)
                return

        if self.state == self._STATE_PUSH_UP:
            if self.newState:
                # Push the block up
                self.dpiSolenoid.switchDriverOnOrOff(self.upPiston, True)
                self.newState = False
                return

            # wait for block to arrive
            if self.dpiClockNBlock.readExit():
                self.dpiSolenoid.switchDriverOnOrOff(self.sidePiston, False)
                self.setState(self._STATE_READY)
                return

        if self.state == self._STATE_IDLE:
            if self.newState:
                self.dpiClockNBlock.blinkArrow(True, 200)
                self.newState = False
                return
            # wait for block
            if self.dpiClockNBlock.readFeed_1():
                self.dpiClockNBlock.blinkArrow(False)
                self.setState(self._STATE_PUSH_OVER)
                return

            return


    def setState(self, newState):
        self.state = newState
        self.newState = True

    def updateReadyFlg(self, minuteHandPosition: float):
        if self.state == self._STATE_READY:
            self.isReadyFlg = True

        feederTheta = self.feederLocation[1]

        if abs(minuteHandPosition - feederTheta) < 30:
            self.isReadyFlg = False





