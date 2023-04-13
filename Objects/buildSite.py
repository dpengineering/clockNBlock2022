import Objects.constants as constants


class BuildSite:

    def __init__(self, index, location0, location1):
        # The need for two locations is just to calculate the "slope" of the build site
        # This is necessary since the build sites aren't flat which can cause the robot arm
        # to lose steps while placing a block down
        # Since we are in 3D, we don't have a traditional slope, but our slope can just be the distance
        # in Z over the distance in X and Y.
        self.index = index
        self.location0 = location0
        self.location1 = location1

        # Locations in cartesian coordinates
        self.location0Cartesian = constants.polarToCartesian(self.location0)
        self.location1Cartesian = constants.polarToCartesian(self.location1)

        self.slope = self.calculateSlope(location0, location1)

        self.currentBlock = None
        self.blockPlacements = None

        # Intersection rectangle in cartesian coordinates
        self.intersectionRectangle = None

        # Flags
        self.isReadyFlg = False


    def setup(self):
        # Our setup is fairly simple, we just need to find the block placement list we have
        # and reset our counter to 0
        self.blockPlacements = self.generatePlacementList(constants.placementArrays[self.index], self.location0)
        self.currentBlock = 0
        self.isReadyFlg = True

        # Intersection rectangle in cartesian coordinates
        corner0 = (self.location0[0] - constants.robotHeadRadius, self.location0[1], self.location0[2])
        corner1 = self.location1
        zHeight = corner0[2] + 10
        corner2 = (corner0[0], corner1[1], zHeight)
        corner3 = (corner1[0], corner0[1], zHeight)
        self.intersectionRectangle = [corner0, corner1, corner2, corner3]


    def process(self, minuteHandPosition):
        # The state machine for this object is just checking if it is ready.
        self.updateReadyFlg(minuteHandPosition)

        self.updateIntersectionRectangle()


    def calculateSlope(self, location0, location1):
        # Take change in R and Z
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
            Args:
                placementArray (list): A list of lists that denote where to place blocks
                startLocation (tuple): The location of the bottom - front corner of the stack
                blockSpacing (int): How far the blocks get placed from each other in mm
            Returns:
                list: A list of tuples that denote where to place blocks
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
        if abs(self.location0[1] - minuteHandPosition) < 30:
            self.isReadyFlg = False
            self.currentBlock = 0
            return

        return


    def updateIntersectionRectangle(self):
        """Updates dimensions of the intersection rectangle
        Only moves the top of the rectangle up or down
        """

        currentZHeight = self.blockPlacements[self.currentBlock][2] + 10
        previousZHeight = self.intersectionRectangle[2][2]

        # If the heights are less than 10mm apart, we don't need to update
        if abs(currentZHeight - previousZHeight) < 10:
            return

        # Update the top of the rectangle
        self.intersectionRectangle[2] = (self.intersectionRectangle[2][0], self.intersectionRectangle[2][1], currentZHeight)
        self.intersectionRectangle[3] = (self.intersectionRectangle[3][0], self.intersectionRectangle[3][1], currentZHeight)




