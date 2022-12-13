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

    state = 0
    newState = False

    STATE_READY = 0
    STATE_FEED_MOVE = 1
    STATE_GRAB = 2
    STATE_BUILD_MOVE = 3
    STATE_RELEASE = 4
    STATE_IDLE = 5

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

    def process(self):
        pass

    def cartesianToPolar(self, x:float, y:float):
        # Convert to Polar Coords and rotate plane
        r = math.sqrt(x ** 2 + y ** 2)
        theta = math.atan2(y, x)

        return r, theta

    def polarToCartesian(self, r:float, theta:float):
        x = r*math.cos(theta)
        y = r*math.sin(theta)

        return x,y

    def moveToPoint(self, x, y, z, speed):
        return dpiRobot.addWaypoint(x, y, z, speed)

    def bufferWaypoints(self, flag: bool):
        return dpiRobot.bufferWaypointsBeforeStartingToMove(flag)

    def getPosition(self):
        return dpiRobot.getCurrentPosition()

    def waitWhileMoving(self):
        return dpiRobot.waitWhileRobotIsMoving()



