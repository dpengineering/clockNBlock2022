#      ******************************************************************
#      *                                                                *
#      *                Hands (Clock Hands) Object                      *
#      *                                                                *
#      *            Arnav Wadhwa                   12/03/2022           *
#      *                                                                *
#      ******************************************************************

import math
from dpeaDPi.DPiStepper import DPiStepper
from time import sleep

import sys
sys.path.insert(0, '..')


# Placeholder name for now
class Hands:
    """Controls the hands through the DPi_Stepper board

    This version has the red hand as a pointer and the yellow hand as the knocker
    """

    dpiStepper = DPiStepper()

    # Motor Constants
    MICROSTEPPING = 8

    POINTER_GEAR_REDUCTION = 5  # Gear reduction is 5:1
    # I am not sure why there is 300 extra steps for a full rotation.
    POINTER_STEPS_PER_REVOLUTION = 200 * MICROSTEPPING * POINTER_GEAR_REDUCTION + 300  # 8300
    # Pointer hand base speed, 1660 steps/sec
    POINTER_BASE_SPEED = int(POINTER_STEPS_PER_REVOLUTION)
    # Pointer hand max speed. I don't feel comfortable sending it more than 0.5 rev / sec - 4150 steps/sec
    POINTER_MAX_SPEED = int(POINTER_STEPS_PER_REVOLUTION / 2)

    KNOCKER_GEAR_REDUCTION = 204  # Gear reduction is 204:1
    KNOCKER_STEPS_PER_REVOLUTION = int(200 * MICROSTEPPING * KNOCKER_GEAR_REDUCTION * 0.998)  # 326400
    # Base knocker speed, 1 revolution in 16 minutes ~ 467 steps/sec
    KNOCKER_BASE_SPEED = KNOCKER_STEPS_PER_REVOLUTION / 700
    KNOCKER_MAX_SPEED = 20000

    pointerDitherState = 0

    def __init__(self, pointer=0, knocker=1):
        """Constructor for hands
        Does nothing, just creates the object
        """
        self.POINTER = pointer
        self.KNOCKER = knocker
        self.currentPointerSpeed = self.POINTER_BASE_SPEED
        self.currentKnockerSpeed = self.KNOCKER_BASE_SPEED
        return

    def process(self):
        """State machine for the hands"""

        if not self.isStepperMoving(self.KNOCKER):
            # print("moving minute hand")
            self.dpiStepper.moveToRelativePositionInSteps(self.KNOCKER, self.KNOCKER_STEPS_PER_REVOLUTION, False)

        return

    def processPointer(self, pos: float):
        """State machine for the pointer
        These are individual state machines to make the code a slight bit cleaner

        The state for the pointer will be reliant on the Robot state
        """

        if self.pointerDitherState == 0:
            # Speed value is arbitrary, more testing needed
            self.setSpeed(self.POINTER, int(self.POINTER_MAX_SPEED / 3))
            self.moveToPosRadians(self.POINTER, pos - 0.25)
            self.pointerDitherState += 1
            return

        # Sulk back to right before our position slowly
        elif self.pointerDitherState == 1:
            self.setSpeed(self.POINTER, int(self.POINTER_BASE_SPEED / 2))
            self.moveToPosRadians(self.POINTER, pos + 0.1)
            self.pointerDitherState += 1
            return

        # Dither slowly to the correct position at base speed
        elif self.pointerDitherState == 2:
            self.setSpeed(self.POINTER, self.POINTER_BASE_SPEED)
            self.moveToPosRadians(self.POINTER, pos - 0.75)
            self.pointerDitherState += 1
            return

        elif self.pointerDitherState == 3:
            self.setSpeed(self.POINTER, self.POINTER_BASE_SPEED)
            self.moveToPosRadians(self.POINTER, pos + 0.5)
            self.pointerDitherState += 1
            return

        elif self.pointerDitherState == 4:
            self.setSpeed(self.POINTER, self.POINTER_BASE_SPEED)
            self.moveToPosRadians(self.POINTER, pos - 0.25)
            self.pointerDitherState += 1
            return

        elif self.pointerDitherState == 5:
            self.setSpeed(self.POINTER, self.POINTER_BASE_SPEED)
            self.moveToPosRadians(self.POINTER, pos)
            self.pointerDitherState = -1
            return
        # Once we are there, do nothing
        else:
            return

    # Sets up hands
    def setup(self):
        """Sets up hands to can be used
        Moves to the "0" position when done
        """
        # print("setup")
        self.dpiStepper.setBoardNumber(0)

        if not self.dpiStepper.initialize():
            # print("Communication with the DPiStepper board failed.")
            return

        self.dpiStepper.setMicrostepping(self.MICROSTEPPING)

        self.dpiStepper.enableMotors(True)
        # print("homing")
        self.home()

    def home(self):
        """Helper function to home the hands and move them to the 0 position"""
        # Move to limit switches
        # print("Home pointer hand")
        self.dpiStepper.moveToHomeInSteps(self.POINTER, 1, self.POINTER_MAX_SPEED, self.POINTER_STEPS_PER_REVOLUTION)
        # print("Home knocker hand")
        self.dpiStepper.moveToHomeInSteps(self.KNOCKER, 1, self.KNOCKER_MAX_SPEED, self.KNOCKER_STEPS_PER_REVOLUTION)

        self.dpiStepper.waitUntilMotorStops(self.POINTER)
        self.dpiStepper.waitUntilMotorStops(self.KNOCKER)
        # print("done homing")

        self.setSpeedBoth(self.POINTER_MAX_SPEED, self.KNOCKER_MAX_SPEED)

        # Go to 0 Position
        # print("moving to 0")
        self.dpiStepper.moveToRelativePositionInSteps(self.KNOCKER, -81100, False)
        self.dpiStepper.moveToRelativePositionInSteps(self.POINTER, 2025, False)

        while not self.dpiStepper.getAllMotorsStopped():
            sleep(0.1)

        self.dpiStepper.setCurrentPositionInSteps(self.KNOCKER, 0)
        self.dpiStepper.setCurrentPositionInSteps(self.POINTER, 0)
        # print("done")

    def setSpeed(self, hand: int, speed: int):
        """Helper function to set the speed of one motor

        Args:
            speed: Speed and acceleration for motor
        """
        self.dpiStepper.setSpeedInStepsPerSecond(hand, speed)
        self.dpiStepper.setAccelerationInStepsPerSecondPerSecond(hand, speed)

    def setSpeedBoth(self, speed0: int, speed1: int):
        """Helper function to set the speeds of the motors

        Args:
            speed0: Speed and acceleration for pointer
            speed1: Speed and acceleration for knocker
        """
        self.setSpeed(0, speed0)
        self.setSpeed(1, speed1)

    def isStepperMoving(self, hand: int):
        """Helper function to check if steppers are moving

        Args:
            hand: which motor to check

        Returns:
            True if moving otherwise false.
        """
        return not self.dpiStepper.getStepperStatus(hand)[1]

    def getPositionSteps(self, hand: int):
        """Helper function to get position of stepper

        Args:
            hand: which motor to check

        Returns:
            Steps of hand
        """
        return self.dpiStepper.getCurrentPositionInSteps(hand)[1]

    def getPositionRadians(self) -> (float, float):
        """Helper function to give hand positions in radians

        Returns:
            tuple (float, float): pointerPos, knockerPos
        """

        pointerPos = self.getPositionSteps(0)
        knockerPos = self.getPositionSteps(1)

        pointerRad = 2 * math.pi * (pointerPos / self.POINTER_STEPS_PER_REVOLUTION)
        knockerRad = 2 * math.pi * (knockerPos / self.KNOCKER_STEPS_PER_REVOLUTION)

        # print(f'pointer: {round(pointerRad, 3)}, Knocker {round(knockerRad, 3)}')
        return round(-pointerRad, 3), round(-knockerRad, 3)

    def moveToPosRadians(self, hand: int, pos: float):
        """Moves hand to a position in radians"""

        # # Does the inverse of getPositionRadians
        # if hand == self.POINTER:
        #     steps = self.POINTER_STEPS_PER_REVOLUTION - (pos * self.POINTER_STEPS_PER_REVOLUTION) / 2 * math.pi
        # else:
        #     steps = self.KNOCKER_STEPS_PER_REVOLUTION - (pos * self.KNOCKER_STEPS_PER_REVOLUTION) / 2 * math.pi

        # Does the inverse of getPositionRadians
        # if hand == self.POINTER:
        #     steps = -pos * self.POINTER_STEPS_PER_REVOLUTION / 2 * math.pi
        # else:
        #     steps = -pos * self.KNOCKER_STEPS_PER_REVOLUTION / 2 * math.pi

        # If that doesn't work:
        # Does the inverse of getPositionRadians
        if hand == self.POINTER:
            steps = -pos * self.POINTER_STEPS_PER_REVOLUTION / (2 * math.pi) % self.POINTER_STEPS_PER_REVOLUTION
        else:
            steps = -pos * self.KNOCKER_STEPS_PER_REVOLUTION / (2 * math.pi) % self.KNOCKER_STEPS_PER_REVOLUTION

        # print(f'Moving {hand} to {round(steps)}')
        self.dpiStepper.moveToAbsolutePositionInSteps(hand, round(steps), False)

    def waitForHandsStopped(self):
        """Helper function that busy-waits until both hands are stopped
            Mostly used for testing"""

        self.dpiStepper.waitUntilMotorStops(self.POINTER)
        self.dpiStepper.waitUntilMotorStops(self.KNOCKER)

    # This is probably going to be quite jerky, will test more
    def followKnocker(self):
        """Helper function to send the pointer to the knocker"""
        pos = self.getPositionRadians()[1]

        self.setSpeed(self.POINTER, self.POINTER_MAX_SPEED)
        self.moveToPosRadians(self.POINTER, pos)

