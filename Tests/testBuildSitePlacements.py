import Objects.constants as constants


def generatePlacementList(placementArray, startLocation, slope, blockSpacing=1):
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

    for rowIdx, row in enumerate(placementArray):
        currentOrigin = startLocation
        for colIdx, value in enumerate(row):
            # If we are at the first column, offset by the offset value
            if colIdx == 0:
                currentOrigin = currentOrigin[0] + value, currentOrigin[1], currentOrigin[2]
            elif value:
                # Calculate the position we need to place our block
                currentRow = numRows - (rowIdx + 1)
                currentCol = colIdx - 1
                zPos = currentRow * blockSizeWithSpacing + currentOrigin[2] + currentCol * slope
                rPos = currentOrigin[0] + currentCol * blockSizeWithSpacing
                placements.insert(0, (rPos, currentOrigin[1], zPos))

    return placements


def calculateSlope(location0, location1):
    # Take change in R and Z
    deltaR = location1[0] - location0[0]
    deltaZ = location1[2] - location0[2]

    # calculate and return slope
    return deltaZ / deltaR


def main():
    array = constants.placementArrays[0]
    print(array)
    initialLocation = constants.buildLocations[0][0]
    slope = calculateSlope(initialLocation, constants.buildLocations[0][1])

    print(generatePlacementList(array, initialLocation, slope))


if __name__ == '__main__':
    main()
