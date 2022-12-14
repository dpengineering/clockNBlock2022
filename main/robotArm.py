#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *      Arnav Wadhwa, Brian Vesper           12/03/2022           *
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

    _STATE_READY = 0
    _STATE_MOVE = 1
    _STATE_GRAB = 2
    _STATE_RELEASE = 3

    speed = 40

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

    #State machine for arm. Goes back to ready between each state both to get new action but also to show block manager it has completed its own action.
    def process(self):
        #Checks if block manager has an action ready. If it does changes state to excute action.
        if self.state == self._STATE_READY:
            if blockManager.actionAvailable():
                self.setState(blockManager.getNextState())
                blockManager.cycleAction()
            return

        #Gets next position from block manager and then moves there. Changes state once move is complete
        if self.state == self._STATE_MOVE:
            if self.newState:
                x,y,z = blockManager.getNextPos()
                dpiRobot.addWaypoint(x,y,z, self.speed)
                self.newState = False
            elif dpiRobot.getRobotStatus == dpiRobot.STATE_STOPPED:
                self.setState(self._STATE_READY)
            return

        #Turns magnet on to pick up block and then rotates it. Changes state after solenoid turns on.
        if self.state == self._STATE_GRAB:
            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self.MAGNET_SOLENOID, True)
                dpiSolenoid.switchDriverOnOrOff(self.ROTATING_SOLENOID, True)
                self.newState = False
            else:
                self.setState(self._STATE_READY)
            return

        #Turns magnet off to drop block. Changes state after solenoid turns off.
        if self.state == self._STATE_RELEASE:
            if self.newState:
                dpiSolenoid.switchDriverOnOrOff(self.MAGNET_SOLENOID, False)
                self.newState = False
            else:
                self.setState(self._STATE_READY)
            return




    def cartesianToPolar(self, x: float, y: float):

        # Convert to Polar Coords and rotate plane
        r = math.sqrt(x ** 2 + y ** 2)
        theta = math.atan2(y, x)
        return r, theta

    def polarToCartesian(self, r: float, theta: float):
        x = r*math.cos(theta)
        y = r*math.sin(theta)
        return x, y

    def moveToPoint(self, x, y, z, speed):
        return dpiRobot.addWaypoint(x, y, z, speed)

    def bufferWaypoints(self, flag: bool):
        return dpiRobot.bufferWaypointsBeforeStartingToMove(flag)

    def getPosition(self):
        return dpiRobot.getCurrentPosition()

    def waitWhileMoving(self):
        return dpiRobot.waitWhileRobotIsMoving()

    def setState(self, nextState: int):
        self.state = nextState
        self.newState = True
