# Test program that runs all the feeders continuously

# To import from other folders in project
import sys
sys.path.insert(0, "..")

from main.robotArm import RobotArm

robotMagnetSolenoid = 11
robotRotationSolenoid = 10

robot = RobotArm(robotMagnetSolenoid, robotRotationSolenoid)

blockFeeders = robot.blockFeeders

NUM_BLOCK_FEEDERS = robot.NUM_BLOCK_FEEDERS


def setup():
    print("Setting up feeder 0")
    blockFeeders[0].setup()


def main():

    setup()

    while True:
        blockFeeders[0].process()


if __name__ == "__main__":
    main()



