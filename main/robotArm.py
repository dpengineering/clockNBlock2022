#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *      Arnav Wadhwa, Brian Vesper           12/03/2022           *
#      *                                                                *
#      ******************************************************************

import math
import numpy as np

# More accurate timer
from timeit import default_timer as timer

import sys
sys.path.insert(0, '..')

from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiSolenoid import DPiSolenoid
from main.blockManager import BlockManager
from main.blockFeeder import BlockFeeder
from main.hands import Hands


class RobotArm:
    """Robot arm object
    Controls robot arm
    Also stores solenoid board and locations, objects for feeders and build sites
    """
    # Constants go here

    dpiRobot = DPiRobot()
    dpiSolenoid = DPiSolenoid()
    hands = Hands()
    MAGNET_SOLENOID = 0
    ROTATING_SOLENOID = 0

    state = 0
    newState = True

    currentManager = 0

    STATE_GET_BLOCK =    0
    STATE_PICKUP_BLOCK = 1
    STATE_MOVE_UP =      2
    STATE_PLACE_BLOCK =  3
    STATE_WAITING =      4

    MINIMUM_Z = 100
    speed = 140

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
    # blockFeeders = [blockFeeder0, blockFeeder1, blockFeeder2] # Removed feeder 3 until the structure is rotated

    NUM_BLOCK_FEEDERS = len(blockFeeders)

    # Locations for all the block feeders
    feederLocations = [(345, -0.906, -65), (342, -2.500, -65), (346, 2.24, -67), (343, 0.663, -63)]

    # Locations for all the build locations
    # Note: Currently the third build Location  is closer to the center
    #   This is because the robot arms crash into the structure that houses the robot
    #   We will also need to make it so the third buildLocation will never path in from the side
    buildLocations = [(355, -0.134, -42), (409, -1.696, -42), (416, 2.998, -42), (350, 1.437, -42)]

    # Sets how high the stack of blocks will be
    stackSize = 5
    blockManagers = []
    for i in range(NUM_BLOCK_FEEDERS):
        blockManagers.append(BlockManager(blockFeeders[i], feederLocations[i], buildLocations[i], stackSize))

    def __init__(self, magnetSolenoid: int, rotatingSolenoid: int):
        """ Constructor for RobotArm
        Args:
            magnetSolenoid (int): Solenoid number to extend and retracts the magnet
            rotatingSolenoid (int): Solenoid number to rotate blocks
        """
        self.target = -1, -1, -1
        self.start = None
        self.MAGNET_SOLENOID = magnetSolenoid
        self.ROTATING_SOLENOID = rotatingSolenoid
        self.rotationPosition = False

    def setup(self) -> bool:

        """Sets up the robot arm
        Returns:
            bool: True on success, otherwise False
        """

        # Sets the board numbers for the robot and solenoid board
        self.dpiRobot.setBoardNumber(0)
        self.dpiSolenoid.setBoardNumber(0)

        # initializes robot
        if not self.dpiRobot.initialize():
            # print("Communication with the DPiRobot board failed.")
            return False

        # initializes solenoid board
        if not self.dpiSolenoid.initialize():
            # print("Communication with the DPiSolenoid board failed.")
            return False

        # Homes robot
        if not self.dpiRobot.homeRobot(True):
            # print("Homing failed.")
            return False

        # Sets first state
        self.rotateBlock()
        self.setState(self.STATE_GET_BLOCK)
        # print(f'Done homing robot, State: {self.state}, newState: {self.newState}')
        return True

    def process(self, minutePos: float, hourPos: float):
        """State machine for Robot arm
        Args:
            minutePos (float): Position of clock's minute hand
            hourPos (float): Position of clock's hour hand
        These are necessary to choose the next blockManager
        And check see if we need to move in from the side to avoid crashing into the hour hand
        Returns:
            none
        """
        # Setup for state machine
        currentPos = self.getPositionRadians()
        # print(f'State: {self.state}, newState: {self.newState}, robotStatus: {self.dpiRobot.getRobotStatus()}')
        # print(f'robot pos: {currentPos}')
        # print(f"Clock: {minutePos}, Robot theta: {currentPos[1]}")
        # print(f'Robot state: {self.state}, {self.newState}')

        # Gets a block by grabbing a list of waypoints from the block manager then going to the waypoints
        # Waits for the movement to finish
        # Changes state to pick up the block
        if self.state == self.STATE_GET_BLOCK:
            if self.newState:
                if not self.chooseNextManager(minutePos):
                    self.setState(self.STATE_WAITING)
                    return
                positionList, self.target = self.blockManagers[self.currentManager].getNextBlock(currentPos)
                self.queueWaypoints(positionList, currentPos, self.speed)
                self.newState = False
                # print(f"R: {self.target[0]}, theta: {self.target[1]}, z: {self.target[2]}")
                # Sends the pointer hand to the place where the robot is picking a block up
                self.hands.setSpeed(self.hands.POINTER, self.hands.POINTER_MAX_SPEED)

                # The + 0.11 for position is necessary because otherwise the hand is offset by a bunch
                self.hands.moveToPosRadians(self.hands.POINTER, self.target[1] + 0.11)

                return

            # If our current position is at the block feeder, we should grab this block:
            elif self.isAtLocation(self.target):
                # print(f"position: {self.hands.getPositionRadians()}")
                self.setState(self.STATE_PICKUP_BLOCK)
                return

        # Picks up block and starts timer
        # Waits 0.5 seconds for the robot to actually pick up the block
        # Changes state to rotate block
        elif self.state == self.STATE_PICKUP_BLOCK:
            if self.newState:
                self.dpiSolenoid.switchDriverOnOrOff(self.MAGNET_SOLENOID, True)
                self.start = timer()
                self.newState = False
                # print("move up")
                return

            # Wait for robot arm to have picked up the block, then move robot arm up so we can rotate it
            elif timer() - self.start > 0.5:
                self.setState(self.STATE_MOVE_UP)
                return

        # This state is necessary because we need to rotate the block
        # Moves the robot up to pull the block out of the feeder
        # Waits for robot to finish move
        # Rotates block and changes state to place the block
        elif self.state == self.STATE_MOVE_UP:
            if self.newState:
                # print("moving up")
                self.target = currentPos[0], currentPos[1], 100
                self.moveToPosRadians(self.target, self.speed)
                self.newState = False
                return

            # elif self.isAtLocation(self.target):
            elif self.isAtLocation(self.target):
                # print("rotating solenoid")
                self.rotateBlock()
                self.setState(self.STATE_PLACE_BLOCK)

                return

        # Stacks block by grabbing a list of waypoints from blockManager
        # Waits for the block to be at the location
        # Drops block and changes state to get another block
        elif self.state == self.STATE_PLACE_BLOCK:

            if self.newState:
                # print("moving to place block position")
                positionList, self.target = self.blockManagers[self.currentManager].placeBlock(currentPos)
                # Make sure stack isn't full, if it is just drop the block
                if type(positionList) == bool and not positionList:
                    self.dpiSolenoid.switchDriverOnOrOff(self.MAGNET_SOLENOID, False)
                    self.setState(self.STATE_GET_BLOCK)
                    
                self.queueWaypoints(positionList, currentPos, self.speed)
                self.newState = False
                # print(f"R: {self.target[0]}, theta: {self.target[1]}, z: {self.target[2]}")
                # Sends the pointer hand to the place where the robot is picking a block up
                self.hands.setSpeed(self.hands.POINTER, self.hands.POINTER_MAX_SPEED)
                self.hands.moveToPosRadians(self.hands.POINTER, self.target[1] + 0.11)
                return

            # Check if we are at the location, drop the block
            # elif self.isAtLocation(self.target):
            elif self.isAtLocation(self.target):
                # print("dropping block")
                # print(f"position: {self.hands.getPositionRadians()}")
                self.dpiSolenoid.switchDriverOnOrOff(self.MAGNET_SOLENOID, False)
                self.setState(self.STATE_GET_BLOCK)
                return

        # Re-homes robot if there is nowhere for it to go
        # This will take a while and interrupt our state machine
        # But is helpful to rehome the robot incase it loses steps
        # Waits for a manager to be free
        # Changes state to get block
        # Note: This will call choose next manager which will set the feeder to the next available one
        #   Then it chooses next manager again in the get block state
        #   This is okay because we will just skip one free feeder
        elif self.state == self.STATE_WAITING:
            if self.newState:
                # print("homing Robot")
                self.dpiRobot.homeRobot(True)
                self.hands.Idle = True
                self.newState = False
                return

            if self.chooseNextManager(minutePos):
                self.hands.Idle = False
                self.setState(self.STATE_GET_BLOCK)

    # ---------------------------------------------------------------------------------
    #                                 Helper functions
    # ---------------------------------------------------------------------------------
    def cartesianToPolar(self, position: tuple):
        """Helper function to change cartesian coordinates to polar
        Args:
            position (tuple): Current robot position in cartesian plane
        Returns:
            r, theta, z (tuple (float)): Returns the polar coordinates that correspond to the cartesian coordinates
        """
        x, y, z = position
        # Convert to Polar Coords
        r = math.sqrt(x ** 2 + y ** 2)
        theta = math.atan2(y, x)
        return r, theta, z

    def polarToCartesian(self, position: tuple):
        """Helper function to change polar coordinates to cartesian

        Args:
            position (tuple): Current robot position in polar plane
        Returns:
            x, y, z (tuple (float)): Returns the cartesian coordinates that correspond to the polar coordinates
        """
                
        r, theta, z = position
        x = r*math.cos(theta)
        y = r*math.sin(theta)
        return x, y, z

    def moveToPoint(self, position: tuple, speed: int):
        """Helper function to take in a tuple and change it to 3 variables that the dpiRobot can read
        Args:
            position (tuple): Position to move to in cartesian coordinates
            speed (int): How fast we want the robot to move
        Returns:
            none
        """
        x, y, z = position
        return self.dpiRobot.addWaypoint(x, y, z, speed)

    # Enter pass a set of coordinates in radians, and then add waypoint for robot
    def moveToPosRadians(self, position: tuple, speed: int):
        """Helper function to move to a position in radians
        Args:
            position (tuple): Position to move to in polar coordinates
            speed (int): How fast we want the robot to move
        Returns:
            none
        """
        return self.moveToPoint(self.polarToCartesian(position), speed)

    def getPosition(self):
        """Helper function to get robot position in cartesian coordinates
        Returns:
            x, y, z: The cartesian coordinates of where the robot currently is.
                    Also removes the boolean the dpiRobot function gives
        """
        robotPos = self.dpiRobot.getCurrentPosition()
        x, y, z = robotPos[1], robotPos[2], robotPos[3]
        return x, y, z

    def getPositionRadians(self):
        """Helper function to get robot position in polar coordinates
        Returns:
            r, theta, z: Where the robot currently is in polar coordinates
                """
        return self.cartesianToPolar(self.getPosition())

    def setState(self, nextState: int):
        """Helper function to set the robot state
        Returns:
             none
        """
        self.state = nextState
        self.newState = True

    def queueWaypoints(self, waypoints: list, currentPos: tuple, speed: int):
        """Helper function to queue waypoints in a list.
        Args:
            waypoints (list): List of waypoints to queue
            speed (int): How fast to move robot
        Returns:
            none
        """
        # For an actually straight line, non-polar moves
        waypoints.insert(0, currentPos)
        waypoints = self.ensureStraightLine(waypoints)
        self.dpiRobot.bufferWaypointsBeforeStartingToMove(True)
        for point in range(len(waypoints)):
            self.moveToPoint(waypoints[point], speed)
        self.dpiRobot.bufferWaypointsBeforeStartingToMove(False)

    def chooseNextManager(self, minutePos: float):
        """Helper function to choose the next blockManager the robot goes to
        Args:
            minutePos (float): Position of the clock's minute hand in radians
        Returns:
            bool: True if there is an available manager, otherwise False
        """
        nextManager = self.currentManager
        # Checks if the manager is actually ready, if not increments manager
        for i in range(self.NUM_BLOCK_FEEDERS):
            nextManager = (nextManager + 1) % self.NUM_BLOCK_FEEDERS
            if self.blockManagers[nextManager].isReady(minutePos):
                # Sets the current manager to the next available one
                self.currentManager = nextManager
                return True
        # print("No next manager")
        return False

    # This function is necessary because we always have to set the rotation to the value that it is not
    # Since it doesn't matter which way we rotate the block
    def rotateBlock(self):

        """Helper function to rotate block"""

        # print("rotate")
        self.rotationPosition = not self.rotationPosition
        self.dpiSolenoid.switchDriverOnOrOff(self.ROTATING_SOLENOID, self.rotationPosition)

    def isAtLocation(self, target: tuple):
        """Helper function to check if the robot is currently at the target location
        Args:
            target (tuple): target position for robot in polar coordinates
        Returns:
            bool: True if robot is at the location, otherwise False
        """
        r, theta, z = self.getPositionRadians()
        # print(f'Robot r, target r: {r}, {target[0]}, theta, tTtheta: {theta}, {target[1]}, Z, tZ: {z}, {target[2]}')
        if abs(r - target[0]) > 0.5:
            return False
        elif abs(theta - target[1]) > 0.01:  # Arbitrary value should probably change
            return False
        elif abs(z - target[2]) > 0.5:
            return False

        return True and self.dpiRobot.getRobotStatus()[1] == 6

    def ensureStraightLine(self, waypoints: list) -> list:
        """Helper function to split up long moves to a list of short moves.
        Used for the robot to move with more 'authority'.
        This ensures that the robot will travel in a straight line as it does not do so with a long move.
        Check DPi_Robot firmware to see why. Alternatively, google how linear delta arms work.

        This makes the robot move in a straight line for cartesian coordinates. (As in no arcs)

        Args:
            waypoints (list): List of waypoints with possible long moves
        Returns:
            straightWaypoints (list): List of waypoints with long moves broken up
        """

        # Create our list of waypoints to return
        # Also, add our current position to the list
        straightWaypoints = [self.getPosition()]

        # Convert our list of waypoints in polar coordinates to a list in cartesian coordinates

        # Note: this operation is fairly slow because of the nested for loops.
        #   If this moves us in a straight line, it might be worth refactoring
        #   The code to work in cartesian coordinates
        for waypoint in waypoints:
            nextPoint = self.polarToCartesian(waypoint)
            # Calculating the distance between our last point and the next point we need to go to
            distance = abs(math.dist(straightWaypoints[-1], nextPoint))

            # If the distance is greater than 25mm, split the move into many steps
            if distance > 25:
                numSteps = int(distance / 25)
                # Current x, y, z values
                cX, cY, cZ = straightWaypoints[-1]
                # target x, y, z
                tX, tY, tZ = nextPoint

                # Split our move into a bunch of steps
                xSteps = np.linspace(cX, tX, numSteps, False)
                ySteps = np.linspace(cY, tY, numSteps, False)
                zSteps = np.linspace(cZ, tZ, numSteps, False)

                # Add these points to our list
                for j in range(len(xSteps)):
                    straightWaypoints.append((xSteps[j], ySteps[j], zSteps[j]))

            straightWaypoints.append(nextPoint)
        return straightWaypoints
