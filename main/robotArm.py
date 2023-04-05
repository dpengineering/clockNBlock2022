import time
import numpy as np
from dpeaDPi.DPiRobot import DPiRobot


class RobotArm:

    # States
    STATE_MOVE_TO_FEEDER     = 0
    STATE_PICKUP_BLOCK       = 1
    STATE_MOVE_TO_BUILD_SITE = 2
    STATE_PLACE_BLOCK        = 3
    STATE_IDLE               = 4

    def __init__(self, dpiSolenoid, magnetSolenoid, rotationSolenoid):

        self.dpiSolenoid = dpiSolenoid
        self.magnetSolenoid = magnetSolenoid
        self.rotationSolenoid = rotationSolenoid

        # Create our dpiRobot object
        self.dpiRobot = DPiRobot()

        # State machine
        self.state = self.STATE_IDLE
        self.newState = False

        # Flags
        self.rotationPositionFlg = False
        self.isHomedFlg = False

        self.initialize()

    def initialize(self):
        """Set up the robot arm"""
        self.dpiRobot.setBoardNumber(0)

        if not self.dpiRobot.initialize():
            raise Exception("Robot arm initialization failed")


