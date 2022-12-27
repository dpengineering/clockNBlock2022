#      ******************************************************************
#      *                                                                *
#      *                        Clock Hands Object                      *
#      *                                                                *
#      *            Arnav Wadhwa                   12/03/2022           *
#      *                                                                *
#      ******************************************************************
import math
from dpeaDPi.DPiStepper import DPiStepper
from time import sleep
from datetime import datetime

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
MINUTE_HAND_STEPS_PER_REVOLUTION =  int(200 * MICROSTEPPING * MINUTE_HAND_GEAR_REDUCTION * 0.998)  # 326400
# Regular minute hand speed in steps per second ~ 90.7 steps/sec
MINUTE_HAND_CLOCK_SPEED = MINUTE_HAND_STEPS_PER_REVOLUTION / 3600
MINUTE_HAND_MAX_SPEED = 20000  # 1600, < 1 rev / 5 sec but fat gear reduction


class Clock:

    dpiStepper = DPiStepper()
    stoppedFlg = False
    # Multiplier for clock speed
    multiplier = 1

    def __init__(self):
        pass

    # Initialize to 12:00 position
    def setup(self):

        self.dpiStepper.setBoardNumber(0)

        if not self.dpiStepper.initialize():
            print("Communication with the DPiStepper board failed.")
            return

        self.dpiStepper.enableMotors(True)

        self.home()

        # Move to current time
        self.moveToTime(int(datetime.now().strftime("%H%M")))

    # There isn't much to do for the clock, just make it go
    def process(self):
        if not self.stoppedFlg:
            self.updatePosition()
            # if hands aren't moving, move them a full rotation
            if not self.isStepperMoving(HOUR_HAND):
                self.moveHand(HOUR_HAND, HOUR_HAND_STEPS_PER_REVOLUTION)

            if not self.isStepperMoving(MINUTE_HAND):
                self.moveHand(MINUTE_HAND, MINUTE_HAND_STEPS_PER_REVOLUTION)
        else:
            return

    # Home clock hands
    def home(self):

        # Move to limit switches
        # print("Home hour hand")
        self.dpiStepper.moveToHomeInSteps(HOUR_HAND, 1, HOUR_HAND_MAX_SPEED, HOUR_HAND_STEPS_PER_REVOLUTION)
        # print("Home minute hand")
        self.dpiStepper.moveToHomeInSteps(MINUTE_HAND, 1, MINUTE_HAND_MAX_SPEED, MINUTE_HAND_STEPS_PER_REVOLUTION)

        self.dpiStepper.waitUntilMotorStops(HOUR_HAND)
        self.dpiStepper.waitUntilMotorStops(MINUTE_HAND)
        # print("done homing")

        # Set Speed and Acceleration to max

        self.dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)

        self.dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)

        # Go to 12:00 Position
        # print("moving to 12")
        self.dpiStepper.moveToRelativePositionInSteps(MINUTE_HAND, 110400, False)
        self.dpiStepper.moveToRelativePositionInSteps(HOUR_HAND, 4320, False)

        while not self.dpiStepper.getAllMotorsStopped():
            sleep(0.1)

        self.dpiStepper.setCurrentPositionInSteps(HOUR_HAND, 0)
        self.dpiStepper.setCurrentPositionInSteps(MINUTE_HAND, 0)
        # print("done")

    def moveToTime(self, time):

        """ Move to specified time
        @param time: The time to move to
        """

        if type(time) is str:
            time = time.replace(':', '')
            time = int(time)

        minutes = (time % 100) % 60
        hours = int(time / 100) % 12

        # Set Speed and Acceleration to max

        self.dpiStepper.enableMotors(True)
        self.dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)

        self.dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)

        # Move to time
        self.dpiStepper.moveToAbsolutePositionInSteps(HOUR_HAND,
                                                 int((hours / 12) * HOUR_HAND_STEPS_PER_REVOLUTION), False)
        self.dpiStepper.moveToAbsolutePositionInSteps(MINUTE_HAND,
                                                 int((minutes / 60) * MINUTE_HAND_STEPS_PER_REVOLUTION), False)

        while not self.dpiStepper.getAllMotorsStopped():
            sleep(0.1)

    def getPositionDegrees(self, hand: int) -> int:

        if hand == HOUR_HAND:
            return round(360 / HOUR_HAND_STEPS_PER_REVOLUTION * self.getPositionSteps(HOUR_HAND))
        else:
            return round(360 / MINUTE_HAND_STEPS_PER_REVOLUTION * self.getPositionSteps(MINUTE_HAND))

    # We will shift this by pi/4 rad to have it return on the same "0" as the robot
    def getPositionRadians(self, hand: int) -> float:
        degreesToRadians = math.pi / 180
        pos = self.getPositionDegrees(hand) * degreesToRadians - math.pi / 4
        return pos

    def getPositionTime(self) -> str:

        # Since there is 30 degrees per hour on a clock, we can take our degrees divide it by 30 and floor it to get
        # the number of hours
        hours = int(self.getPositionDegrees(HOUR_HAND) / 30)

        # Same logic as above but there's 5 degrees per minute
        minutes = int(self.getPositionDegrees(MINUTE_HAND) / 5)

        return f'{hours}:{minutes}'

    def getPositionSteps(self, hand: int):
        return self.dpiStepper.getCurrentPositionInSteps(hand)[1]

    def moveHand(self, hand: int, steps: int):
        if hand == HOUR_HAND:
            speed = HOUR_HAND_CLOCK_SPEED
        elif hand == MINUTE_HAND:
            speed = MINUTE_HAND_CLOCK_SPEED
        else:
            return False
        self.dpiStepper.setSpeedInStepsPerSecond(hand, speed * self.multiplier)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(hand, speed * self.multiplier)

        self.dpiStepper.moveToRelativePositionInSteps(hand, steps, False)

    # Resets steps value to be in our range
    def updatePosition(self):
        hourHandPosition = self.getPositionSteps(HOUR_HAND)
        if hourHandPosition >= HOUR_HAND_STEPS_PER_REVOLUTION:
            self.dpiStepper.setCurrentPositionInSteps(HOUR_HAND, hourHandPosition % HOUR_HAND_STEPS_PER_REVOLUTION)

        minuteHandPosition = self.getPositionSteps(MINUTE_HAND)
        if minuteHandPosition >= MINUTE_HAND_STEPS_PER_REVOLUTION:
            self.dpiStepper.setCurrentPositionInSteps(MINUTE_HAND, minuteHandPosition % MINUTE_HAND_STEPS_PER_REVOLUTION)

    def isStepperMoving(self, hand: int):
        return not self.dpiStepper.getStepperStatus(hand)[1]

    def emergencyStop(self):
        self.stoppedFlg = True
        self.dpiStepper.emergencyStop(HOUR_HAND)
        self.dpiStepper.emergencyStop(MINUTE_HAND)

    def resume(self):
        self.stoppedFlg = False



