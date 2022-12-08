#      ******************************************************************
#      *                                                                *
#      *                      Main ClockNBlock Loop                     *
#      *                                                                *
#      *            Arnav Wadhwa                   12/0382022           *
#      *                                                                *
#      ******************************************************************


from main.clockHands import Clock
from main.blockFeeder import BlockFeeder
from main.robotArm import RobotArm

import time
from time import sleep

# TODO: Maybe make this an object. I don't think it is necessary though

# Setup all of our components
clock = Clock()
robot = RobotArm()

# For the ClockNBlock boards
structure0 = BlockFeeder(6, 7, 0)
structure1 = BlockFeeder(4, 3, 1)
structure2 = BlockFeeder(9, 8, 2)
structure3 = BlockFeeder(0, 1, 3)
# Not sure if this array is needed, might come in handy though
structures = [structure0, structure1, structure2, structure3]


def setup():

    # Call setup functions for each component
    clock.setup()
    robot.setup()
    for i in range(0, 3):
        structures[i].setup()


def main():

    setup()

    while(True):

        for i in range(0,3):
            structures[i].state()

        # TODO: Implement these

        # clock.state()

        # Note: I will probably put the "tool pathing" function inside the robot class rather than here
        # robot.state()


if __name__ == "__main__":
    main()



