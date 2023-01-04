#      ******************************************************************
#      *                                                                *
#      *                        Block Manager                           *
#      *                                                                *
#      *     Brian Vesper, Arnav Wadhwa            12/15/2022           *
#      *                                                                *
#      ******************************************************************
import math

from main.blockFeeder import BlockFeeder


class BlockManager:

    # Constants
    _BLOCK_SIZE = 31  # Block size in mm
    _ROBOT_HEAD_WIDTH = 150  # Baseplate of robot head in mm

    def __init__(self,  blockFeeder: BlockFeeder, feederPos: tuple, buildPos: tuple, stackSize = 5):
        self.radianOffset = .2
        self.feederPos = feederPos
        self.buildPos = buildPos
        self.MINIMUM_MOVING_HEIGHT = 100  # feederPos[2] + self._BLOCK_SIZE * 6
        self.blockFeeder = blockFeeder
        self.blockPositions = self.generateBlockPlacements(buildPos, stackSize)
        self.blockToPlace = 0

    def getNextBlock(self, currentPos: tuple, hourPos: float):
        if self.hourBlocking(hourPos):
            print("going pathSide")
            list, target = self.pathToTargetSide(currentPos, self.feederPos, self.radianOffset)
        else:
            list, target = self.pathToTarget(currentPos, self.feederPos, self._ROBOT_HEAD_WIDTH)
        return list, target

    def placeBlock(self, currentPos: tuple, hourPos: float):
        if self.blockToPlace == len(self.blockPositions):
            return False
        if self.hourBlocking(hourPos):
            print('going Pathside')
            path, target = self.pathToTarget(currentPos, self.blockPositions[self.blockToPlace], self.radianOffset)
        else:
            path, target = self.pathToTarget(currentPos, self.blockPositions[self.blockToPlace], self._BLOCK_SIZE)
        self.blockToPlace += 1
        return path, target

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
        waypoint = currentPos[0], currentPos[1], targetZ + 10
        movingPath.append(waypoint)
        currentPos = waypoint

        # slide over to point
        waypoint = targetR, targetTheta, currentPos[2]
        movingPath.append(waypoint)


        movingPath.append(target)

        return movingPath, target

        # Enter:
    #   Current position of robot, (r, theta, z)
    #   Target position of robot, (r, theta, z)
    #   Offset of how far to slide over (radius)
    # returns list of waypoints to go to
    def pathToTargetSide(self, currentPos: tuple, target: tuple, offset: float):
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

        #shift range from 0-2pi cuz easier
        feedPos = self.feederPos[1] + math.pi
        buildPos = self.buildPos[1] + math.pi
        clockPos = clockPos + math.pi

        #find angle between
        distFeed = abs(feedPos - clockPos)
        distBuild = abs(buildPos - clockPos)

        #if its the bigger angle change to the smaller one
        if distFeed < math.pi:
            distFeed = 2*math.pi - distFeed

        if distBuild < math.pi:
            distBuild = 2*math.pi - distBuild

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

    def hourBlocking(self, hourPos):

        feedPos = abs(self.feederPos[1])
        buildPos = abs(self.buildPos[1])
        hourPos = abs(hourPos)

        if abs(hourPos - feedPos) < 0.6 or abs(hourPos - buildPos) < 0.6:
            self.resetStack()
            return True

        return False
