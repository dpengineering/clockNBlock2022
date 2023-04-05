import numpy as np


class BuildSite:

    def __init__(self, location0, location1):
        # The need for two locations is just to calculate the "slope" of the build site
        # This is necessary since the build sites aren't flat which can cause the robot arm
        # to lose steps while placing a block down
        # Since we are in 3D, we don't have a traditional slope, but our slope can just be the distance
        # in Z over the distance in X and Y.
        self.location = location0
        self.slope = self.calculateSlope(location0, location1)

        self.currentBlock = None
        self.blockPlacements = None

        # Flags
        self.isReadyFlg = False

    def calculateSlope(self, location0, location1):
        # Take change all 3 axes
        deltaX = location1[0] - location0[0]
        deltaY = location1[1] - location0[1]
        deltaZ = location1[2] - location0[2]

        # sum change in X and Y
        deltaXY = np.sqrt(deltaX**2 + deltaY**2)

        # calculate and return slope
        return deltaZ / deltaXY


