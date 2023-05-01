from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiStepper import DPiStepper
from time import sleep

dpiRobot = DPiRobot()
dpiRobot.setBoardNumber(0)

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
MINUTE_HAND_STEPS_PER_REVOLUTION = int(200 * MICROSTEPPING * MINUTE_HAND_GEAR_REDUCTION * 1.002)  # 327052
# Base minute hand speed, 1 revolution per hour, about 90.8 steps per second
MINUTE_HAND_BASE_SPEED = MINUTE_HAND_STEPS_PER_REVOLUTION / (60 * 60)
MINUTE_HAND_MAX_SPEED = 20000
MINUTE_HAND_ACCELERATION = MINUTE_HAND_MAX_SPEED // 4

if not dpiRobot.initialize():
    print("Failed to initialize robot")
    exit()

dpiStepper = DPiStepper()
dpiStepper.setBoardNumber(0)
if not dpiStepper.initialize():
    print("Failed to initialize stepper")
    exit()


def main():

    if not dpiRobot.homeRobot(True):
        raise Exception("Failed to home robot")

    dpiStepper.setMicrostepping(MICROSTEPPING)
    dpiStepper.enableMotors(True)

    dpiStepper.setAccelerationInStepsPerSecondPerSecond(HOUR_HAND_PIN, HOUR_HAND_ACCELERATION)
    dpiStepper.setAccelerationInStepsPerSecondPerSecond(MINUTE_HAND_PIN, MINUTE_HAND_ACCELERATION)

    dpiStepper.setSpeedInStepsPerSecond(HOUR_HAND_PIN, HOUR_HAND_MAX_SPEED)
    dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND_PIN, MINUTE_HAND_MAX_SPEED)

    dpiStepper.moveToHomeInSteps(HOUR_HAND_PIN, 1, HOUR_HAND_MAX_SPEED, HOUR_HAND_STEPS_PER_REVOLUTION)
    dpiStepper.moveToHomeInSteps(MINUTE_HAND_PIN, 1, MINUTE_HAND_MAX_SPEED, MINUTE_HAND_STEPS_PER_REVOLUTION)

    while not dpiStepper.getAllMotorsStopped():
        sleep(0.1)


    dpiStepper.setSpeedInStepsPerSecond(MINUTE_HAND_PIN, MINUTE_HAND_BASE_SPEED)

    while True:
        if dpiStepper.getStepperStatus(MINUTE_HAND_PIN)[1]:
            print('Moving stopped minute hand')
            dpiStepper.moveToRelativePositionInSteps(MINUTE_HAND_PIN, MINUTE_HAND_STEPS_PER_REVOLUTION, False)

        print(f'Minute hand speed: {dpiStepper.getCurrentVelocityInStepsPerSecond(MINUTE_HAND_PIN)}')


if __name__ == '__main__':
    main()



