#      ******************************************************************
#      *                                                                *
#      *                      Main ClockNBlock Loop                     *
#      *                                                                *
#      *            Arnav Wadhwa                   12/08/2022           *
#      *                                                                *
#      ******************************************************************
from datetime import datetime
import signal
import sys
sys.path.insert(0, '..')

from main.clockHands import Clock
from main.robotArm import RobotArm

from time import sleep


robotMagnetSolenoid = 11
robotRotationSolenoid = 10

clock = Clock()
robot = RobotArm(robotMagnetSolenoid, robotRotationSolenoid)

blockFeeders = robot.blockFeeders

NUM_BLOCK_FEEDERS = robot.NUM_BLOCK_FEEDERS


def setup():

    # Call setup functions for each component
    robot.setup()
    clock.setup()
    for i in range(NUM_BLOCK_FEEDERS):
        blockFeeders[i].setup()

    # Move to current time
    currentTime = datetime.now().strftime("%H:%M")
    print(f"moving to current time which is {currentTime}")
    time = currentTime.replace(':', '')
    time = int(time)
    clock.moveToTime(time)
    clock.dpiStepper.waitUntilMotorStops(1)
    clock.dpiStepper.waitUntilMotorStops(0)



def exit_handler():
    robot.dpiRobot.disableMotors()


def main():

    setup()

    print("moving on to loop")
    while True:

        for i in range(NUM_BLOCK_FEEDERS):
            blockFeeders[i].process()
        clock.process()
        robot.process(clock.getPositionRadians(1), clock.getPositionRadians(0))  # Minute, hour hand
        sleep(0.01)
        signal.signal(signal.SIGTERM, (lambda signum, frame: exit_handler()))
        signal.signal(signal.SIGINT, (lambda signum, frame: exit_handler()))


if __name__ == "__main__":
    main()



