#      ******************************************************************
#      *                                                                *
#      *                      Main ClockNBlock Loop                     *
#      *                                                                *
#      *            Arnav Wadhwa                   12/08/2022           *
#      *                                                                *
#      ******************************************************************


from clockHands import Clock
from robotArm import RobotArm

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
    # clock.setup()

    # for i in range(NUM_BLOCK_FEEDERS):
    #     blockFeeders[i].setup()
    blockFeeders[0].setup()
    # blockFeeders[2].setup()
    blockFeeders[3].setup()



def main():

    setup()

    print("moving on to loop")
    while True:

        # for i in range(NUM_BLOCK_FEEDERS):
            # blockFeeders[i].process()
        blockFeeders[0].process()
        # blockFeeders[2].process()
        blockFeeders[3].process()
        clock.process()
        # robot.process(clock.getPositionRadians(1))  # Minute hand

        sleep(0.5)


if __name__ == "__main__":
    main()



