#      ******************************************************************
#      *                                                                *
#      *                        Clock Hands Object                      *
#      *                                                                *
#      *            Arnav Wadhwa                   12/03/2022           *
#      *                                                                *
#      ******************************************************************

from dpeaDPi.DPiStepper import DPiStepper
from time import sleep

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
MINUTE_HAND_STEPS_PER_REVOLUTION = 200 * MICROSTEPPING * MINUTE_HAND_GEAR_REDUCTION  # 326400
# Regular minute hand speed in steps per second ~ 90.7 steps/sec
MINUTE_HAND_CLOCK_SPEED = MINUTE_HAND_STEPS_PER_REVOLUTION / 3600
MINUTE_HAND_MAX_SPEED = 1600  # 1600, < 1 rev / 5 sec but fat gear reduction

dpiStepper = DPiStepper()


class Clock:

    def __init__(self):
        pass

    # Initialize to 12:00 position
    def setupClock(self):

        dpiStepper.setBoardNumber(0)
        if not dpiStepper.initialize():
            print("Communication with the DPiStepper board failed.")
            return

        dpiStepper.enableMotors(True)

        self.home()

    # Home clock hands
    def home(self):

        # Move to limit switches

        dpiStepper.moveToHomeInSteps(HOUR_HAND, 1, HOUR_HAND_MAX_SPEED, HOUR_HAND_STEPS_PER_REVOLUTION)
        dpiStepper.moveToHomeInSteps(MINUTE_HAND, 1, MINUTE_HAND_MAX_SPEED, MINUTE_HAND_STEPS_PER_REVOLUTION)

        dpiStepper.waitUntilMotorStops(HOUR_HAND)
        dpiStepper.waitUntilMotorStops(MINUTE_HAND)

        # Set Speed and Acceleration to max

        dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)
        dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)
        dpiStepper.moveToRelativePositionInSteps(HOUR_HAND, HOUR_HAND_STEPS_PER_REVOLUTION, True)

        dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)
        dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)

        # Go to 12:00 Position

        dpiStepper.moveToRelativePositionInSteps(MINUTE_HAND, -55825, False)
        dpiStepper.moveToRelativePositionInSteps(HOUR_HAND, 120, False)

        # TODO: replace this with the state function
        while not dpiStepper.getAllMotorsStopped():
            sleep(0.1)

        dpiStepper.setCurrentPositionInSteps(HOUR_HAND, 0)
        dpiStepper.setCurrentPositionInSteps(MINUTE_HAND, 0)

    # TODO: Replace with state function (honestly you can probably just delete this)
    def moveClock(self, multiplier: int):

        dpiStepper.enableMotors(True)

        if 0 < multiplier < 15:
            CLOCK_SPEED = multiplier
        else:
            CLOCK_SPEED = 1

        dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_CLOCK_SPEED * CLOCK_SPEED)
        dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_CLOCK_SPEED * CLOCK_SPEED)

        dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_CLOCK_SPEED * CLOCK_SPEED)
        dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_CLOCK_SPEED * CLOCK_SPEED)

    def moveToTime(self, time):

        """ Move to specified time
        @param time: The time to move to
        """

        # To give current time use datetime.now().strftime("%H:%M")
        if type(time) is str:
            time = time.replace(':', '')
            time = int(time)

        minutes = (time % 100) % 60
        hours = int(time / 100) % 12

        # Set Speed and Acceleration to max

        dpiStepper.enableMotors(True)
        dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)
        dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_MAX_SPEED)

        dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)
        dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_MAX_SPEED)

        # Move to time
        dpiStepper.moveToAbsolutePositionInSteps(HOUR_HAND,
                                                 int((hours / 12) * HOUR_HAND_STEPS_PER_REVOLUTION), False)
        dpiStepper.moveToAbsolutePositionInSteps(MINUTE_HAND,
                                                 int((minutes / 60) * MINUTE_HAND_STEPS_PER_REVOLUTION), False)

        # TODO: replace this with the state function
        while not dpiStepper.getAllMotorsStopped():
            sleep(0.1)

    # Used to move the clock to a time that is inputted at a speed that is a multiple of real time.
    # TODO: Clean this up its disgusting
    def moveToTimeRelative(self, time, speed: int):

        # To give current time use datetime.now().strftime("%H:%M")
        if type(time) is str:
            time = time.replace(':', '')
            time = int(time)

        # Extract minutes and hours from time
        hours = int(time / 100) % 12
        minutes = (time % 100) % 60

        # Goal position in steps
        hourGoalPos = int((hours / 12) * HOUR_HAND_STEPS_PER_REVOLUTION)
        minuteGoalPos = int((minutes / 60) * MINUTE_HAND_STEPS_PER_REVOLUTION)

        # Current clock position
        hourCurrentPos = dpiStepper.getCurrentPositionInSteps(HOUR_HAND)
        minuteCurrentPos = dpiStepper.getCurrentPositionInSteps(MINUTE_HAND)

        # Super messy way to calculate steps
        hourSteps = ((hourGoalPos + HOUR_HAND_STEPS_PER_REVOLUTION) - hourCurrentPos) % HOUR_HAND_STEPS_PER_REVOLUTION
        minuteSteps = ((minuteGoalPos + MINUTE_HAND_STEPS_PER_REVOLUTION) - minuteCurrentPos) % MINUTE_HAND_STEPS_PER_REVOLUTION

        # Enable Steppers
        dpiStepper.enableMotors(True)

        # Set acceleration and speed
        dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND, HOUR_HAND_CLOCK_SPEED * speed)
        dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND, HOUR_HAND_CLOCK_SPEED * speed)

        dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND, MINUTE_HAND_CLOCK_SPEED * speed)
        dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND, MINUTE_HAND_CLOCK_SPEED * speed)

        # Move to our goal position (in relative steps)
        dpiStepper.moveToRelativePositionInSteps(HOUR_HAND, hourSteps, False)
        dpiStepper.moveToRelativePositionInSteps(MINUTE_HAND, minuteSteps, False)

        # TODO: Replace with something that isn't busy waiting
        while not dpiStepper.getAllMotorsStopped():
            sleep(0.1)

        # Current clock position
        hourCurrentPos = dpiStepper.getCurrentPositionInSteps(HOUR_HAND)
        minuteCurrentPos = dpiStepper.getCurrentPositionInSteps(MINUTE_HAND)

        # Set stepper position back to being within our range
        dpiStepper.setCurrentPositionInSteps(HOUR_HAND, hourCurrentPos % HOUR_HAND_STEPS_PER_REVOLUTION)
        dpiStepper.setCurrentPositionInSteps(MINUTE_HAND, minuteCurrentPos % MINUTE_HAND_STEPS_PER_REVOLUTION)


    # ---------------------------------------------------------------------------------
    #                                 Private functions
    # ---------------------------------------------------------------------------------





    def getPositionDegrees(self, hand: int) -> int:

        if hand == HOUR_HAND:
            return round(360 / HOUR_HAND_STEPS_PER_REVOLUTION * dpiStepper.getCurrentPositionInSteps(HOUR_HAND))
        else:
            return round(360 / MINUTE_HAND_STEPS_PER_REVOLUTION * dpiStepper.getCurrentPositionInSteps(MINUTE_HAND))

    def getPositionTime(self) -> str:

        # Since there is 30 degrees per hour on a clock, we can take our degrees divide it by 30 and floor it to get
        # the number of hours
        hours = int(self.getPositionDegrees(HOUR_HAND) / 30)

        # Same logic as above but there's 5 degrees per minute
        minutes = int(self.getPositionDegrees(MINUTE_HAND) / 5)

        return f'{hours}:{minutes}'


def main():
    clock = Clock()
    clock.setupClock()
    clock.moveToTime(615)


if __name__ == "__main__":
    main()

