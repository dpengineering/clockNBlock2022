#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *            Arnav Wadhwa                   12/03/2022           *
#      *                                                                *
#      ******************************************************************

from dpeaDPi.DPiRobot import DPiRobot
from time import sleep

# Constants go here

dpiRobot = DPiRobot()


class RobotArm:

    def __init__(self):
        pass

    def setup(self):

        dpiRobot.setBoardNumber(0)

        if not dpiRobot.initialize():
            print("Communication with the DPiRobot board failed.")
            return

        if not dpiRobot.homeRobot(True):
            print("Homing failed.")
            return

