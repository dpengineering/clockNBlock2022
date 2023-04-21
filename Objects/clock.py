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
    HOUR_HAND_STEPS_PER_REVOLUTION = 200 * MICROSTEPPING * HOUR_HAND_GEAR_REDUCTION + 290  # 8300
    # Hour hand base speed
    HOUR_HAND_BASE_SPEED = int(HOUR_HAND_STEPS_PER_REVOLUTION / 2)
    # Hour hand max speed. I don't feel comfortable sending it more than 0.5 rev / sec - 4150 steps/sec
    HOUR_HAND_MAX_SPEED = int(HOUR_HAND_STEPS_PER_REVOLUTION / 2)
    HOUR_HAND_ACCELERATION = HOUR_HAND_MAX_SPEED // 4

    # Offset for pointing, not sure why this is necessary
    HOUR_HAND_OFFSET = 6.3  # degrees


    MINUTE_HAND_PIN = 1
    MINUTE_HAND_GEAR_REDUCTION = 204  # Gear reduction is 204:1
    MINUTE_HAND_STEPS_PER_REVOLUTION = int(200 * MICROSTEPPING * MINUTE_HAND_GEAR_REDUCTION * 1.002)  # 326400
    MINUTE_HAND_BASE_SPEED = MINUTE_HAND_STEPS_PER_REVOLUTION // (20 * 60)
    MINUTE_HAND_MAX_SPEED = 15000
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

        return True

    # This is necessary because the block feeders need to prime which means the clock needs to be out of the way
    # After that happens we can go to real time.
    def setup2(self):
        """ Sets up the hands so they can be used."""

        # Set minute hand speed to max
        self.dpiStepper.setSpeedInStepsPerSecond(self.MINUTE_HAND_PIN, self.MINUTE_HAND_MAX_SPEED)
        # Send minute hand in a full circle
        self.dpiStepper.moveToRelativePositionInSteps(self.MINUTE_HAND_PIN, self.MINUTE_HAND_STEPS_PER_REVOLUTION, True)

        # Set base speeds
        self.setSpeeds(self.HOUR_HAND_BASE_SPEED, self.MINUTE_HAND_BASE_SPEED)

        # Set minute hand going for a revolution
        self.moveToPositionsRelative(minuteHandPosition=self.MINUTE_HAND_STEPS_PER_REVOLUTION)

        return True

    def process(self, hourHandPosition=None):
        """Processes the clock"""

        # If the minute hand is stopped, send it going for a revolution
        self.refreshSteps()

        if self.dpiStepper.getStepperStatus(self.MINUTE_HAND_PIN)[1]:
            self.dpiStepper.moveToRelativePositionInSteps(self.MINUTE_HAND_PIN, self.MINUTE_HAND_STEPS_PER_REVOLUTION, False)

        if hourHandPosition is not None:
            self.moveToPositionDegrees(hourDegrees=hourHandPosition, waitFlg=False)




    #--------------------------------    Helper functions    --------------------------------#


    def setSpeeds(self, hourHandSpeed, minuteHandSpeed):
        """Sets the speed of the hands"""
        self.dpiStepper.setSpeedInStepsPerSecond(self.HOUR_HAND_PIN, hourHandSpeed)
        self.dpiStepper.setSpeedInStepsPerSecond(self.MINUTE_HAND_PIN, minuteHandSpeed)

    def moveToPositionsRelative(self, hourHandPosition=None, minuteHandPosition=None, waitFlg=False):
        """Moves the hands to the given positions"""
        if hourHandPosition is not None:
            self.dpiStepper.moveToRelativePositionInSteps(self.HOUR_HAND_PIN, hourHandPosition, False)

        if minuteHandPosition is not None:
            self.dpiStepper.moveToRelativePositionInSteps(self.MINUTE_HAND_PIN, minuteHandPosition, False)

        if waitFlg:
            while not self.dpiStepper.getAllMotorsStopped():
                sleep(0.1)

    def convertTimeToSteps(self, hour, minute, second=0):
        """Converts the given time to steps"""
        hourToSteps = hour * self.HOUR_HAND_STEPS_PER_REVOLUTION // 12 + minute * self.HOUR_HAND_STEPS_PER_REVOLUTION // (12 * 60)
        minuteToSteps = minute * self.MINUTE_HAND_STEPS_PER_REVOLUTION // 60 + second * self.MINUTE_HAND_STEPS_PER_REVOLUTION // (60 * 60)
        return hourToSteps, minuteToSteps

    def getPositionDegrees(self) -> tuple:
        """Gets the position of the hands in degrees"""
        _successFlg, hourPosition = self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN)
        _successFlg, minutePosition = self.dpiStepper.getCurrentPositionInSteps(self.MINUTE_HAND_PIN)
        
        hourDegrees = hourPosition / self.HOUR_HAND_STEPS_PER_REVOLUTION * 360
        minuteDegrees = minutePosition / self.MINUTE_HAND_STEPS_PER_REVOLUTION * 360

        # Subtracting 360 because degrees go the other way than the clock is moving
        return abs(hourDegrees - 360) % 360, abs((minuteDegrees % 360) - 360)

    def degreesToSteps(self, degrees, hand):
        """Converts degrees to steps"""
        if hand == self.HOUR_HAND_PIN:
            # Since degrees go counterclockwise and the clock goes clockwise, we need to subtract the degrees from 360
            return (360 - degrees) * self.HOUR_HAND_STEPS_PER_REVOLUTION / 360 % self.HOUR_HAND_STEPS_PER_REVOLUTION

        elif hand == self.MINUTE_HAND_PIN:
            return (360 - degrees) * self.MINUTE_HAND_STEPS_PER_REVOLUTION / 360 % self.MINUTE_HAND_STEPS_PER_REVOLUTION


    def moveToTime(self, hour, minute, second=0, waitFlg=False):
        """Moves the hands to the given time"""
        hourToSteps, minuteToSteps = self.convertTimeToSteps(hour, minute, second)

        # Calculate the steps to move
        _successFlg, hourPosition = self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN)
        _successFlg, minutePosition = self.dpiStepper.getCurrentPositionInSteps(self.MINUTE_HAND_PIN)

        hourDifference = hourToSteps - hourPosition % self.HOUR_HAND_STEPS_PER_REVOLUTION
        minuteDifference = minuteToSteps - minutePosition % self.MINUTE_HAND_STEPS_PER_REVOLUTION

        self.moveToPositionsRelative(hourDifference, minuteDifference, waitFlg)


    def emergencyStop(self):
        """Stops both hands"""
        self.dpiStepper.emergencyStop(self.HOUR_HAND_PIN)
        self.dpiStepper.emergencyStop(self.MINUTE_HAND_PIN)

    def moveToPositionDegrees(self, hourDegrees=None, minuteDegrees=None, waitFlg=True):
        """Moves the hands to the given positions in degrees"""
        self.refreshSteps()

        if hourDegrees is not None:
            hourToSteps = self.degreesToSteps(hourDegrees + self.HOUR_HAND_OFFSET, self.HOUR_HAND_PIN)
            self.dpiStepper.moveToAbsolutePositionInSteps(self.HOUR_HAND_PIN, int(hourToSteps), waitFlg)

        if minuteDegrees is not None:
            minuteToSteps = self.degreesToSteps(minuteDegrees, self.MINUTE_HAND_PIN)
            self.dpiStepper.moveToAbsolutePositionInSteps(self.MINUTE_HAND_PIN, int(minuteToSteps), waitFlg)


    def refreshSteps(self):

        hourDegrees, minuteDegrees = self.getPositionDegrees()
        hourSteps, minuteSteps = self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN)[0], self.dpiStepper.getCurrentPositionInSteps(self.MINUTE_HAND_PIN)[0]

        if hourDegrees >= 360:
            hourSteps = hourSteps % self.HOUR_HAND_STEPS_PER_REVOLUTION
            self.dpiStepper.setCurrentPositionInSteps(self.HOUR_HAND_PIN, hourSteps)

        if minuteDegrees >= 360:
            minuteSteps = minuteSteps % self.MINUTE_HAND_STEPS_PER_REVOLUTION
            self.dpiStepper.setCurrentPositionInSteps(self.MINUTE_HAND_PIN, minuteSteps)
