# Simple test to check clock positions and degrees
import math
# To import from the other folders in project
import sys
from time import sleep

sys.path.insert(0, "..")

from main.hands import Hands
from main.robotArm import RobotArm

hands = Hands()
robot = RobotArm(11, 10)


# Testing different points as well as the accuracy of getDegrees, radians, and steps
def main():
    robot.setup()
    print('setting Up')
    hands.setup()

    # Set speeds to max
    print('setting max speed')
    hands.setSpeedBoth(hands.POINTER_MAX_SPEED, hands.KNOCKER_MAX_SPEED)

    # Move hands a full revolution
    print('moving one revolution')
    hands.dpiStepper.moveToRelativePositionInSteps(hands.POINTER, hands.POINTER_STEPS_PER_REVOLUTION, False)
    hands.dpiStepper.moveToRelativePositionInSteps(hands.KNOCKER, hands.KNOCKER_STEPS_PER_REVOLUTION, False)

    hands.waitForHandsStopped()
    sleep(2)

    # Getting position radians
    print(f'Pointer pos: {hands.getPositionRadians()[0] - 0.11}, Knocker pos: {hands.getPositionRadians()[1]}')

    # Set knocker going on its own
    print('setting knocker speed to base')
    hands.setSpeed(hands.KNOCKER, hands.KNOCKER_BASE_SPEED)

    print('moving knocker')
    # hands.dpiStepper.moveToRelativePositionInSteps(hands.KNOCKER, hands.KNOCKER_STEPS_PER_REVOLUTION, False)

    # Moving pointer to feed 0
    # pos = robot.feederLocations[0][1]
    pos = math.pi / 2
    print(f'Move pointer pi / 2')
    hands.moveToPosRadians(hands.POINTER, pos)

    hands.waitForHandsStopped()
    print(f'Hour: {hands.getPositionRadians()[0]}, Minute: {hands.getPositionRadians()[1]}')
    sleep(2)
    pos = 3 * math.pi / 2
    print(f'Move pointer 3pi / 2')
    hands.moveToPosRadians(hands.POINTER, pos)
    hands.waitForHandsStopped()

    print(f'Hour: {hands.getPositionRadians()[0]}, Minute: {hands.getPositionRadians()[1]}')
    sleep(2)
    pos = robot.blockManagers[0].feederPos[1] + 0.11
    print(f'Move to Feeder 0 ')
    hands.moveToPosRadians(hands.POINTER, pos)

    hands.waitForHandsStopped()
    sleep(2)
    print(f'Hour: {hands.getPositionRadians()[0] - 0.11}, Minute: {hands.getPositionRadians()[1]}')

    pos = robot.blockManagers[0].buildPos[1] + 0.11
    print(f'Move to build 0')
    hands.moveToPosRadians(hands.POINTER, pos)
    hands.waitForHandsStopped()
    print(f'Hour: {hands.getPositionRadians()[0] - 0.11}, Minute: {hands.getPositionRadians()[1]}')


    pos = robot.blockManagers[1].feederPos[1] + 0.11
    print(f'Move to Feeder 1 ')
    hands.moveToPosRadians(hands.POINTER, pos)

    hands.waitForHandsStopped()
    sleep(2)
    print(f'Hour: {hands.getPositionRadians()[0] - 0.11}, Minute: {hands.getPositionRadians()[1]}')

    pos = robot.blockManagers[1].buildPos[1] + 0.11
    print(f'Move to build 1')
    hands.moveToPosRadians(hands.POINTER, pos)
    hands.waitForHandsStopped()
    print(f'Hour: {hands.getPositionRadians()[0] - 0.11}, Minute: {hands.getPositionRadians()[1]}')

    pos = robot.blockManagers[2].feederPos[1] + 0.11
    print(f'Move to Feeder 2 ')
    hands.moveToPosRadians(hands.POINTER, pos)

    hands.waitForHandsStopped()
    sleep(5)
    print(f'Hour: {hands.getPositionRadians()[0] - 0.11}, Minute: {hands.getPositionRadians()[1]}')

    pos = robot.blockManagers[2].buildPos[1] + 0.11
    print(f'Move to build 2')
    hands.moveToPosRadians(hands.POINTER, pos)
    hands.waitForHandsStopped()
    print(f'Hour: {hands.getPositionRadians()[0] - 0.11}, Minute: {hands.getPositionRadians()[1]}')
    hands.dpiStepper.enableMotors(False)


if __name__ == "__main__":
    main()
