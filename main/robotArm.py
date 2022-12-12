#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *            Arnav Wadhwa                   12/03/2022           *
#      *                                                                *
#      ******************************************************************

from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiSolenoid import DPiSolenoid

import math

# Constants go here

dpiRobot = DPiRobot()
dpiSolenoid = DPiSolenoid()


class RobotArm:

    MAGNET_SOLENOID = 0
    ROTATING_SOLENOID = 0

    def __init__(self, magnetSolenoid: int, rotatingSolenoid: int):
        self.MAGNET_SOLENOID = magnetSolenoid
        self.ROTATING_SOLENOID = rotatingSolenoid

    def setup(self) -> bool:

        dpiRobot.setBoardNumber(0)
        dpiSolenoid.setBoardNumber(0)

        if not dpiRobot.initialize():
            print("Communication with the DPiRobot board failed.")
            return False

        if not dpiSolenoid.initialize():
            print("Communication with the DPiSolenoid board failed.")
            return False

        if not dpiRobot.homeRobot(True):
            print("Homing failed.")
            return False

        return True

    def cartesianToPolar(self):

        robotCords = dpiRobot.getCurrentPosition()
        # Get x, y, z from our tuple
        x = robotCords[1]
        y = robotCords[2]
        z = robotCords[3] / 31

        # Convert to Polar Coords and rotate plane
        r = math.sqrt(x ** 2 + y ** 2) / 31
        theta = math.atan2(y, x) - math.pi / 2

        return r, theta, z


