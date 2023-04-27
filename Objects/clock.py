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
    # Hour hand base speed, 1 revolution in 12 hours, about 0.19 steps per second
    HOUR_HAND_BASE_SPEED = HOUR_HAND_STEPS_PER_REVOLUTION / (12 * 60 * 60)
    # Hour hand max speed. I don't feel comfortable sending it more than 0.5 rev / sec - 4150 steps/sec
    HOUR_HAND_MAX_SPEED = int(HOUR_HAND_STEPS_PER_REVOLUTION / 2)
    HOUR_HAND_ACCELERATION = HOUR_HAND_MAX_SPEED // 4

    # Hour Hand offset, not sure why this is needed...
    HOUR_HAND_OFFSET = 6.3  # degrees

    MINUTE_HAND_PIN = 1
    MINUTE_HAND_GEAR_REDUCTION = 204  # Gear reduction is 204:1
    MINUTE_HAND_STEPS_PER_REVOLUTION = int(200 * MICROSTEPPING * MINUTE_HAND_GEAR_REDUCTION * 1.002)  # 326400
    # Base minute hand speed, 1 revolution per hour, about 90.6 steps per second
    MINUTE_HAND_BASE_SPEED = MINUTE_HAND_STEPS_PER_REVOLUTION / (60 * 60)
    MINUTE_HAND_MAX_SPEED = 20000
    MINUTE_HAND_ACCELERATION = MINUTE_HAND_MAX_SPEED // 4

    # TODO: Ask Stan what's up with this

    def __init__(self):
        self.initialize()
        self.robotIdleFlg = False

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
        self.dpiStepper.moveToHomeInSteps(self.HOUR_HAND_PIN, 1, self.HOUR_HAND_MAX_SPEED,
                                          self.HOUR_HAND_STEPS_PER_REVOLUTION)

        self.dpiStepper.moveToHomeInSteps(self.MINUTE_HAND_PIN, 1, self.MINUTE_HAND_MAX_SPEED,
                                          self.MINUTE_HAND_STEPS_PER_REVOLUTION)

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
        # Move to current time
        t = localtime()
        hourToSteps, minuteToSteps = self.convertTimeToSteps(t.tm_hour, t.tm_min, t.tm_sec)
        print(f'Hour: {t.tm_hour}, Minute: {t.tm_min}, Second: {t.tm_sec}')
        print(f'Hour Steps: {hourToSteps}, Minute Steps: {minuteToSteps}')
        self.moveToPositionsRelative(hourToSteps, minuteToSteps, waitFlg=True)
        print(f'Finished moving to current time')
        print(f'Current Hour Position: {self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN)}')
        print(f'Target Hour Position: {hourToSteps}')

        # Set base speeds
        print(self.setSpeeds(self.HOUR_HAND_BASE_SPEED, self.MINUTE_HAND_BASE_SPEED))
        print(f'Minute Hand Base Speed: {self.MINUTE_HAND_BASE_SPEED}')

        # Set minute hand going for a revolution
        # self.moveToPositionsRelative(minuteHandPosition=self.MINUTE_HAND_STEPS_PER_REVOLUTION)

        return True

    def process(self):
        """Processes the clock"""
        # This just basically includes checking how far off from the desired position the hands are
        # if they are too far away, then speed/slow them down to get them back to the desired position

        # Note: One case where this will be off is when there is a transfer from 11:59 to 12:00
        # or something along those lines. However, this will be fixed fairly quickly because it will only speed up for around
        # 1 second and then slow down again. This needs to be tested though

        # If the minute hand is stopped, send it going for a revolution

        if self.dpiStepper.getStepperStatus(self.MINUTE_HAND_PIN)[1]:
            print('moving minute hand')
            self.dpiStepper.moveToRelativePositionInSteps(self.MINUTE_HAND_PIN, self.MINUTE_HAND_STEPS_PER_REVOLUTION,
                                                          False)

        # Get current time
        t = localtime()
        hourToSteps, minuteToSteps = self.convertTimeToSteps(t.tm_hour, t.tm_min, t.tm_sec)
        hourToSteps = hourToSteps % self.HOUR_HAND_STEPS_PER_REVOLUTION
        minuteToSteps = minuteToSteps % self.MINUTE_HAND_STEPS_PER_REVOLUTION

        # print(f'Hour: {t.tm_hour}, Minute: {t.tm_min}, Second: {t.tm_sec}')

        # Get current positions
        _successFlg, hourPosition = self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN)
        hourPosition = hourPosition % self.HOUR_HAND_STEPS_PER_REVOLUTION
        _successFlg, minutePosition = self.dpiStepper.getCurrentPositionInSteps(self.MINUTE_HAND_PIN)
        minutePosition = minutePosition % self.MINUTE_HAND_STEPS_PER_REVOLUTION

        # Calculate the difference between the desired position and the current position
        hourDifference = hourToSteps - hourPosition
        # minuteDifference = minuteToSteps - minutePosition

        # print(f'Hour difference: {hourDifference}')
        # print(f'HourToSteps: {hourToSteps}, HourPosition: {hourPosition}')

        # print(f'Minute difference: {minuteDifference}')
        # print(f'MinuteToSteps: {minuteToSteps}, MinutePosition: {minutePosition}')

        # If there is a difference in the hour hand, send it to the desired position
        if hourDifference != 0:
            # print(f'Hour hand is off by {hourDifference} steps')
            self.dpiStepper.moveToRelativePositionInSteps(self.HOUR_HAND_PIN, hourDifference, False)

        print(f'Minute hand speed: {self.dpiStepper.getCurrentVelocityInStepsPerSecond(self.MINUTE_HAND_PIN)}')
        print(f'Minute Hand is off by {minutePosition - minuteToSteps} steps')
        print(f'Minute Hand Position: {minutePosition}, Minute To Steps: {minuteToSteps}')

        # else:
            # print(f'Hour hand is at the correct position')

        # if abs(minuteDifference) > self.MINUTE_HAND_STEPS_PER_REVOLUTION * 0.1:
        #     # print(f'speeding up minute hand by {minuteDifference * 0.01} steps')
        #     self.dpiStepper.setSpeedInStepsPerSecond(self.MINUTE_HAND_PIN,
        #                                              self.MINUTE_HAND_BASE_SPEED + minuteDifference * 0.01)
        # else:
        #     # print(f'setting minute hand speed to {self.MINUTE_HAND_BASE_SPEED}')
        #     self.dpiStepper.setSpeedInStepsPerSecond(self.MINUTE_HAND_PIN, self.MINUTE_HAND_BASE_SPEED)


    #--------------------------------    Helper functions    --------------------------------#


    def setSpeeds(self, hourHandSpeed: float, minuteHandSpeed: float) -> None:
        """Sets the speed of the hands"""
        hourHand = self.dpiStepper.setSpeedInStepsPerSecond(self.HOUR_HAND_PIN, hourHandSpeed)
        minuteHand = self.dpiStepper.setSpeedInStepsPerSecond(self.MINUTE_HAND_PIN, minuteHandSpeed)
        return hourHand and minuteHand

    def moveToPositionsRelative(self, hourHandPosition=None, minuteHandPosition=None, waitFlg=False) -> None:
        """Moves the hands to the given positions"""
        if hourHandPosition is not None:
            self.dpiStepper.moveToRelativePositionInSteps(self.HOUR_HAND_PIN, hourHandPosition, False)

        if minuteHandPosition is not None:
            self.dpiStepper.moveToRelativePositionInSteps(self.MINUTE_HAND_PIN, minuteHandPosition, False)

        if waitFlg:
            while not self.dpiStepper.getAllMotorsStopped():
                sleep(0.1)

    def moveToPositionDegrees(self, hourDegrees=None, minuteDegrees=None, waitFlg=True) -> None:
        """Moves the hands to the given positions in degrees"""

        if hourDegrees is not None:
            hourToSteps = self.degreesToSteps(hourDegrees + self.HOUR_HAND_OFFSET, self.HOUR_HAND_PIN) % self.HOUR_HAND_STEPS_PER_REVOLUTION
            self.dpiStepper.moveToAbsolutePositionInSteps(self.HOUR_HAND_PIN, int(hourToSteps), waitFlg)

        if minuteDegrees is not None:
            minuteToSteps = self.degreesToSteps(minuteDegrees, self.MINUTE_HAND_PIN) % self.MINUTE_HAND_STEPS_PER_REVOLUTION
            self.dpiStepper.moveToAbsolutePositionInSteps(self.MINUTE_HAND_PIN, int(minuteToSteps), waitFlg)

    def moveToTime(self, hour: int, minute: int, second=0, waitFlg=False) -> None:
        """Moves the hands to the given time"""
        hourToSteps, minuteToSteps = self.convertTimeToSteps(hour, minute, second)

        # Calculate the steps to move
        _successFlg, hourPosition = self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN)
        _successFlg, minutePosition = self.dpiStepper.getCurrentPositionInSteps(self.MINUTE_HAND_PIN)

        hourDifference = hourToSteps - hourPosition % self.HOUR_HAND_STEPS_PER_REVOLUTION
        minuteDifference = minuteToSteps - minutePosition % self.MINUTE_HAND_STEPS_PER_REVOLUTION

        self.moveToPositionsRelative(hourDifference, minuteDifference, waitFlg)

    def convertTimeToSteps(self, hour: int, minute: int, second=0) -> tuple:
        """Converts the given time to steps"""
        hourToSteps = hour * self.HOUR_HAND_STEPS_PER_REVOLUTION // 12 + minute * self.HOUR_HAND_STEPS_PER_REVOLUTION // (12 * 60)
        minuteToSteps = minute * self.MINUTE_HAND_STEPS_PER_REVOLUTION // 60 + second * self.MINUTE_HAND_STEPS_PER_REVOLUTION // (60 * 60)

        return hourToSteps, minuteToSteps

    def degreesToSteps(self, degrees: float, hand: int) -> float:
        """Converts degrees to steps"""
        if hand == self.HOUR_HAND_PIN:
            # Since degrees go counterclockwise and the clock goes clockwise, we need to subtract the degrees from 360
            return (360 - degrees) * self.HOUR_HAND_STEPS_PER_REVOLUTION / 360 % self.HOUR_HAND_STEPS_PER_REVOLUTION

        elif hand == self.MINUTE_HAND_PIN:
            return (360 - degrees) * self.MINUTE_HAND_STEPS_PER_REVOLUTION / 360 % self.MINUTE_HAND_STEPS_PER_REVOLUTION

    def getPositionDegrees(self) -> tuple:
        """Gets the position of the hands in degrees"""
        _successFlg, hourPosition = self.dpiStepper.getCurrentPositionInSteps(self.HOUR_HAND_PIN)
        _successFlg, minutePosition = self.dpiStepper.getCurrentPositionInSteps(self.MINUTE_HAND_PIN)

        hourPosition = hourPosition % self.HOUR_HAND_STEPS_PER_REVOLUTION
        minutePosition = minutePosition % self.MINUTE_HAND_STEPS_PER_REVOLUTION

        hourDegrees = (hourPosition / self.HOUR_HAND_STEPS_PER_REVOLUTION) * 360
        minuteDegrees = (minutePosition / self.MINUTE_HAND_STEPS_PER_REVOLUTION) * 360

        # Subtracting 360 because degrees go the other way than the clock is moving
        hourDegrees = 360 - hourDegrees
        minuteDegrees = 360 - minuteDegrees

        return hourDegrees, minuteDegrees

    def emergencyStop(self) -> None:
        """Stops both hands"""
        self.dpiStepper.emergencyStop(self.HOUR_HAND_PIN)
        self.dpiStepper.emergencyStop(self.MINUTE_HAND_PIN)