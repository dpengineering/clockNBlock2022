# Simple test to check clock positions and degrees

import math
# To import the DPiClockNBlock library
import sys
sys.path.insert(0, "..")

from main.clockHands import Clock
from main.robotArm import RobotArm

clock = Clock()
robot = RobotArm(11, 10)

# Motor Constants

MICROSTEPPING = 8

# Hour Hand constants

HOUR_HAND = 0
HOUR_HAND_GEAR_REDUCTION = 5  # Gear reduction is 5:1
# I am not sure why there is 300 extra steps for a full rotation.
HOUR_HAND_STEPS_PER_REVOLUTION = 200 * MICROSTEPPING * HOUR_HAND_GEAR_REDUCTION + 300  # 8300
# Regular hour hand speed in steps per second ~ 0.19 steps/sec
HOUR_HAND_CLOCK_SPEED = HOUR_HAND_STEPS_PER_REVOLUTION / 43200
HOUR_HAND_MAX_SPEED = HOUR_HAND_STEPS_PER_REVOLUTION / 5  # 1600

# Minute Hand Constants

MINUTE_HAND = 1
MINUTE_HAND_GEAR_REDUCTION = 204  # Gear reduction is 204:1
MINUTE_HAND_STEPS_PER_REVOLUTION = int(200 * MICROSTEPPING * MINUTE_HAND_GEAR_REDUCTION * 0.998)  # 326400
# Regular minute hand speed in steps per second ~ 90.7 steps/sec
MINUTE_HAND_CLOCK_SPEED = MINUTE_HAND_STEPS_PER_REVOLUTION / 3600
MINUTE_HAND_MAX_SPEED = 20000


def setup():
    clock.setup()


# Testing different points as well as the accuracy of getDegrees, radians, and steps
def main():
    setup()
    clock.dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)
    clock.dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)

    clock.dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)
    clock.dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)

    print("go to 12:05")
    clock.moveToTime(1205)
    clock.dpiStepper.waitUntilMotorStops(MINUTE_HAND)
    clock.dpiStepper.waitUntilMotorStops(HOUR_HAND)
    # Print radian position and time
    print(f'Hour radians: {clock.getPositionRadians(HOUR_HAND)}')
    print(f'Minute radians: {clock.getPositionRadians(MINUTE_HAND)}')
    print(f'Should be {math.pi / 2} for both')
    print(f'Time: {clock.getPositionTime()}')

    print(robot.blockManagers[2].isReady(clock.getPositionRadians(1)))

    # print("go to 3:15")
    # clock.moveToTime(315)
    # clock.dpiStepper.waitUntilMotorStops(MINUTE_HAND)
    # clock.dpiStepper.waitUntilMotorStops(HOUR_HAND)
    # # Print radian position and time
    # print(f'Hour radians: {clock.getPositionRadians(HOUR_HAND)}')
    # print(f'Minute radians: {clock.getPositionRadians(MINUTE_HAND)}')
    # print(f'should be 0 for both')
    # print(f'Time: {clock.getPositionTime()}')
    #
    # print("go to 6:30")
    # clock.moveToTime(630)
    # clock.dpiStepper.waitUntilMotorStops(MINUTE_HAND)
    # clock.dpiStepper.waitUntilMotorStops(HOUR_HAND)
    # # Print radian position and time
    # print(f'Hour radians: {clock.getPositionRadians(HOUR_HAND)}')
    # print(f'Minute radians: {clock.getPositionRadians(MINUTE_HAND)}')
    # print(f'should be {3*math.pi / 2} for both')
    # print(f'Time: {clock.getPositionTime()}')
    #
    # print("Move 3 rotations")
    # clock.dpiStepper.moveToRelativePositionInSteps(HOUR_HAND, HOUR_HAND_STEPS_PER_REVOLUTION * 3, False)
    # clock.dpiStepper.moveToRelativePositionInSteps(MINUTE_HAND, MINUTE_HAND_STEPS_PER_REVOLUTION * 3, False)
    # clock.dpiStepper.waitUntilMotorStops(MINUTE_HAND)
    #
    # clock.updatePosition()
    #
    # print(f'Hour Steps: {clock.getPositionSteps(HOUR_HAND)}, Radians: {clock.getPositionRadians(HOUR_HAND)}')
    # print(f'Minute Steps: {clock.getPositionSteps(MINUTE_HAND)}, Radians: {clock.getPositionRadians(MINUTE_HAND)}')
    # print(f'should be 0 rad for both')
    # print(f'Time: {clock.getPositionTime()}')

    # Honestly I think that is all that we need to check
if __name__ == "__main__":
    main()
