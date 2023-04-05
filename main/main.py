""" Main file for the project. Sets up all global objects and runs the main loop."""
from dpeaDPi.DPiSolenoid import DPiSolenoid

import constants
from robotArm import RobotArm
from buildSite import BuildSite
from blockFeeder import BlockFeeder


# Create the DPiSolenoid object since it is referenced by multiple objects
dpiSolenoid = DPiSolenoid()

dpiSolenoid.setBoardNumber(0)

if not dpiSolenoid.initialize():
    raise Exception("Solenoid initialization failed")

# Create the robot arm object

robot = RobotArm(dpiSolenoid, constants.magnetSolenoid, constants.rotationSolenoid)

buildSites = []
for location in constants.buildLocations:
    buildSites.append(BuildSite(location[0], location[1]))

blockFeeders = []
for blockFeederInfo in zip(constants.blockFeederLocations, constants.blockFeederSolenoids, constants.clockNBlockBoards):
    blockFeeders.append(BlockFeeder(blockFeederInfo[0], blockFeederInfo[1], blockFeederInfo[2]))



