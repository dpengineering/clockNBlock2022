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
    # print("setup robo")
    robot.setup()
    hands.setup()
    for i in range(NUM_BLOCK_FEEDERS):
        # print(f"setup blockfeeder {i}")
        blockFeeders[i].setup()

    hands.dpiStepper.moveToRelativePositionInSteps(1, 326400, False)
    hands.dpiStepper.waitUntilMotorStops(1)
    hands.setSpeedBoth(hands.POINTER_BASE_SPEED, round(hands.KNOCKER_BASE_SPEED))



# Main loop where all of the individual state functions are called.
def main():

    setup()

    # print("moving on to loop")
    while True:
        # Call state functions
        for i in range(NUM_BLOCK_FEEDERS):
            blockFeeders[i].process()
        hands.process()
        robot.process(hands.getPositionRadians()[1], hands.getPositionRadians()[0])  # Minute, hour hand


# Run script
if __name__ == "__main__":
    main()



