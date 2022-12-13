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

from time import sleep

#
# pin assignments show how the pistons are wired to the DPiSolenoid board
#
_BLOCK_FEEDER0__FIRST_PISTON__DRIVER_NUM    = 6
_BLOCK_FEEDER0__SECOND_PISTON__DRIVER_NUM   = 7
_BLOCK_FEEDER1__FIRST_PISTON__DRIVER_NUM    = 4
_BLOCK_FEEDER1__SECOND_PISTON__DRIVER_NUM   = 3
_BLOCK_FEEDER2__FIRST_PISTON__DRIVER_NUM    = 9
_BLOCK_FEEDER2__SECOND_PISTON__DRIVER_NUM   = 8
_BLOCK_FEEDER3__FIRST_PISTON__DRIVER_NUM    = 0
_BLOCK_FEEDER3__SECOND_PISTON__DRIVER_NUM   = 1

_NUMBER_OF_BLOCK_FEEDERS    = 4

# For the ClockNBlock boards
blockFeeder0 = BlockFeeder(_BLOCK_FEEDER0__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER0__SECOND_PISTON__DRIVER_NUM, 0)
blockFeeder1 = BlockFeeder(_BLOCK_FEEDER1__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER1__SECOND_PISTON__DRIVER_NUM, 1)
blockFeeder2 = BlockFeeder(_BLOCK_FEEDER2__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER2__SECOND_PISTON__DRIVER_NUM, 2)
blockFeeder3 = BlockFeeder(_BLOCK_FEEDER3__FIRST_PISTON__DRIVER_NUM, _BLOCK_FEEDER3__SECOND_PISTON__DRIVER_NUM, 3)
# Not sure if this array is needed, might come in handy though
blockFeeders = [blockFeeder0, blockFeeder1, blockFeeder2, blockFeeder3]

robotMagnetSolenoid = 11
robotRotationSolenoid = 10

clock = Clock()
robot = RobotArm(robotMagnetSolenoid, robotRotationSolenoid)


def setup():

    # Call setup functions for each component
    robot.setup()
    # clock.setup()

    blockFeeders[0].setup()
    print("done with setup")
    # for i in range(0, 3):
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



