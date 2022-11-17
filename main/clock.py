
from dpeaDPi.DPiStepper import DPiStepper
from time import sleep

#constants
MICROSTEPPING = 16

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = SECONDS_PER_MINUTE*60
HOURS_PER_HALF_DAY = MINUTES_PER_HOUR*12

HOUR_HAND = 0
HOUR_HAND_STEPS_PER_REVOLUTION = 2304000
HOUR_HAND_BASE_SPEED_STEPS_PER_SECOND = HOUR_HAND_STEPS_PER_REVOLUTION / HOURS_PER_HALF_DAY

MINUTE_HAND = 1
MINUTE_HAND_STEPS_PER_REVOLUTION = 768000
MINUTE_HAND_BASE_SPEED_STEPS_PER_SECOND = MINUTE_HAND_STEPS_PER_REVOLUTION / MINUTES_PER_HOUR

#variables


class Clock:

    def __init__(self):
        pass

    def initalize(self, boardNum):

        # Talk to DPiStepper
        dpiStepper = DPiStepper()
        dpiStepper.setBoardNumber(boardNum)

        # Make sure board is initalized
        if not dpiStepper.initialize():
            print("Communication with the DPiStepper board failed.")
            return

        # Enable motors and set constants
        dpiStepper.enableMotors(True)

        dpiStepper.setMicrostepping(MICROSTEPPING)

        # Home clock hands

        dpiStepper.moveToHomeInSteps(MINUTE_HAND, 1, MINUTE_HAND_BASE_SPEED_STEPS_PER_SECOND*60,
                                     MINUTE_HAND_STEPS_PER_REVOLUTION)
        dpiStepper.moveToHomeInSteps(HOUR_HAND, 1, HOUR_HAND_BASE_SPEED_STEPS_PER_SECOND*12*60,
                                     HOUR_HAND_STEPS_PER_REVOLUTION)

        while not dpiStepper.getAllMotorsStopped():
            sleep(0.02)

        sleep(0.1)

        
