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
    for i in range(NUM_BLOCK_FEEDERS):
        print(f"setup blockfeeder {i}")
        if not blockFeeders[i].setup():
            raise Exception(f"BlockFeeder {i} setup failed")


def main():

    setup()

    while True:
        for i in range(NUM_BLOCK_FEEDERS):
            print(f'Running blockfeeder {i}')
            blockFeeders[i].process()


if __name__ == "__main__":
    main()



