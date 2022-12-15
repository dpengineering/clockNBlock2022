#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *      Arnav Wadhwa, Brian Vesper           12/03/2022           *
#      *                                                                *
#      ******************************************************************

from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiSolenoid import DPiSolenoid
from blockManager import BlockManager
from blockFeeder import BlockFeeder

import math

# Constants go here

dpiRobot = DPiRobot()
dpiSolenoid = DPiSolenoid()


class RobotArm:

    MAGNET_SOLENOID = 0
    ROTATING_SOLENOID = 0

    state = 0
    newState = False

    _STATE_READY =        0
    _STATE_GET_BLOCK =    1
    _STATE_ROTATE_BLOCK = 2
    _STATE_PLACE_BLOCK =  3

    MINIMUM_Z = 140
    speed = 40
    # pin assignments show how the pistons are wired to the DPiSolenoid board
    #
    _BLOCK_FEEDER0__FIRST_PISTON__DRIVER_NUM = 6
    _BLOCK_FEEDER0__SECOND_PISTON__DRIVER_NUM = 7
    _BLOCK_FEEDER1__FIRST_PISTON__DRIVER_NUM = 4
    _BLOCK_FEEDER1__SECOND_PISTON__DRIVER_NUM = 3
    _BLOCK_FEEDER2__FIRST_PISTON__DRIVER_NUM = 9
    _BLOCK_FEEDER2__SECOND_PISTON__DRIVER_NUM = 8
    _BLOCK_FEEDER3__FIRST_PISTON__DRIVER_NUM = 0
    _BLOCK_FEEDER3__SECOND_PISTON__DRIVER_NUM = 1

    # For the ClockNBlock boards
    blockFeeder0 = BlockFeeder(_BLOCK_FEEDER0__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER0__SECOND_PISTON__DRIVER_NUM, 0)
    blockFeeder1 = BlockFeeder(_BLOCK_FEEDER1__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER1__SECOND_PISTON__DRIVER_NUM, 1)
    blockFeeder2 = BlockFeeder(_BLOCK_FEEDER2__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER2__SECOND_PISTON__DRIVER_NUM, 2)
    blockFeeder3 = BlockFeeder(_BLOCK_FEEDER3__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER3__SECOND_PISTON__DRIVER_NUM, 3)

    blockFeeders = [blockFeeder0, blockFeeder1, blockFeeder2, blockFeeder3]

    NUM_BLOCK_FEEDERS = len(blockFeeders)

    # For now, I have just put the locations as an array
    # eventually we would like to just grab this from the locations file
    # TODO: Train feeder 1 and 2
    feederLocations = [(345, -0.906, -62), (345, -0.906, -62), (345, -0.906, -62), (340, 0.661, -63)]
    # TODO: Retrain the z values to the point where they are actually placing a block
    buildLocations = [(422, -0.134, -44), (419, -1.696, -45), (426, 2.998, -42), (420, 1.437, -42)]
    stackSize = 5
    blockManagers = []
    for i in range(NUM_BLOCK_FEEDERS):
        blockManagers.append(BlockManager(blockFeeders[i], feederLocations[i], buildLocations[i], stackSize))

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
        if self.state == self._STATE_READY:
            # Move out of the way if we haven't done so
            r, theta, z = self.getPositionRadians()
            if z < self.MINIMUM_Z:
                pos = r, theta, self.MINIMUM_Z
                self.moveToPosRadians(pos, self.speed)



    def cartesianToPolar(self, position: tuple):

        x, y, z = position
        # Convert to Polar Coords and rotate plane
        r = math.sqrt(x ** 2 + y ** 2)
        theta = math.atan2(y, x)
        return r, theta, z

    def polarToCartesian(self, position: tuple):

        r, theta, z = position
        x = r*math.cos(theta)
        y = r*math.sin(theta)
        return x, y, z

    def moveToPoint(self, position: tuple, speed: int):
        x, y, z = position
        return dpiRobot.addWaypoint(x, y, z, speed)

    # Enter pass a set of coordinates in radians, and then add waypoint for robot
    def moveToPosRadians(self, waypoint: tuple, speed: int):
        return self.moveToPoint(self.polarToCartesian(waypoint), speed)

    def getPosition(self):
        robotPos = dpiRobot.getCurrentPosition()
        x, y, z = robotPos[1], robotPos[2], robotPos[3]
        return x, y, z

    def getPositionRadians(self):
        return self.cartesianToPolar(self.getPosition())

    def waitWhileMoving(self):
        return dpiRobot.waitWhileRobotIsMoving()

    def setState(self, nextState: int):
        self.state = nextState
        self.newState = True

    def queueWaypoints(self, waypoints: list, speed: int):
        dpiRobot.bufferWaypointsBeforeStartingToMove(True)
        for point in range(len(waypoints)):
            self.moveToPosRadians(waypoints[point], speed)
        dpiRobot.bufferWaypointsBeforeStartingToMove(False)

