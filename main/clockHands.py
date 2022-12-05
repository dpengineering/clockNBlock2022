#      ******************************************************************
#      *                                                                *
#      *                        Clock Hands Object                      *
#      *                                                                *
#      *            Arnav Wadhwa                   12/03/2022           *
#      *                                                                *
#      ******************************************************************

from dpeaDPi import DPiStepper
from time import sleep

# Motor Constanta

MICROSTEPPING = 8

# Hour Hand constants

HOUR_HAND = 0
HOUR_HAND_GEAR_REDUCTION = 5  # Gear reduction is 5:1
HOUR_HAND_STEPS_PER_REVOLUTION = 200 * MICROSTEPPING * HOUR_HAND_GEAR_REDUCTION  # 8000
# Regular hour hand speed in steps per second ~ 0.19 steps/sec
HOUR_HAND_CLOCK_SPEED = HOUR_HAND_STEPS_PER_REVOLUTION / 43200
HOUR_HAND_MAX_SPEED = HOUR_HAND_STEPS_PER_REVOLUTION / 5  # 1600

# Minute Hand Constants

MINUTE_HAND = 1
MINUTE_HAND_GEAR_REDUCTION = 204 # Gear reduction is 204:1
MINUTE_HAND_STEPS_PER_REVOLUTION = 200 * MICROSTEPPING * MINUTE_HAND_GEAR_REDUCTION # 326400
# Regular minute hand speed in steps per second ~ 90.7 steps/sec
MINUTE_HAND_CLOCK_SPEED = MINUTE_HAND_STEPS_PER_REVOLUTION / 3600
MINUTE_HAND_MAX_SPEED = MINUTE_HAND_STEPS_PER_REVOLUTION / 204  # 1600, < 1 rev / 5 sec but fat gear reduction

dpiStepper = DPiStepper()


# Initialize to 12:00 position
def setupClock():

    dpiStepper.setBoardNumber(0)
    if not dpiStepper.initialize():
        print("Communication with the DPiStepper board failed.")
        return

    dpiStepper.enableMotors(True)

    home()

    dpiStepper.enableMotors(False)


# Home clock hands
async def home():

    # Set Speed and Acceleration to max

    dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)
    dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)

    dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)
    dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)

    # Move to limit switches

    dpiStepper.moveToHomeInSteps(HOUR_HAND, 1, HOUR_HAND_MAX_SPEED, HOUR_HAND_STEPS_PER_REVOLUTION)
    dpiStepper.moveToHomeInSteps(MINUTE_HAND, 1, MINUTE_HAND_MAX_SPEED, MINUTE_HAND_STEPS_PER_REVOLUTION)

    dpiStepper.waitUntilMotorStops(HOUR_HAND)
    dpiStepper.waitUntilMotorStops(MINUTE_HAND)

    # Go to 12:00 Position

    dpiStepper.moveToRelativePositionInSteps(MINUTE_HAND, -9000, False)
    dpiStepper.moveToRelativePositionInSteps(HOUR_HAND, 1368, False)


async def moveClock(multiplier: int):

    dpiStepper.enableMotors(True)

    if 0 < multiplier < 15:
        CLOCK_SPEED = multiplier
    else:
        CLOCK_SPEED = 1

    dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_CLOCK_SPEED * CLOCK_SPEED)
    dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_CLOCK_SPEED * CLOCK_SPEED)

    dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_CLOCK_SPEED * CLOCK_SPEED)
    dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_CLOCK_SPEED * CLOCK_SPEED)

    # TODO: Ask Stan if it is worth it to implement a "just move" function to the firmware


def moveToTime(time):

    """ Move to specified time
    @param time: The time to move to
    """

    if type(time) is str:
        time.replace(':', '')
        time = int(time)

    minutes = (time % 100) % 60
    hours = int(time / 100) % 12

    # Set Speed and Acceleration to max

    dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)
    dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)

    dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)
    dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)

    # Move to time
    # TODO: Ask Stan if absolute position is steps from 0 and if it goes in the positive direction.
    #  Or should I calculate my own position based on relative values.
    dpiStepper.moveToAbsolutePositionInSteps(HOUR_HAND, (hours / 12) * HOUR_HAND_STEPS_PER_REVOLUTION, False)
    dpiStepper.moveToAbsolutePositionInSteps(MINUTE_HAND, (minutes / 60) * MINUTE_HAND_STEPS_PER_REVOLUTION, False)


# TODO: Get position in degrees
#   Get position in radians
#   Move to position in degrees / radians (Maybe change time to this one too)
#   Figure out interrupt handler for when it goes over the block places. 




