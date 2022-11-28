import sys

from dpeaDPi.DPiStepper import DPiStepper
from time import sleep

#constants
MICROSTEPPING = 8

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE*60
SECONDS_PER_HALF_DAY = SECONDS_PER_HOUR*12

HOUR_HAND = 0
HOUR_HAND_STEPS_PER_REVOLUTION = 144000 * MICROSTEPPING
HOUR_HAND_BASE_SPEED_STEPS_PER_SECOND = HOUR_HAND_STEPS_PER_REVOLUTION / SECONDS_PER_HALF_DAY

MINUTE_HAND = 1
MINUTE_HAND_STEPS_PER_REVOLUTION = 48000 * MICROSTEPPING
MINUTE_HAND_BASE_SPEED_STEPS_PER_SECOND = MINUTE_HAND_STEPS_PER_REVOLUTION / SECONDS_PER_HOUR

#variables

dpiStepper = DPiStepper()
dpiStepper.setBoardNumber(0)
class Clock:

    def __init__(self):
        pass

    def initalize(boardNum):

        # Talk to DPiStepper
        # dpiStepper = DPiStepper()
        # dpiStepper.setBoardNumber(boardNum)

        print("Initalizing")

        # Make sure board is initalized
        if not dpiStepper.initialize():
            print("Communication with the DPiStepper board failed.")
            return

        print("Enable Motors")
        # Enable motors and set constants
        dpiStepper.enableMotors(True)
        print("Set Microstepping")
        dpiStepper.setMicrostepping(MICROSTEPPING)

        # Home clock hands
        print("Home Minute Hand")
        dpiStepper.moveToHomeInSteps(MINUTE_HAND, 1, MINUTE_HAND_BASE_SPEED_STEPS_PER_SECOND*20,
                                     MINUTE_HAND_STEPS_PER_REVOLUTION)
        print("Home Hour Hand")
        dpiStepper.moveToHomeInSteps(HOUR_HAND, 1, HOUR_HAND_BASE_SPEED_STEPS_PER_SECOND*60,
                                     HOUR_HAND_STEPS_PER_REVOLUTION)

        while not dpiStepper.getAllMotorsStopped():
            print("wait")
            sleep(0.02)

        sleep(0.1)
        print("Move to 12 Minute")
        dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_BASE_SPEED_STEPS_PER_SECOND*20)
        dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND_BASE_SPEED_STEPS_PER_SECOND, HOUR_HAND_BASE_SPEED_STEPS_PER_SECOND*60)
        dpiStepper.moveToRelativePositionInSteps(MINUTE_HAND, -9000, True)
        print("Move to 12 Hour")
        dpiStepper.moveToRelativePositionInSteps(HOUR_HAND, 197000, True)

        # Move to 12:00
        # Make this plz
        dpiStepper.enableMotors(False)
def main():
    Clock.initalize(0)


if __name__ == "__main__":
    try:
        main()
    finally:
        print('Interrupted')
        dpiStepper.emergencyStop(0)
        dpiStepper.emergencyStop(1)
        dpiStepper.enableMotors(False)

        
