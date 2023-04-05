"""Constants for all of our objects"""
from DPi_ClockNBlock_Python.DPiClockNBlock import DPiClockNBlock


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
buildLocations = [[(466, -0.139, -1446.0), (467, -0.139, -1446.0)],
                  [(475, -1.685, -1444.9), (476, -1.685, -1444.9)],
                  [(479, 3.004, -1446.9), (480, 3.004, -1446.9)],
                  [(523, 1.434, -1446.5), (524, 1.434, -1446.5)]]

# Block Feeders
blockFeederLocations = [(343, -0.906, -1473.6),
                        (340, -2.497, -1475.3),
                        (343, 2.218, -1472.7),
                        (339, 0.648, -1471.2)]

# Clock Minute Hand Radius
# The place where we will place a block on the clock's minute hand
clockMinuteHandRadius = 520



# DPi Boards
clockNBlockBoards = []

for i in range(4):
    dpiClockNBlock = DPiClockNBlock()
    dpiClockNBlock.setBoardNumber(i)
    clockNBlockBoards.append(dpiClockNBlock)


