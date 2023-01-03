#      ******************************************************************
#      *                                                                *
#      *                        Block Manager                           *
#      *                                                                *
#      *     Brian Vesper, Arnav Wadhwa            12/15/2022           *
#      *                                                                *
#      ******************************************************************
from blockFeeder import BlockFeeder


class BlockManager:

    # Constants
    _BLOCK_SIZE = 31  # Block size in mm
    _ROBOT_HEAD_WIDTH = 150  # Baseplate of robot head in mm

    def __init__(self,  blockFeeder: BlockFeeder, feederPos: tuple, buildPos: tuple, stackSize = 5):
        self.feederPos = feederPos
        self.buildPos = buildPos
        self.MINIMUM_MOVING_HEIGHT = feederPos[2] + self._BLOCK_SIZE * 6
        self.blockFeeder = blockFeeder
        self.blockPositions = self.generateBlockPlacements(buildPos, stackSize)
        self.blockToPlace = 0

    def getNextBlock(self, currentPos: tuple):
        return self.pathToTarget(currentPos, self.feederPos, self._ROBOT_HEAD_WIDTH / 2)

    def placeBlock(self, currentPos: tuple):
        if self.blockToPlace == len(self.blockPositions):
            return False
        path = self.pathToTarget(currentPos, self.blockPositions[self.blockToPlace], self._BLOCK_SIZE)
        self.blockToPlace += 1
        return path

    # Enter:
    #   Current position of robot, (r, theta, z)
    #   Target position of robot, (r, theta, z)
    #   Offset of how far to slide over (radius)
    # returns list of waypoints to go to
    def pathToTarget(self, currentPos: tuple, target: tuple, offset: float):
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
        waypoint = currentPos[0], currentPos[1], targetZ
        movingPath.append(waypoint)
        currentPos = waypoint

        # slide over to point
        movingPath.append(target)

        return movingPath

        # Generates the list of positions that we want to place blocks at
        # Enter base location as a tuple of (r, theta, z)

    def generateBlockPlacements(self, baseLocation: tuple, stackSize: int):

        placements = []

        r, theta, z = baseLocation

        # Our r, theta, z will be the middle block on the first layer.
        # This location will be where the first block we place is. Gets updated per layer we insert
        initialPos = (r + 2 * self._BLOCK_SIZE, theta, z)

        # Build our list:
        for layer in range(1, stackSize + 1):
            for block in range(stackSize - layer + 1):
                pos = initialPos[0] - self._BLOCK_SIZE * block, initialPos[1], initialPos[2]
                placements.append(pos)

            # Find first block on next row:
            r, theta, z = initialPos[0] - self._BLOCK_SIZE / 2, initialPos[1], initialPos[2] + self._BLOCK_SIZE
            initialPos = (r, theta, z)

        return placements

    def isReady(self, clockPos: float) -> bool:

        minPos = self.feederPos[1] + 0.6
        maxPos = self.buildPos[1] - 0.18
        if minPos < clockPos < maxPos:
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


