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


class Clock:
    """Clock object
    Controls clock hands through the DPi_Stepper board
    """

    # Creates setpper board object
    dpiStepper = DPiStepper()

    def __init__(self):
        """Constructor for clock object
        Does nothing, just creates the object
        """
        pass

    # Sets up block
    def setup(self):
        """Sets up clock so it can be used
        Moves clock to the 12:00 position when done
        """
        # print("setup")
        self.dpiStepper.setBoardNumber(0)

        if not self.dpiStepper.initialize():
            # print("Communication with the DPiStepper board failed.")
            return

        self.dpiStepper.enableMotors(True)
        # print("homing")
        self.home()

    # There isn't much to do for the clock, just make it go
    def process(self, multiplier=1):
        """State machine for the clock"""

        # print(f"Hour Position (max {HOUR_HAND_STEPS_PER_REVOLUTION}): {self.getPositionSteps(HOUR_HAND)}")
        # print(f"Minute Position (max {MINUTE_HAND_STEPS_PER_REVOLUTION}): {self.getPositionSteps(MINUTE_HAND)}")
        # Check if we need to reset the clock steps to be in our range
        self.updatePosition()

        # if hands aren't moving, move them a full rotation
        if not self.isStepperMoving(HOUR_HAND):
            # print("moving hour hand")
            self.moveHand(HOUR_HAND, HOUR_HAND_STEPS_PER_REVOLUTION, multiplier)

        if not self.isStepperMoving(MINUTE_HAND):
            # print("moving minute hand")
            self.moveHand(MINUTE_HAND, MINUTE_HAND_STEPS_PER_REVOLUTION, multiplier)

    # Home clock hands
    def home(self):
        """Helper function to home the clock hands and move them to the 12:00 position"""
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
        """Moves the clock to a specified time
        Args:
            time: The time we want to go to, it is fine if there is a colon as we remove it
        """

        # If the time was inputted as a string with a colon, remove that colon and cast to int
        if type(time) is str:
            time = time.replace(':', '')
            time = int(time)

        # Separating the minute and hour value
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
                                                 int(hours / 12 * HOUR_HAND_STEPS_PER_REVOLUTION), False)
        self.dpiStepper.moveToAbsolutePositionInSteps(MINUTE_HAND,
                                                 int(minutes / 60 * MINUTE_HAND_STEPS_PER_REVOLUTION), False)

        # Wait for motors to stop
        while not self.dpiStepper.getAllMotorsStopped():
            sleep(0.1)

    def getPositionDegrees(self, hand: int) -> int:
        """Helper function to return position of specified hand in degrees
        Args:
            hand (int): Which hand to get the position of
        Returns:
            int: Clock hand position in degrees
        """

        # Checks what hand it is and returns degree value of it
        #   We subtract 90 from our values because the '0' position of our clock is actually at the 12:00 position
        #   And not at the same 0 of our polar coordinate system
        if hand == HOUR_HAND:
            return round(360 / HOUR_HAND_STEPS_PER_REVOLUTION * self.getPositionSteps(HOUR_HAND)) - 90
        else:
            return round(360 / MINUTE_HAND_STEPS_PER_REVOLUTION * self.getPositionSteps(MINUTE_HAND)) - 90

    def getPositionRadians(self, hand: int) -> float:
        """Helper function to give clock hand position in radians
        Args:
            hand (int): The hand we want to get the position of
        Returns:
            float: Clock hand position in radians
        """

        # Convert our getPositionDegrees() function to radians
        degreesToRadians = math.pi / 180
        pos = self.getPositionDegrees(hand) * degreesToRadians

        # Returns -pos rounded to the third decimal place
        #   The return value is -pos because the clock goes clockwise where as the radian system goes counter clockwise
        return round(-pos, 3)

    def getPositionTime(self) -> str:
        """Returns time that the clock is currently at"""
        # Since there is 30 degrees per hour on a clock, we can take our degrees divide it by 30 and floor it to get
        # the number of hours
        hours = int(self.getPositionDegrees(HOUR_HAND) / 30)

        # Same logic as above but there's 5 degrees per minute
        minutes = int(self.getPositionDegrees(MINUTE_HAND) / 5)
        if hours == 0:
            hours = 12

        return f'{hours}:{minutes}'

    def moveHand(self, hand: int, steps: int, multiplier=1):
        """Moves specified hand a certian number of steps
        Args:
            hand (int): Hand to be moved
            steps (int): Number of steps to move
        Returns:
            True on success, otherwise False
        """

        # Checks if minute or hour hand is given, if neither then returns false
        if hand == HOUR_HAND:
            speed = HOUR_HAND_CLOCK_SPEED
        elif hand == MINUTE_HAND:
            speed = MINUTE_HAND_CLOCK_SPEED
        else:
            return False

        # Moves amount of steps at real time speed
        self.dpiStepper.setSpeedInStepsPerSecond(hand, speed * multiplier)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(hand, speed * multiplier)

        self.dpiStepper.moveToRelativePositionInSteps(hand, steps, False)

    def updatePosition(self):
        """Helper function to reset step value to within the range of a full rotation"""

        hourHandPosition = self.dpiStepper.getCurrentPositionInSteps(HOUR_HAND)[1]
        if hourHandPosition >= HOUR_HAND_STEPS_PER_REVOLUTION:
            self.dpiStepper.setCurrentPositionInSteps(HOUR_HAND, hourHandPosition % HOUR_HAND_STEPS_PER_REVOLUTION)

        minuteHandPosition = self.dpiStepper.getCurrentPositionInSteps(MINUTE_HAND)[1]
        if minuteHandPosition >= MINUTE_HAND_STEPS_PER_REVOLUTION:
            self.dpiStepper.setCurrentPositionInSteps(MINUTE_HAND, minuteHandPosition % MINUTE_HAND_STEPS_PER_REVOLUTION)

    def isStepperMoving(self, hand: int):
        """Helper function to check if steppers are moving"""
        return not self.dpiStepper.getStepperStatus(hand)[1]

    def getPositionSteps(self, hand: int):
        return self.dpiStepper.getCurrentPositionInSteps(hand)[1]

