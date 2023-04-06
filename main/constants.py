"""Constants for all of our objects"""
import numpy as np

blockSize = 31  # mm

# Solenoid Values
# Robot Arm
magnetSolenoid = 11
rotationSolenoid = 10

# Feeder solenoids in (side, up) order
blockFeederSolenoids = [(6, 7),
                        (4, 3),
                        (9, 8),
                        (0, 1)]


# Locations

# Build Sites
#   Replace second value with the location of the ends of the build sites.
buildLocations = [[(293.6, 350.570, -1442.8), (480.3, 351.789, -1444.3)],
                  [(285.8, 263.268, -1442.8), (543.6, 262.883, -1442.8)],
                  [(278.8, 172.206, -1444.3), (524.9, 172.340, -1447.4)],
                  [(280.1, 82.162, -1447.4), (414.2, 82.032, -1449.0)]]

# Block Feeders
blockFeederLocations = [(343.0, 308.000, -1474.6),
                        (340.8, 217.512, -1473.7),
                        (338.6, 127.862, -1473.2),
                        (341.2, 37.535, -1470.6)]

# Clock Minute Hand Radius
# The place where we will place a block on the clock's minute hand
clockMinuteHandRadius = 325.6
clockMinuteHandZHeight = -1416.5


# Block Placement Arrays
# These arrays hold the arrangement of blocks to build on the building site
# The first column in each array will be reserved for the amount of offset the next row should have from the first

# Build 0 has room for 6 blocks on the base.
placement0 = [ [0, 1, 0, 0, 0, 0, 0],
               [0, 1, 1, 0, 0, 0, 0],
               [0, 1, 1, 1, 0, 0, 0],
               [0, 1, 1, 1, 1, 0, 0],
               [0, 1, 1, 1, 1, 1, 0],
               [0, 1, 1, 1, 1, 1, 1]]

# Build 1 has room for 8 blocks on the base.
placement1 = [[- blockSize / 2, 0, 0, 0, 0, 1, 0, 0, 0],
              [0              , 0, 0, 0, 1, 1, 0, 0, 0],
              [- blockSize / 2, 0, 0, 0, 1, 1, 1, 0, 0],
              [0              , 0, 0, 1, 1, 1, 1, 0, 0],
              [-blockSize/2,    0, 0, 1, 1, 1, 1, 1, 0],
              [0              , 0, 1, 1, 1, 1, 1, 1, 0],
              [0              , 0, 1, 1, 1, 1, 1, 1, 0],
              [0              , 0, 1, 1, 1, 1, 1, 1, 0]]

# Build 2 has room for 7 blocks on the base.
placement2 = [[0              , 0, 0, 0, 1, 0, 0, 0],
              [- blockSize / 2, 0, 0, 0, 1, 1, 0, 0],
              [0              , 0, 0, 1, 1, 1, 0, 0],
              [- blockSize / 2, 0, 0, 1, 1, 1, 1, 0],
              [0              , 0, 1, 1, 1, 1, 1, 0],
              [- blockSize / 2, 0, 1, 1, 1, 1, 1, 1],
              [0              , 1, 1, 1, 1, 1, 1, 1]]

# Build 3 has room for 3 blocks on the base (only using 2 for now).
placement3 = [[- blockSize / 2, 0, 1, 0, 0, 0, 0],
              [0              , 1, 1, 0, 0, 0, 0],
              [0              , 1, 1, 0, 0, 0, 0],
              [0              , 1, 1, 0, 0, 0, 0],
              [0              , 1, 1, 0, 0, 0, 0],
              [0              , 1, 1, 0, 0, 0, 0]]

placementArrays = [placement0, placement1, placement2, placement3]


# Count the number of 1s in placement arrays
# This will be used to determine how many seconds per block we need to use
numpyArray = np.array(placementArrays)
numBlocks = 0
for value in np.nditer(numpyArray):
    if value == 1:
        numBlocks += 1



