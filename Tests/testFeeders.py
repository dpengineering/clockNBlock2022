# Test program that runs all the feeders continuously

# To import the from other folders in project
import sys
sys.path.insert(0, "..")

from main.robotArm import RobotArm

robotMagnetSolenoid = 11
robotRotationSolenoid = 10

robot = RobotArm(robotMagnetSolenoid, robotRotationSolenoid)

blockFeeders = robot.blockFeeders

NUM_BLOCK_FEEDERS = robot.NUM_BLOCK_FEEDERS


def setup():
    print("Setting up feeders")
    for i in range(NUM_BLOCK_FEEDERS):
        blockFeeders[i].setup()


def main():

    setup()

    while True:

        for i in range(NUM_BLOCK_FEEDERS):
            blockFeeders[i].process()


if __name__ == "__main__":
    main()



