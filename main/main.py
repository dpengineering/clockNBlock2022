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
    print("setup robo")
    robot.setup()

    for i in range(NUM_BLOCK_FEEDERS):
        print(f"setup blockfeeder {i}")
        blockFeeders[i].setup()
    print("setup clock")
    clock.setup()


def main():

    setup()

    print("moving on to loop")
    while True:

        for i in range(NUM_BLOCK_FEEDERS):
            blockFeeders[i].process()
        clock.process()
        robot.process(clock.getPositionRadians(1))  # Minute hand
        sleep(0.01)


if __name__ == "__main__":
    main()



