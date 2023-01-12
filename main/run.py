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

from main.robotArm import RobotArm

robotMagnetSolenoid = 11
robotRotationSolenoid = 10

robot = RobotArm(robotMagnetSolenoid, robotRotationSolenoid)

hands = robot.hands
blockFeeders = robot.blockFeeders

NUM_BLOCK_FEEDERS = robot.NUM_BLOCK_FEEDERS


def setup():

    # Call setup functions for each component
    # print("setup robo")
    robot.setup()
    hands.setup()
    for i in range(NUM_BLOCK_FEEDERS):
        # print(f"setup blockfeeder {i}")
        blockFeeders[i].setup()

    hands.dpiStepper.moveToRelativePositionInSteps(1, 326400, False)
    hands.dpiStepper.waitUntilMotorStops(1)
    hands.setSpeedBoth(hands.POINTER_BASE_SPEED, round(hands.KNOCKER_BASE_SPEED))


def exit_handler():
    robot.dpiRobot.waitWhileRobotIsMoving()
    robot.dpiRobot.homeRobot(True)
    hands.dpiStepper.enableMotors(False)


def main():

    setup()

    # print("moving on to loop")
    while True:

        for i in range(NUM_BLOCK_FEEDERS):
            blockFeeders[i].process()
        hands.process()
        robot.process(hands.getPositionRadians()[1], hands.getPositionRadians()[0])  # Minute, hour hand
        # Runs exit handler when program stops(only works sometimes)
        signal.signal(signal.SIGTERM, (lambda signum, frame: exit_handler()))
        signal.signal(signal.SIGINT, (lambda signum, frame: exit_handler()))


if __name__ == "__main__":
    main()



