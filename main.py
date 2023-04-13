""" Main file for the project. Sets up all global objects and runs the Objects loop."""
from time import sleep

from dpeaDPi.DPiSolenoid import DPiSolenoid

import Objects.constants as constants
from Objects.robotArm import RobotArm
from Objects.buildSite import BuildSite
from Objects.blockFeeder import BlockFeeder
from Objects.clock import Clock


# Create the DPiSolenoid object since it is referenced by multiple objects
dpiSolenoid = DPiSolenoid()

dpiSolenoid.setBoardNumber(0)

if not dpiSolenoid.initialize():
    raise Exception("Solenoid initialization failed")


buildSites = []
for idx, location in enumerate(constants.buildLocations):
    buildSites.append(BuildSite(idx, location[0], location[1]))

blockFeeders = []
for num, blockFeederInfo in enumerate(zip(constants.blockFeederLocations, constants.blockFeederSolenoids)):
    blockFeeders.append(BlockFeeder(blockFeederInfo[0], blockFeederInfo[1], num, dpiSolenoid))


clock = Clock()


# Create the robot arm object
robot = RobotArm(dpiSolenoid, constants.magnetSolenoid, constants.rotationSolenoid, buildSites, blockFeeders)


def setup():

    if not robot.setup():
        raise Exception("Robot setup failed")

    # Set up part 1 of the clock
    if not clock.setup():
        raise Exception("Clock setup failed")

    # Set up block feeders
    for blockFeeder in blockFeeders:
        if not blockFeeder.setup():
            raise Exception("Block feeder setup failed")

    # Set up clock part 2
    if not clock.setup2():
        raise Exception("Clock setup 2 failed")

    main()


def main():
    while True:
        # Process all  the loops
        if robot.isHomedFlg:
            clock.process()
            hourPos, minutePos = clock.getPositionDegrees()

            robot.process(minutePos)

            [blockFeeder.process(minutePos) for blockFeeder in blockFeeders]
            [buildSite.process(minutePos) for buildSite in buildSites]

        # Read for when the E-Stop gets released
        elif robot.dpiRobot.getRobotStatus()[1] != robot.dpiRobot.STATE_NOT_HOMED:
            clock.emergencyStop()
            sleep(0.1)

        else:
            setup()



if __name__ == '__main__':
    setup()







