#      ******************************************************************
#      *                                                                *
#      *                        Block Manager                           *
#      *                                                                *
#      *     Brian Vesper, Arnav Wadhwa            12/15/2022           *
#      *                                                                *
#      ******************************************************************
import math

# To import from other folders in project
import sys

import numpy as np

sys.path.insert(0, "..")

from main.blockFeeder import BlockFeeder


class BlockManager:
    """Block Manager object

    Gives robot arm positions to move to

    """
    # Constants
    _BLOCK_SIZE = 30  # Block size in mm
    _ROBOT_HEAD_WIDTH = 160  # Baseplate of robot head in mm

    def __init__(self, blockFeeder: BlockFeeder, feederPos: tuple, buildPos: tuple, managerNumber: int, stackSize=6):
        """Constructor for blockManagers

        Args:
            blockFeeder (BlockFeeder): blockFeeder object that corresponds to the block manager
            feederPos (tuple): Feeder location in polar coordinates
            buildPos (tuple): Build site location in polar coordinates
            managerNumber (int): Manager number to determine which stack we want
        """
        self.radianOffset = .25
        self.feederPos = feederPos
        self.buildPos = buildPos
        self.MINIMUM_MOVING_HEIGHT = -1480.8 + 200  # feederPos[2] + self._BLOCK_SIZE * 6
        self.blockFeeder = blockFeeder
        self.blockPlacementList = self.generateBlockPlacements(buildPos, managerNumber)
        self.blockToPlace = 0

    def getNextBlock(self, currentPos: tuple, minimumZHeight):
        """Gets the next block

        Args:
            currentPos (tuple): Current position of robot arm in polar coordinates

        Returns:
            list: List of waypoints (tuple) to move the robot to
            tuple: Final position to move, used to check completion of robot's state
        """
        # The head is fairly large, so we need a larger radian offset.
        waypointList, target = self.pathToTarget(currentPos, self.feederPos, self.radianOffset + 0.1, minimumZHeight)

        return waypointList, target

    def placeBlock(self, currentPos: tuple):
        """Gives positions to place block

        Args:
            currentPos (tuple): Current position of robot arm in polar coordinates

        Returns:
            list: List of waypoints (tuple) to move the robot to
            tuple: Final position to move, used to check completion of robot's state
        """
        if self.blockToPlace == len(self.blockPlacementList):
            return False

        waypointList, target = self.pathToTarget(currentPos, self.blockPlacementList[self.blockToPlace], self.radianOffset)

        self.blockToPlace += 1
        return waypointList, target

    def pathToTarget(self, currentPos: tuple, target: tuple, offset=.25, minimumZHeight=None):
        """Helper function to generate the path the robot takes to a target position (With radian offset)

        Args:
            currentPos (tuple): Current position of robot arm in polar coordinates
            target (tuple): Final position the robot moves to
            offset (float): How far away from final position we want to move down
                This is so the robot does not crash into potentially stacked blocks
            minimumZHeight(int) or None: The minimum height we should travel so we don't collide with other towers

        Returns:
            list: List of waypoints (tuple) to move the robot to
            tuple: Final position to move, used to check completion of robot's state
        """
        movingPath = []
        targetR, targetTheta, targetZ = target
        # If we are too low, bring the robot up to over the working height.
        if minimumZHeight is not None and minimumZHeight > currentPos[2]:
            waypoint = currentPos[0], currentPos[1], minimumZHeight
            currentPos = waypoint
            movingPath.append(waypoint)

        # Add actual moving points:

        # Go side to point and hover above
        waypoint = targetR, targetTheta - offset, currentPos[2]
        movingPath.append(waypoint)
        currentPos = waypoint

        # Go down to right next to point
        waypoint = currentPos[0], currentPos[1], targetZ + 10

        movingPath.append(waypoint)
        currentPos = waypoint

        # slide over to point
        waypoint = targetR, targetTheta, currentPos[2]
        movingPath.append(waypoint)

        movingPath.append(target)

        return movingPath, target

    def generateBlockPlacements(self, baseLocation: tuple, managerNumber: int):
        """Helper function to generate the list of where to place each individual block

        Args:
            baseLocation (tuple): The location of the build site
            stackSize (int): How high and wide the stack is

        Returns:
            list: Where to place individual blocks
        """

        placements = []

        r, theta, z = baseLocation

        # Using if else statements because python's match case was added in python 3.10
        if managerNumber == 0:
            # Right triangle
            placementArray = ([0, 1, 0, 0, 0, 0, 0],
                              [0, 1, 1, 0, 0, 0, 0],
                              [0, 1, 1, 1, 0, 0, 0],
                              [0, 1, 1, 1, 1, 0, 0],
                              [0, 1, 1, 1, 1, 1, 0],
                              [0, 1, 1, 1, 1, 1, 1])
            placements = self.generatePlacementsFromArray(placementArray)
        elif managerNumber == 1:
            # Funky shape
            placementArray = ([-self._BLOCK_SIZE/2, 0, 0, 0, 1, 0, 0],
                              [0                  , 0, 0, 1, 1, 0, 0],
                              [-self._BLOCK_SIZE/2, 0, 0, 1, 1, 1, 0],
                              [0                  , 0, 1, 1, 1, 1, 0],
                              [0                  , 0, 1, 1, 1, 1, 0],
                              [0                  , 0, 1, 1, 1, 1, 0])
            placements = self.generatePlacementsFromArray(placementArray)
        elif managerNumber == 2:
            # Regular pyramid
            placementArray = ([-self._BLOCK_SIZE/2, 0, 0, 0, 1, 0, 0],
                              [0                  , 0, 0, 1, 1, 0, 0],
                              [-self._BLOCK_SIZE/2, 0, 0, 1, 1, 1, 0],
                              [0                  , 0, 1, 1, 1, 1, 0],
                              [-self._BLOCK_SIZE/2, 0, 1, 1, 1, 1, 1],
                              [0                  , 1, 1, 1, 1, 1, 1])
            placements = self.generatePlacementsFromArray(placementArray)
        elif managerNumber == 3:
            # 2 wide tower. This manager cannot build huge towers
            placementArray = ([-self._BLOCK_SIZE/2, 0, 1, 0, 0, 0, 0],
                              [0                  , 1, 1, 0, 0, 0, 0],
                              [0                  , 1, 1, 0, 0, 0, 0],
                              [0                  , 1, 1, 0, 0, 0, 0],
                              [0                  , 1, 1, 0, 0, 0, 0],
                              [0                  , 1, 1, 0, 0, 0, 0])
            placements = self.generatePlacementsFromArray(placementArray)

        return placements

    def generatePlacementsFromArray(self, placementArray, blockSpacing=1) -> list:
        """Creates a list of where to place blocks dependent on an array passed in.
        Each 1 in the array will denote where to place a block and the 0's are empty space
        Since we would like to have some rows "offset" from each other, the first column will be reserved
        For setting the offset of the next row in mm. The origin will be at the bottom - back corner
        of the stack and the positions will be calculated from there.
        blockSpacing (int): How far the blocks get placed from each other in mm
        """
        placements = []
        blockSizeWithSpacing = self._BLOCK_SIZE + blockSpacing
        numRows = len(placementArray)
        colSize = len(placementArray[1]) - 1
        for rowIdx, row in enumerate(placementArray):
            currentOrigin = self.buildPos
            for colIdx, value in enumerate(row):
                # If we are at the first column, offset by the
                if colIdx == 0:
                    currentOrigin = currentOrigin[0] + value, currentOrigin[1], currentOrigin[2]
                elif value:
                    # Calculate the position we need to place our block
                    zPos = (numRows - rowIdx - 1) * blockSizeWithSpacing + currentOrigin[2]
                    rPos = (-colSize + (colIdx - 1)) * blockSizeWithSpacing + currentOrigin[0]
                    placements.insert(0, (rPos, currentOrigin[1], zPos))

        return placements

    def isReady(self, minutePos: float) -> bool:
        """Helper function to check if a blockFeeder is ready to give a block

        Args:
            minutePos (float): Position of minute hand in radians
                Important so that the robot does not crash into the minute hand when picking up and stacking blocks

        Returns:
            bool: True if currentFeeder is ready, False otherwise
        """
        # print(f"Feed: {self.feederPos[1]}, Build: {self.buildPos[1]}, Clock: {minutePos}")

        # Shift range from 0 to 2pi because it makes the math easier
        feedPos = (self.feederPos[1] + 2 * math.pi) % (2 * math.pi)
        buildPos = (self.buildPos[1] + 2 * math.pi) % (2 * math.pi)
        minutePos = (minutePos + 2 * math.pi) % (2 * math.pi)

        # Find angle between minute hand and the locations for the feeder and building site
        distFeed = abs(feedPos - minutePos)
        distBuild = abs(buildPos - minutePos)

        # Edge case handler to make sure that we are choosing the minor arc
        if distFeed > math.pi:
            distFeed = 2 * math.pi - distFeed

        if distBuild > math.pi:
            distBuild = 2 * math.pi - distBuild

        # print(f"distFeed: {distFeed}, distBuild: {distBuild}")

        # Checks if the robot arm is too close to each build site
        if distFeed < 0.6 or distBuild < 0.6:
            self.resetStack()
            return False

        # Block feeder is not in ready state
        if not self.blockFeeder.state == 0:
            return False

        # Check if stack is complete
        if self.blockToPlace == len(self.blockPlacementList):
            return False

        return True

    def resetStack(self):
        self.blockToPlace = 0
