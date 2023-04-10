import constants
from sympy import Plane, Point3D, Polygon


class BuildSite:

    def __init__(self, index, location0, location1):
        # The need for two locations is just to calculate the "slope" of the build site
        # This is necessary since the build sites aren't flat which can cause the robot arm
        # to lose steps while placing a block down
        # Since we are in 3D, we don't have a traditional slope, but our slope can just be the distance
        # in Z over the distance in X and Y.
        self.index = index
        self.location = location0
        # For reference
        self.location1 = location1

        # Locations in cartesian coordinates
        self.locationCartesian = constants.polarToCartesian(self.location)
        self.location1Cartesian = constants.polarToCartesian(self.location1)

        self.slope = self.calculateSlope(location0, location1)

        self.currentBlock = None
        self.blockPlacements = None

        self.intersectionPlane = None

        # Polygon intersection bounds
        self.corner0 = None
        self.corner1 = None
        self.corner2 = None
        self.corner3 = None
        self.intersectionPolygon = None


        # Flags
        self.isReadyFlg = False


    def setup(self):
        # Our setup is fairly simple, we just need to find the block placement list we have
        # and reset our counter to 0
        self.blockPlacements = self.generatePlacementList(constants.placementArrays[self.index], self.location)
        self.currentBlock = 0
        self.isReadyFlg = True
        point0 = Point3D(self.locationCartesian)
        point1 = Point3D(self.location1Cartesian)
        point2 = Point3D(constants.polarToCartesian(self.blockPlacements[-1]))
        self.intersectionPlane = Plane(point0, point1, point2)

        # Polygon intersection bounds
        # Lower corners
        # Closest to center
        self.corner0 = Point3D(self.locationCartesian[0] - constants.robotHeadWidth, self.locationCartesian[1], self.locationCartesian[2])
        # Farthest from center
        self.corner1 = Point3D(self.location1Cartesian[0] + constants.robotHeadWidth, self.location1Cartesian[1], self.location1Cartesian[2])

        # Upper corners
        # Z Value
        zHeight = constants.polarToCartesian(self.blockPlacements[self.currentBlock][2]) + 10  # Height of the highest block placed + 10mm
        # Closest to center
        self.corner2 = Point3D(self.locationCartesian[0] - constants.robotHeadWidth, self.locationCartesian[1], zHeight)
        # Farthest from center
        self.corner3 = Point3D(self.location1Cartesian[0] + constants.robotHeadWidth, self.location1Cartesian, zHeight)

        self.intersectionPolygon = Polygon(self.corner0, self.corner1, self.corner2, self.corner3)


    def process(self, minuteHandPosition):
        # The state machine for this object is just checking if it is ready.
        self.updateReadyFlg(minuteHandPosition)

        self.updatePolygon()


    def calculateSlope(self, location0, location1):
        # Take change all 3 axes
        deltaR = location1[0] - location0[0]
        deltaZ = location1[2] - location0[2]

        # calculate and return slope
        return deltaZ / deltaR


    def generatePlacementList(self, placementArray, startLocation, blockSpacing=1):
        """Creates a list of where to place blocks dependent on an array passed in.
            Each 1 in the array will denote where to place a block and the 0's are empty space
            Since we would like to have some rows "offset" from each other, the first column will be reserved
            For setting the offset of the next row in mm. The origin will be at the bottom - back corner
            of the stack and the positions will be calculated from there.
            blockSpacing (int): How far the blocks get placed from each other in mm
            """
        placements = []
        blockSizeWithSpacing = constants.blockSize + blockSpacing
        numRows = len(placementArray)
        colSize = len(placementArray[1]) - 1
        for rowIdx, row in enumerate(placementArray):
            currentOrigin = startLocation
            for colIdx, value in enumerate(row):
                # If we are at the first column, offset by the offset value
                if colIdx == 0:
                    currentOrigin = currentOrigin[0] + value, currentOrigin[1], currentOrigin[2]
                elif value:
                    # Calculate the position we need to place our block
                    currentRow = numRows - rowIdx - 1
                    currentCol = -colSize + colIdx - 1
                    zPos = currentRow * blockSizeWithSpacing + currentOrigin[2] + currentCol * self.slope * blockSizeWithSpacing
                    rPos = currentCol * blockSizeWithSpacing + currentOrigin[0]
                    placements.insert(0, (rPos, currentOrigin[1], zPos))

        return placements

    def updateReadyFlg(self, minuteHandPosition: float):
        if self.currentBlock < len(self.blockPlacements):
            self.isReadyFlg = True

        # If the minute hand is within 30 degrees of the build site, we are not ready
        if abs(self.location[1] - minuteHandPosition) < 30:
            self.isReadyFlg = False
            self.currentBlock = 0
            return

        return

    def updatePolygon(self):
        # Calculate the Z height

        if self.currentBlock != 0:
            lastBlockPlaced = self.currentBlock - 1
        else:
            lastBlockPlaced = self.currentBlock

        zHeight = self.blockPlacements[lastBlockPlaced][2] + 10

        # Check if zHeight is within 10mm of the last Z height
        # The last Z height is found by looking at corner2

        previousZHeight = self.corner2.z

        zHeight = constants.polarToCartesian(self.blockPlacements[lastBlockPlaced][2]) + 10

        if abs(zHeight - previousZHeight) > 10:
            self.corner2.z = zHeight
            self.corner3.z = zHeight
            self.intersectionPolygon = Polygon(self.corner0, self.corner1, self.corner2, self.corner3)

        return





