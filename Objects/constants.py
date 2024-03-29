"""Constants for all of our objects"""
import numpy as np

blockSize = 30  # in mm
blockPadding = 1  # in mm

# Solenoid Values
# Robot Arm
magnetSolenoid = 11
rotationSolenoid = 10
robotHeadRadius = 80  # Major radius of the robot end effector mm
robotSpeed = 120
rotationHeight = -1430
maximumMovingRadius = 350  # mm
robotMovingPadding = 10  # Padding for robot arm to move around blocks mm
degreesPerBlock = 360 / blockSize + blockPadding  # Degrees per block
maximumSpiralingZHeight = -1210  # mm

# Clock
clockDeadZone = 45  # Degrees
hourHandZHeight = -1416.5

# Feeder solenoids in (side, up) order
blockFeederSolenoids = [(6, 7),
                        (4, 3),
                        (9, 8),
                        (0, 1)]


# Locations

# Build Sites
#   Replace second value with the location of the ends of the build sites.
buildLocations = [[(303.6, 351.870, -1443.8), (478.3, 351.789, -1445.3)],
                  [(295.8, 263.268, -1444.8), (543.6, 262.883, -1444.8)],
                  [(288.8, 172.206, -1445.3), (524.9, 172.340, -1448.4)],
                  [(290.1, 82.162, -1448.4), (414.2, 82.032, -1450.0)]]

# Block Feeders
blockFeederLocations = [(343.0, 308.000, -1472.6),
                        (340.8, 217.512, -1471.7),
                        (338.6, 127.862, -1471.2),
                        (341.2, 37.535, -1468.6)]

# Clock Minute Hand Radius
# The place where we will place a block on the clock's minute hand
clockMinuteHandRadius = 325.6
clockMinuteHandZHeight = -1416.5


# Block Placement Arrays
# These arrays hold the arrangement of blocks to build on the building site
# The first column in each array will be reserved for the amount of offset the next row should have from the first

# Build 0 has room for 5 blocks on the base.
placement0 = [[0, 1, 0, 0, 0, 0, 0],
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
placement3 = [[0,               0, 0, 0, 0, 0, 0],
              [- blockSize / 2, 0, 0, 1, 0, 0, 0],
              [0              , 0, 1, 1, 0, 0, 0],
              [0              , 0, 1, 1, 0, 0, 0],
              [0              , 0, 1, 1, 0, 0, 0],
              [0              , 0, 1, 1, 0, 0, 0]]

placementArrays = [placement0, placement1, placement2, placement3]


# Exclusion Zones for poles
poleLocations = [(398.3, 270.719, -1438.1),
                 (425.9, 206.192, -1438.1),
                 (429.2, 332.259, -1398.1)]

# 2D representation of the pole exclusion zones, 700 is an arbitrary number that is larger than the build area
pole0 = [(poleLocations[0][0] - robotHeadRadius, poleLocations[0][1], -np.inf),
         (700, poleLocations[0][1], -np.inf),
         (poleLocations[0][0] - robotHeadRadius, poleLocations[0][1], np.inf),
         (700, poleLocations[0][1], np.inf)]

pole1 = [(poleLocations[1][0] - robotHeadRadius, poleLocations[1][1], -np.inf),
         (700, poleLocations[1][1], -np.inf),
         (poleLocations[1][0] - robotHeadRadius, poleLocations[1][1], np.inf),
         (700, poleLocations[1][1], np.inf)]

pole2 = [(poleLocations[2][0] - robotHeadRadius, poleLocations[2][1], -np.inf),
         (700, poleLocations[2][1], -np.inf),
         (poleLocations[2][0] - robotHeadRadius, poleLocations[2][1], np.inf),
         (700, poleLocations[2][1], np.inf)]


poles = [pole0, pole1, pole2]


def cartesianToPolar(position: tuple) -> tuple:
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
    theta = np.rad2deg(theta)

    # Make sure theta is between 0 and 360
    theta = (theta + 360) % 360

    return r, theta, z


def polarToCartesian(position: tuple) -> tuple:
    """Converts polar coordinates to cartesian coordinates"""
    r, theta, z = position
    theta = np.deg2rad(theta)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y, z
