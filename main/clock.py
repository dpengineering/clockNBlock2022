from time import sleep, localtime
from dpeaDPi.DPiStepper import DPiStepper


class Clock:

    # Constants
    dpiStepper = DPiStepper()

    # Motor Constants
    MICROSTEPPING = 8

    HOUR_HAND_PIN = 0
    HOUR_HAND_GEAR_REDUCTION = 5  # Gear reduction is 5:1
    # I am not sure why there is 300 extra steps for a full rotation.
    HOUR_HAND_STEPS_PER_REVOLUTION = 200 * MICROSTEPPING * HOUR_HAND_GEAR_REDUCTION + 290 # 8300
    # Hour hand base speed, 1 revolution in 12 hours, about 0.19 steps per second
    HOUR_HAND_BASE_SPEED = HOUR_HAND_STEPS_PER_REVOLUTION // (12 * 60 * 60)
    # Hour hand max speed. I don't feel comfortable sending it more than 0.5 rev / sec - 4150 steps/sec
    HOUR_HAND_MAX_SPEED = int(HOUR_HAND_STEPS_PER_REVOLUTION / 2)
    HOUR_HAND_ACCELERATION = HOUR_HAND_MAX_SPEED // 4

    MINUTE_HAND_PIN = 1
    MINUTE_HAND_GEAR_REDUCTION = 204  # Gear reduction is 204:1
    MINUTE_HAND_STEPS_PER_REVOLUTION = int(200 * MICROSTEPPING * MINUTE_HAND_GEAR_REDUCTION * 1.002)  # 326400
    # Base minute hand speed, 1 revolution per hour, about 90.6 steps per second
    MINUTE_HAND_BASE_SPEED = MINUTE_HAND_STEPS_PER_REVOLUTION // (60 * 60)
    MINUTE_HAND_MAX_SPEED = 20000
    MINUTE_HAND_ACCELERATION = MINUTE_HAND_MAX_SPEED // 4

    def __init__(self):
        self.initialize()

    def initialize(self):

        self.dpiStepper.setBoardNumber(0)
        if not self.dpiStepper.initialize():
            raise Exception("DPi Stepper initialization failed")

        self.dpiStepper.setMicrostepping(self.MICROSTEPPING)

        self.dpiStepper.enableMotors(True)

    def setup(self):
        """ Sets up the hands so they can be used."""

        # Set accelerations
        # this is done once and left alone
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(self.HOUR_HAND_PIN, self.HOUR_HAND_ACCELERATION)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(self.MINUTE_HAND_PIN, self.MINUTE_HAND_ACCELERATION)

        # Home hands
        self.dpiStepper.moveToHomeInSteps(self.HOUR_HAND_PIN, 1, self.HOUR_HAND_MAX_SPEED, self.HOUR_HAND_STEPS_PER_REVOLUTION)

        self.dpiStepper.moveToHomeInSteps(self.MINUTE_HAND_PIN, 1, self.MINUTE_HAND_MAX_SPEED, self.MINUTE_HAND_STEPS_PER_REVOLUTION)

        while not self.dpiStepper.getAllMotorsStopped():
            sleep(0.1)

        # Move to 12:00 position
        self.setSpeeds(self.HOUR_HAND_MAX_SPEED, self.MINUTE_HAND_MAX_SPEED)

        self.dpiStepper.moveToRelativePositionInSteps(self.HOUR_HAND_PIN, 2025, False)
        self.dpiStepper.moveToRelativePositionInSteps(self.MINUTE_HAND_PIN, -81100, False)

        while not self.dpiStepper.getAllMotorsStopped():
            sleep(0.1)

        self.dpiStepper.setCurrentPositionInSteps(self.HOUR_HAND_PIN, 0)
        self.dpiStepper.setCurrentPositionInSteps(self.MINUTE_HAND_PIN, 0)

        # Move to current time
        t = localtime()
        hourToSteps, minuteToSteps = self.convertTimeToSteps(t.tm_hour, t.tm_min, t.tm_sec)
        self.moveToPositionsRelative(hourToSteps, minuteToSteps)

        # Set base speeds
        self.setSpeeds(self.HOUR_HAND_BASE_SPEED, self.MINUTE_HAND_BASE_SPEED)

        # Set them going for an hour
        self.moveToPositionsRelative(self.HOUR_HAND_STEPS_PER_REVOLUTION, self.MINUTE_HAND_STEPS_PER_REVOLUTION)

    def process(self):
        """Processes the clock"""
        # This just basically includes checking how far off from the desired position the hands are
        # if they are too far away, then speed/slow them down to get them back to the desired position

        # Note: One case where this will be off is when there is a transfer from 11:59 to 12:00
        # or something along those lines. However, this will be fixed fairly quickly because it will only speed up for around
        # 1 second and then slow down again. This needs to be tested though

        # Get current time
        t = localtime()
        hourToSteps, minuteToSteps = self.convertTimeToSteps(t.tm_hour, t.tm_min, t.tm_sec)

        # Get current positions
        _successFlg, hourPosition = self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN) % self.HOUR_HAND_STEPS_PER_REVOLUTION
        _successFlg, minutePosition = self.dpiStepper.getCurrentPositionInSteps(self.MINUTE_HAND_PIN) % self.MINUTE_HAND_STEPS_PER_REVOLUTION

        # Calculate the difference between the desired position and the current position
        hourDifference = hourToSteps - hourPosition % self.HOUR_HAND_STEPS_PER_REVOLUTION
        minuteDifference = minuteToSteps - minutePosition % self.MINUTE_HAND_STEPS_PER_REVOLUTION

        # If the difference is greater than 5% of total steps, adjust the speed
        if abs(hourDifference) > self.HOUR_HAND_STEPS_PER_REVOLUTION * 0.05:
            self.dpiStepper.setSpeedInStepsPerSecond(self.HOUR_HAND_PIN, self.HOUR_HAND_BASE_SPEED + hourDifference * 0.01)
        else:
            self.dpiStepper.setSpeedInStepsPerSecond(self.HOUR_HAND_PIN, self.HOUR_HAND_BASE_SPEED)

        if abs(minuteDifference) > self.MINUTE_HAND_STEPS_PER_REVOLUTION * 0.05:
            self.dpiStepper.setSpeedInStepsPerSecond(self.MINUTE_HAND_PIN, self.MINUTE_HAND_BASE_SPEED + minuteDifference * 0.01)
        else:
            self.dpiStepper.setSpeedInStepsPerSecond(self.MINUTE_HAND_PIN, self.MINUTE_HAND_BASE_SPEED)



    #--------------------------------    Helper functions    --------------------------------#


    def setSpeeds(self, hourHandSpeed, minuteHandSpeed):
        """Sets the speed of the hands"""
        self.dpiStepper.setSpeedInStepsPerSecond(self.HOUR_HAND_PIN, hourHandSpeed)
        self.dpiStepper.setSpeedInStepsPerSecond(self.MINUTE_HAND_PIN, minuteHandSpeed)

    def moveToPositionsRelative(self, hourHandPosition, minuteHandPosition, waitFlg=False):
        """Moves the hands to the given positions"""
        self.dpiStepper.moveToRelativePositionInSteps(self.HOUR_HAND_PIN, hourHandPosition, False)
        self.dpiStepper.moveToRelativePositionInSteps(self.MINUTE_HAND_PIN, minuteHandPosition, False)

        if waitFlg:
            while not self.dpiStepper.getAllMotorsStopped():
                sleep(0.1)

    def convertTimeToSteps(self, hour, minute, second=0):
        """Converts the given time to steps"""
        hourToSteps = hour * self.HOUR_HAND_STEPS_PER_REVOLUTION // 12 + minute * self.HOUR_HAND_STEPS_PER_REVOLUTION // (12 * 60)
        minuteToSteps = minute * self.MINUTE_HAND_STEPS_PER_REVOLUTION // 60 + second * self.MINUTE_HAND_STEPS_PER_REVOLUTION // (60 * 60)
        return hourToSteps, minuteToSteps

    def getPositionDegrees(self):
        """Gets the position of the hands in degrees"""
        _successFlg, hourPosition = self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN)
        _successFlg, minutePosition = self.dpiStepper.getCurrentPositionInSteps(self.MINUTE_HAND_PIN)
        
        hourDegrees = hourPosition / self.HOUR_HAND_STEPS_PER_REVOLUTION * 360
        minuteDegrees = minutePosition / self.MINUTE_HAND_STEPS_PER_REVOLUTION * 360

        return hourDegrees % 360, minuteDegrees % 360

    def moveToTime(self, hour, minute, second=0, waitFlg=False):
        """Moves the hands to the given time"""
        hourToSteps, minuteToSteps = self.convertTimeToSteps(hour, minute, second)

        # Calculate the steps to move
        _successFlg, hourPosition = self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN)
        _successFlg, minutePosition = self.dpiStepper.getCurrentPositionInSteps(self.MINUTE_HAND_PIN)

        hourDifference = hourToSteps - hourPosition % self.HOUR_HAND_STEPS_PER_REVOLUTION
        minuteDifference = minuteToSteps - minutePosition % self.MINUTE_HAND_STEPS_PER_REVOLUTION

        self.moveToPositionsRelative(hourDifference, minuteDifference, waitFlg)



