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
sys.path.insert(0, "..")

from main.blockFeeder import BlockFeeder


class BlockManager:
    """Block Manager object

    Gives robot arm positions to move to

    """
    # Constants
    _BLOCK_SIZE = 31  # Block size in mm
    _ROBOT_HEAD_WIDTH = 150  # Baseplate of robot head in mm

    def __init__(self,  blockFeeder: BlockFeeder, feederPos: tuple, buildPos: tuple, stackSize = 5):
        """Constructor for blockManagers

        Args:
            blockFeeder (BlockFeeder): blockFeeder object that corresponds to the block manager
            feederPos (tuple): Feeder location in polar coordinates
            buildPos (tuple): Build site location in polar coordinates
            stackSize (int): Optional height and width of stack
        """
        self.radianOffset = .2
        self.feederPos = feederPos
        self.buildPos = buildPos
        self.MINIMUM_MOVING_HEIGHT = 100  # feederPos[2] + self._BLOCK_SIZE * 6
        self.blockFeeder = blockFeeder
        self.blockPositions = self.generateBlockPlacements(buildPos, stackSize)
        self.blockToPlace = 0

    def getNextBlock(self, currentPos: tuple):
        """Gets the next block

        Args:
            currentPos (tuple): Current position of robot arm in polar coordinates

        Returns:
            list: List of waypoints (tuple) to move the robot to
            tuple: Final position to move, used to check completion of robot's state
        """
        # The head is fairly large so we need a larger radian offset.
        waypointList, target = self.pathToTargetSide(currentPos, self.feederPos, self.radianOffset + 0.1)

        return waypointList, target

    def placeBlock(self, currentPos: tuple, hourPos: float):
        """Gives positions to place block

        Args:
            currentPos (tuple): Current position of robot arm in polar coordinates
            hourPos (float): Used to check it the hour hand is in the way of the building site
                Important to check so the robot does not crash into the hour hand

        Returns:
            list: List of waypoints (tuple) to move the robot to
            tuple: Final position to move, used to check completion of robot's state
        """
        if self.blockToPlace == len(self.blockPositions):
            return False
        if self.hourBlocking(hourPos):
            # print('going Pathside')
            waypointList, target = self.pathToTargetSide(currentPos, self.blockPositions[self.blockToPlace], self.radianOffset)
        else:
            waypointList, target = self.pathToTarget(currentPos, self.blockPositions[self.blockToPlace], self._BLOCK_SIZE)
        self.blockToPlace += 1
        return waypointList, target

    def pathToTarget(self, currentPos: tuple, target: tuple, offset: float):
        """Helper function to generate the path the robot takes to a target position (With radius offset)

        Args:
            currentPos (tuple): Current position of robot arm in polar coordinates
            target (tuple): Final position the robot moves to
            offset (float): How far away from final position we want to move down
                This is so the robot does not crash into potentially stacked blocks

        Returns:
            list: List of waypoints (tuple) to move the robot to
            tuple: Final position to move, used to check completion of robot's state
        """
        movingPath = []
        targetR, targetTheta, targetZ = target
        # If we are too low, bring the robot up to over the working height.
        if currentPos[2] < self.MINIMUM_MOVING_HEIGHT:
            waypoint = currentPos[0], currentPos[1], self.MINIMUM_MOVING_HEIGHT
            currentPos = waypoint
            movingPath.append(waypoint)

        # Add actual moving points:
        # Go next to point and hover above
        waypoint = targetR - offset, targetTheta, currentPos[2]
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

    def pathToTargetSide(self, currentPos: tuple, target: tuple, offset: float):
        """Helper function to generate the path the robot takes to a target position (With radian offset)

        Args:
            currentPos (tuple): Current position of robot arm in polar coordinates
            target (tuple): Final position the robot moves to
            offset (float): How far away from final position we want to move down
                This is so the robot does not crash into potentially stacked blocks

        Returns:
            list: List of waypoints (tuple) to move the robot to
            tuple: Final position to move, used to check completion of robot's state
        """
        movingPath = []
        targetR, targetTheta, targetZ = target
        # If we are too low, bring the robot up to over the working height.
        if currentPos[2] < self.MINIMUM_MOVING_HEIGHT:
            waypoint = currentPos[0], currentPos[1], self.MINIMUM_MOVING_HEIGHT
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

        # Generates the list of positions that we want to place blocks at
        # Enter base location as a tuple of (r, theta, z)

    def generateBlockPlacements(self, baseLocation: tuple, stackSize: int):
        """Helper function to generate the list of where to place each individual block

        Args:
            baseLocation (tuple): The location of the build site
            stackSize (int): How high and wide the stack is

        Returns:
            list: Where to place individual blocks
        """

        placements = []

        r, theta, z = baseLocation

        # Our r, theta, z will be the middle block on the first layer.
        # This location will be where the first block we place is. Gets updated per layer we insert
        initialPos = (r + stackSize / 2 * self._BLOCK_SIZE, theta, z)

        # Build our list:
        for layer in range(1, stackSize + 1):
            for block in range(stackSize - layer + 1):
                pos = initialPos[0] - (self._BLOCK_SIZE + 2) * block, initialPos[1], initialPos[2]
                placements.append(pos)

            # Find first block on next row:
            r, theta, z = initialPos[0] - self._BLOCK_SIZE / 2, initialPos[1], initialPos[2] + self._BLOCK_SIZE + 2
            initialPos = (r, theta, z)

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
        feedPos = (self.feederPos[1] + 2*math.pi) % (2*math.pi)
        buildPos = (self.buildPos[1] + 2*math.pi) % (2*math.pi)
        minutePos = (minutePos + 2 * math.pi) % (2 * math.pi)

        # Find angle between minute hand and the locations for the feeder and building site
        distFeed = abs(feedPos - minutePos)
        distBuild = abs(buildPos - minutePos)

        # Edge case handler to make sure that we are choosing the minor arc
        if distFeed > math.pi:
            distFeed = 2*math.pi - distFeed

        if distBuild > math.pi:
            distBuild = 2*math.pi - distBuild

        # print(f"distFeed: {distFeed}, distBuild: {distBuild}")

        # Checks if the robot arm is too close to each build site
        if distFeed < 0.6 or distBuild < 0.6:

            self.resetStack()
            return False

        # Block feeder is not in ready state
        if not self.blockFeeder.state == 0:
            return False

        # Check if stack is complete
        if self.blockToPlace == len(self.blockPositions):
            return False

        return True

    def resetStack(self):
        self.blockToPlace = 0

    def hourBlocking(self, hourPos: float):
        """Helper function to check if the hour hand is too close to a feeder or build location

        Args:
            hourPos (float): Position of hour hand in radians
                Important so that the robot does not crash into the hour hand when picking up and stacking blocks

        Returns:
            bool: True if hour hand is too close is ready, False otherwise
        """
        # Shift range from 0 to 2pi because it makes the math easier
        feedPos = (self.feederPos[1] + 2*math.pi) % (2*math.pi)
        buildPos = (self.buildPos[1] + 2*math.pi) % (2*math.pi)
        hourPos = (hourPos + 2*math.pi) % (2*math.pi)

        # Find angle between hour hand and the locations for the feeder and building site
        distFeed = abs(feedPos - hourPos)
        distBuild = abs(buildPos - hourPos)

        # Edge case handler to make sure that we are choosing the minor arc
        if distFeed > math.pi:
            distFeed = 2*math.pi - distFeed

        if distBuild > math.pi:
            distBuild = 2*math.pi - distBuild

        # Checks if the robot arm is too close to each build site
        if distFeed < 0.6 or distBuild < 0.6:
            return True

        return False
