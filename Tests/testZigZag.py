import sys
import numpy as np
from time import sleep
sys.path.append('../')

from dpeaDPi.DPiSolenoid import DPiSolenoid

from Objects.robotArm import RobotArm
import Objects.constants as constants

dpiSolenoid = DPiSolenoid()
dpiSolenoid.setBoardNumber(0)
if not dpiSolenoid.initialize():
    raise Exception("Solenoid initialization failed")

robot = RobotArm(dpiSolenoid, constants.magnetSolenoid, constants.rotationSolenoid)
if not robot.setup():
    raise Exception("Robot setup failed")

# This is an excerpt from robotManager.planZigZagMove() for testing purposes


def testZigZag(initialPoint, finalPoint):

    waypoints = []
    sign = np.random.choice([-1, 1])

    zigZagDistance = 50  # The threshold for when to zig-zag in mm
    zigZagAngleRange = (30, 60)  # The angle to zig-zag at
    zigZagAngle = np.random.randint(zigZagAngleRange[0], zigZagAngleRange[1])  # The angle to zig-zag at

    # Get the current and next waypoint cartesian coordinates
    currentX, currentY, currentZ = constants.polarToCartesian(initialPoint)

    nextX, nextY, nextZ = constants.polarToCartesian(finalPoint)

    # If the move is over the threshold in the XY plane, zig-zag
    distance = np.sqrt((nextX - currentX) ** 2 + (nextY - currentY) ** 2)
    # Get the angle between the current and next waypoint
    angle = np.rad2deg(np.arctan2(nextY - currentY, nextX - currentX))
    rawAngle = angle

    # Get the angle to zig-zag at
    sign = sign * -1
    angle += sign * zigZagAngle

    # Split the move up into segments of length zigZagDistance
    # If the move is less than zigZagDistance, do a small zig-zag
    if distance < zigZagDistance:
        intermediateX = currentX + distance / 2 * np.cos(np.deg2rad(angle))
        intermediateY = currentY + distance / 2 * np.sin(np.deg2rad(angle))
        intermediateZ = currentZ
        intermediatePoint = constants.cartesianToPolar((intermediateX, intermediateY, intermediateZ))
        waypoints.append(intermediatePoint)
        waypoints.append(finalPoint)
        return waypoints

    else:
        numSegments = int(distance / zigZagDistance)
        intermediateWaypoints = []

        for j in range(numSegments):
            intermediateX = currentX + zigZagDistance * (j + 1) * np.cos(np.deg2rad(angle))
            intermediateY = currentY + zigZagDistance * (j + 1) * np.sin(np.deg2rad(angle))
            intermediateZ = currentZ
            intermediatePoint = intermediateX, intermediateY, intermediateZ

            nextX = currentX + zigZagDistance * (j + 2) * np.cos(np.deg2rad(rawAngle))
            nextY = currentY + zigZagDistance * (j + 2) * np.sin(np.deg2rad(rawAngle))
            nextZ = currentZ

            nextPoint = constants.cartesianToPolar((nextX, nextY, nextZ))

            currentX = intermediateX
            currentY = intermediateY

            sign = sign * -1
            angle += sign * zigZagAngle
            intermediatePoint = constants.cartesianToPolar(intermediatePoint)
            nextPoint = constants.cartesianToPolar(nextPoint)
            intermediateWaypoints.append(intermediatePoint)
            intermediateWaypoints.append(nextPoint)

        intermediateWaypoints.append(finalPoint)
        return intermediateWaypoints


def main():
    sleep(5)
    initialPoint = (500, 260, -1350)
    finalPoint = (500, 172, -1350)
    waypoints = testZigZag(initialPoint, finalPoint)

    print(f'RobotState: {robot.dpiRobot.getRobotStatus()} \n Stopped State: {robot.dpiRobot.STATE_STOPPED}')

    print(waypoints)
    robot.queueWaypoints(waypoints, robotState=robot.dpiRobot.getRobotStatus()[1])


if __name__ == "__main__":
    main()
