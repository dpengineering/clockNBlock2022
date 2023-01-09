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

from main.hands import Hands
from main.robotArm import RobotArm

robotMagnetSolenoid = 11
robotRotationSolenoid = 10

hands = Hands()
robot = RobotArm(robotMagnetSolenoid, robotRotationSolenoid)

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


def exit_handler():
    robot.dpiRobot.homeRobot()
    robot.dpiRobot.addWaypoint(0, 20, 0)
    robot.dpiRobot.disableMotors()
    hands.dpiStepper.emergencyStop(0)
    hands.dpiStepper.emergencyStop(1)


def main():

    setup()

    # print("moving on to loop")
    while True:

        for i in range(NUM_BLOCK_FEEDERS):
            blockFeeders[i].process()
        hands.process(robot)
        robot.process(hands.getPositionRadians()[1], hands.getPositionRadians()[0])  # Minute, hour hand
        # Runs exit handler when program stops(only works sometimes)
        signal.signal(signal.SIGTERM, (lambda signum, frame: exit_handler()))
        signal.signal(signal.SIGINT, (lambda signum, frame: exit_handler()))


if __name__ == "__main__":
    main()



