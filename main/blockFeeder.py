from dpeaDPi.DPiClockNBlock import DPiClockNBlock


class BlockFeeder:

    # States
    _STATE_READY         = 0
    _STATE_BLOCK_REMOVED = 1
    _STATE_PUSH_OVER     = 2
    _STATE_PUSH_UP       = 3
    _STATE_IDLE          = 4

    def __init__(self, feederLocation, solenoidNumbers, dpiClockNBlockNumber):
        self.feederLocation = feederLocation
        self.sidePiston = solenoidNumbers[0]
        self.upPiston = solenoidNumbers[1]
        self.dpiClockNBlock = DPiClockNBlock()
        self.dpiClockNBlock.setBoardNumber(dpiClockNBlockNumber)

        # Flags
        self.isReadyFlg = False


