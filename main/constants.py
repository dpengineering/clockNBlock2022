"""Constants for all of our objects"""
import numpy as np

blockSize = 31  # mm

# Solenoid Values
# Robot Arm
magnetSolenoid = 11
rotationSolenoid = 10
robotHeadRadius = 80  # Major radius of the robot end effector
robotSpeed = 140
rotationHeight = -1430

# Feeder solenoids in (side, up) order
blockFeederSolenoids = [(6, 7),
                        (4, 3),
                        (9, 8),
                        (0, 1)]


# Locations

# Build Sites
#   Replace second value with the location0 of the ends of the build sites.
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

# This is the point where the robot arm will start hitting the side posts and crashing
maximumMovingRadius = 414.2  # mm


def cartesianToPolar(position: tuple):
    """Helper function to change cartesian coordinates to polar
    Args:
        position (tuple): Current robot position in cartesian plane
    Returns:
        r, theta, z (tuple (float)): Returns the polar coordinates that correspond to the cartesian coordinates
    """
    x, y, z = position
    # Convert to Polar Coords
    r = np.sqrt(x ** 2 + y ** 2)
    theta = np.arctan2(y, x)
    print(theta)
    theta = np.rad2deg(theta)
    print(theta)

    # Adjust for negative values
    if x < 0 < y:
        theta += 180
    elif x < 0 and y < 0:
        theta += 360
    elif y < 0 < x:
        theta += 360

    return r, theta, z


def polarToCartesian(position: tuple):
    """Converts polar coordinates to cartesian coordinates"""
    r, theta, z = position
    theta = np.deg2rad(theta)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y, z



