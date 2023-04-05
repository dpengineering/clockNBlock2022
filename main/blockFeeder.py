

class BlockFeeder:
    def __init__(self, feederLocation, solenoidNumbers, dpiClockNBlock):
        self.feederLocation = feederLocation
        self.sidePiston = solenoidNumbers[0]
        self.upPiston = solenoidNumbers[1]
        self.dpiClockNBlock = dpiClockNBlock

        # Flags
        self.isReadyFlg = False
