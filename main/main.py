#      ******************************************************************
#      *                                                                *
#      *                      Main ClockNBlock Loop                     *
#      *                                                                *
#      *            Arnav Wadhwa                   12/0382022           *
#      *                                                                *
#      ******************************************************************


from clockHands import Clock
from blockFeeder import BlockFeeder
from robotArm import RobotArm
from blockManager import BlockManager

from time import sleep


robotMagnetSolenoid = 11
robotRotationSolenoid = 10

clock = Clock()
robot = RobotArm(robotMagnetSolenoid, robotRotationSolenoid)
blockManager = BlockManager()

# Grab blockFeeder array from blockManager
blockFeeders = blockManager.blockFeeders
_NUM_BLOCK_FEEDERS = len(blockFeeders)


def setup():

    # Call setup functions for each component
    robot.setup()
    clock.setup()

    blockFeeders[0].setup()
    print("done with setup")
    # for i in range(_NUM_BLOCK_FEEDERS):
    #     structures[i].setup()


def main():

    setup()

    print("moving on to loop")
    while True:

        blockFeeders[0].process()
        print(blockFeeders[0].state)
        sleep(0.5)


if __name__ == "__main__":
    main()



