#      ******************************************************************
#      *                                                                *
#      *                      Main ClockNBlock Loop                     *
#      *                                                                *
#      *            Arnav Wadhwa                   12/08/2022           *
#      *                                                                *
#      ******************************************************************
import sys
sys.path.insert(0, '/home/pi/projects/clockNBlock2022/')

from main.robotArm import RobotArm

# Constants for setup

robotMagnetSolenoid = 11
robotRotationSolenoid = 10

robot = RobotArm(robotMagnetSolenoid, robotRotationSolenoid)

hands = robot.hands
blockFeeders = robot.blockFeeders

NUM_BLOCK_FEEDERS = robot.NUM_BLOCK_FEEDERS


def setup():

    # Call setup functions for each component
    if not robot.setup():
        raise Exception("Robot setup failed")

    if not hands.setup():
        raise Exception("Hands setup failed")
    for i in range(NUM_BLOCK_FEEDERS):
        # print(f"setup blockfeeder {i}")
        if not blockFeeders[i].setup():
            raise Exception(f"BlockFeeder {i} setup failed")

    hands.dpiStepper.moveToRelativePositionInSteps(1, 326400, False)
    hands.dpiStepper.waitUntilMotorStops(1)
    hands.setSpeedBoth(hands.POINTER_BASE_SPEED, round(hands.KNOCKER_BASE_SPEED))


# Main loop where all of the individual state functions are called.
def main():

    setup()

    # print("moving on to loop")
    while robot.isHomedFlg:
        # Call state functions
        for i in range(NUM_BLOCK_FEEDERS):
            blockFeeders[i].process()
        hands.process()
        robot.process(hands.getPositionRadians()[1])

        setup()


# Run script
if __name__ == "__main__":
    main()



