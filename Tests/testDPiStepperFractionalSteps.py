# Quick test for DPi Stepper board, to make sure I'm not doing something wrong.
# I'll still write the fix for this, just making sure to tell Stan

from dpeaDPi.DPiStepper import DPiStepper

dpiStepper = DPiStepper()

MICROSTEPPING = 8
# Some constants, not all of them will be used
HOUR_HAND_PIN = 0
HOUR_HAND_GEAR_REDUCTION = 5  # Gear reduction is 5:1
# I am not sure why there is 300 extra steps for a full rotation.
HOUR_HAND_STEPS_PER_REVOLUTION = 200 * MICROSTEPPING * HOUR_HAND_GEAR_REDUCTION + 290  # 8300
# Hour hand base speed, 1 revolution in 12 hours, about 0.19 steps per second
HOUR_HAND_BASE_SPEED = HOUR_HAND_STEPS_PER_REVOLUTION / (12 * 60 * 60)
# Hour hand max speed. I don't feel comfortable sending it more than 0.5 rev / sec - 4150 steps/sec
HOUR_HAND_MAX_SPEED = int(HOUR_HAND_STEPS_PER_REVOLUTION / 2)
HOUR_HAND_ACCELERATION = HOUR_HAND_MAX_SPEED // 4


# Begin testing
def main():
    dpiStepper.setBoardNumber(0)

    if not dpiStepper.initialize():
        raise Exception("Stepper initialization failed")

    dpiStepper.setMicrostepping(MICROSTEPPING)

    # Home the hour hand
    dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND_PIN, HOUR_HAND_MAX_SPEED)

    dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND_PIN, HOUR_HAND_ACCELERATION)

    dpiStepper.moveToHomeInSteps(HOUR_HAND_PIN, 1, HOUR_HAND_MAX_SPEED, HOUR_HAND_STEPS_PER_REVOLUTION)

    # Set speed to base speed
    dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND_PIN, HOUR_HAND_BASE_SPEED)

    # Send it in a full rotation
    dpiStepper.moveToRelativePositionInSteps(HOUR_HAND_PIN, HOUR_HAND_STEPS_PER_REVOLUTION, True)


if __name__ == "__main__":
    main()

