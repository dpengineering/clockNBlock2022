# Simple test to check clock positions and degrees

# To import from the other folders in project
import sys
sys.path.insert(0, "..")

from main.hands import Hands
from main.robotArm import RobotArm

hands = Hands()
robot = RobotArm(11, 10)


# Testing different points as well as the accuracy of getDegrees, radians, and steps
def main():
    print('setting Up')
    hands.setup()

    # Set speeds to max
    print('setting max speed')
    hands.setSpeedBoth(hands.POINTER_MAX_SPEED, hands.KNOCKER_MAX_SPEED)

    # Move hands a full revolution
    print('moving one revolution')
    hands.dpiStepper.moveToRelativePositionInSteps(hands.POINTER, hands.POINTER_STEPS_PER_REVOLUTION, False)
    hands.dpiStepper.moveToRelativePositionInSteps(hands.KNOCKER, hands.KNOCKER_STEPS_PER_REVOLUTION, False)

    # Getting position radians
    print(f'Pointer pos: {hands.getPositionRadians()[0]}, Knocker pos: {hands.getPositionRadians()[1]}')

    # Set knocker going on its own
    print('setting knocker speed to base')
    hands.setSpeed(hands.KNOCKER, hands.KNOCKER_BASE_SPEED)

    print('moving knocker')
    hands.dpiStepper.moveToRelativePositionInSteps(hands.KNOCKER, hands.KNOCKER_STEPS_PER_REVOLUTION, False)

    # Moving pointer to feed 0
    pos = robot.feederLocations[0][1]
    print(f'Move pointer to Feeder 0 pickup')
    hands.moveToPosRadians(hands.POINTER, pos)


if __name__ == "__main__":
    main()
