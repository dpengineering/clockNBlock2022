#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *      Arnav Wadhwa, Brian Vesper           12/03/2022           *
#      *                                                                *
#      ******************************************************************
import sys
sys.path.insert(0, '..')
from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiSolenoid import DPiSolenoid
from main.blockManager import BlockManager
from main.blockFeeder import BlockFeeder

import math

# More accurate timer
from timeit import default_timer as timer


class RobotArm:

    # Constants go here

    dpiRobot = DPiRobot()
    dpiSolenoid = DPiSolenoid()
    MAGNET_SOLENOID = 0
    ROTATING_SOLENOID = 0

    state = 0
    newState = True

    currentManager = -1

    _STATE_GET_BLOCK =    0
    _STATE_PICKUP_BLOCK = 1
    _STATE_MOVE_UP =      2
    _STATE_PLACE_BLOCK =  3

    MINIMUM_Z = 100
    speed = 60

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
    blockFeeder0 = BlockFeeder(_BLOCK_FEEDER0__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER0__SECOND_PISTON__DRIVER_NUM, 0, dpiSolenoid)
    blockFeeder1 = BlockFeeder(_BLOCK_FEEDER1__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER1__SECOND_PISTON__DRIVER_NUM, 1, dpiSolenoid)
    blockFeeder2 = BlockFeeder(_BLOCK_FEEDER2__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER2__SECOND_PISTON__DRIVER_NUM, 2, dpiSolenoid)
    blockFeeder3 = BlockFeeder(_BLOCK_FEEDER3__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER3__SECOND_PISTON__DRIVER_NUM, 3, dpiSolenoid)

    blockFeeders = [blockFeeder0, blockFeeder1, blockFeeder2, blockFeeder3]

    NUM_BLOCK_FEEDERS = len(blockFeeders)

    # For now, I have just put the locations as an array
    # eventually we would like to just grab this from the locations file
    feederLocations = [(345, -0.906, -63), (342, -2.500, -63), (343, 2.196, -63), (340, 0.661, -63)]

    buildLocations = [(422, -0.134, -42), (419, -1.696, -42), (426, 2.998, -42), (420, 1.437, -42)]
    stackSize = 4
    blockManagers = []
    for i in range(NUM_BLOCK_FEEDERS):
        blockManagers.append(BlockManager(blockFeeders[i], feederLocations[i], buildLocations[i], stackSize))

    def __init__(self, magnetSolenoid: int, rotatingSolenoid: int):
        self.target = -1, -1, -1
        self.start = None
        self.MAGNET_SOLENOID = magnetSolenoid
        self.ROTATING_SOLENOID = rotatingSolenoid
        self.rotationPosition = True

    def setup(self) -> bool:

        self.dpiRobot.setBoardNumber(0)
        self.dpiSolenoid.setBoardNumber(0)

        if not self.dpiRobot.initialize():
            print("Communication with the DPiRobot board failed.")
            return False

        if not self.dpiSolenoid.initialize():
            print("Communication with the DPiSolenoid board failed.")
            return False

        if not self.dpiRobot.homeRobot(True):
            print("Homing failed.")
            return False

        if not self.dpiSolenoid.initialize():
            print("Communication with DPiSolenoid board failed")
            return False

        self.setState(self._STATE_GET_BLOCK)
        self.dpiSolenoid.switchDriverOnOrOff(self.ROTATING_SOLENOID, self.rotationPosition)
        print(f'Done homing robot, State: {self.state}, newState: {self.newState}')
        return True

    def process(self, minutePos: float, hourPos: float):

        currentPos = self.getPositionRadians()
        print(f'robot pos: {currentPos}')
        print(f"Clock: {minutePos}, Robot theta: {currentPos[1]}")
        print(f'Robot state: {self.state}, {self.newState}')
        if self.state == self._STATE_GET_BLOCK:
            if self.newState:
                self.chooseNextManager(minutePos)
                positionList, self.target = self.blockManagers[self.currentManager].getNextBlock(currentPos, hourPos)
                self.queueWaypoints(positionList, self.speed)
                self.newState = False
                return
            # If our current position is at the block feeder, we should grab this block:
            elif self.isAtLocation(self.target):
                self.setState(self._STATE_PICKUP_BLOCK)
                return

        elif self.state == self._STATE_PICKUP_BLOCK:
            if self.newState:
                self.dpiSolenoid.switchDriverOnOrOff(self.MAGNET_SOLENOID, True)
                self.start = timer()
                self.newState = False
                print("move up")
                return
            # Wait for robot arm to have picked up the block, then move robot arm up so we can rotate it
            elif timer() - self.start > 0.5:
                self.setState(self._STATE_MOVE_UP)
                return

        elif self.state == self._STATE_MOVE_UP:
            if self.newState:
                print("moving up")
                self.target = currentPos[0], currentPos[1], 100
                self.moveToPosRadians(self.target, self.speed)
                self.newState = False
                return

            elif self.isAtLocation(self.target):
                print("rotating solenoid")
                self.rotateBlock()
                self.setState(self._STATE_PLACE_BLOCK)
                return

        elif self.state == self._STATE_PLACE_BLOCK:
            if self.newState:
                print("moving to place block position")
                positionList, self.target = self.blockManagers[self.currentManager].placeBlock(currentPos, hourPos)
                # Make sure stack isn't full, if it is just drop the block
                if type(positionList) == bool and not positionList:
                    self.dpiSolenoid.switchDriverOnOrOff(self.MAGNET_SOLENOID, False)
                    self.setState(self._STATE_GET_BLOCK)
                self.queueWaypoints(positionList, self.speed)
                self.newState = False
                return

            # Check if we are at the location, drop the block
            elif self.isAtLocation(self.target):
                print("dropping block")
                self.dpiSolenoid.switchDriverOnOrOff(self.MAGNET_SOLENOID, False)
                self.setState(self._STATE_GET_BLOCK)
                return




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
        return self.dpiRobot.addWaypoint(x, y, z, speed)

    # Enter pass a set of coordinates in radians, and then add waypoint for robot
    def moveToPosRadians(self, waypoint: tuple, speed: int):
        return self.moveToPoint(self.polarToCartesian(waypoint), speed)

    def getPosition(self):
        robotPos = self.dpiRobot.getCurrentPosition()
        x, y, z = robotPos[1], robotPos[2], robotPos[3]
        return x, y, z

    def getPositionRadians(self):
        return self.cartesianToPolar(self.getPosition())

    def setState(self, nextState: int):
        self.state = nextState
        self.newState = True

    def queueWaypoints(self, waypoints: list, speed: int):
        self.dpiRobot.bufferWaypointsBeforeStartingToMove(True)
        for point in range(len(waypoints)):
            self.moveToPosRadians(waypoints[point], speed)
        self.dpiRobot.bufferWaypointsBeforeStartingToMove(False)

    def chooseNextManager(self, clockPos):
        nextManager = (self.currentManager + 1) % 4
        while not self.blockManagers[nextManager].isReady(clockPos):
            nextManager = (nextManager + 1) % 4

        self.currentManager = nextManager

    def rotateBlock(self):
        print("rotate")
        self.rotationPosition = not self.rotationPosition
        self.dpiSolenoid.switchDriverOnOrOff(self.ROTATING_SOLENOID, self.rotationPosition)

    def isAtLocation(self, target: tuple):
        pos = self.getPositionRadians()
        if abs(pos[0] - target[0]) > 1:
            return False
        elif abs(pos[1] - target[1]) > 0.05:  # Arbitrary value should probably change
            return False
        elif abs(pos[2] - target[2]) > 1:
            return False

        return True


