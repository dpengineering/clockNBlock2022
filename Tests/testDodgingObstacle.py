# Test for dodging obstacle

import sys
from time import sleep
import numpy as np
sys.path.append('../')


from Objects.robotArm import RobotArm
from Objects.buildSite import BuildSite
from Objects.blockFeeder import BlockFeeder
import Objects.constants as constants
from dpeaDPi.DPiSolenoid import DPiSolenoid


# We will directly interface with the robot manager in this test.
# Normally you would never do this.
from Objects.robotManager import RobotManager

# Create the objects
dpiSolenoid = DPiSolenoid()
dpiSolenoid.setBoardNumber(0)
if not dpiSolenoid.initialize():
    raise Exception("Solenoid initialization failed")

robot = RobotArm(dpiSolenoid, magnetSolenoid=constants.magnetSolenoid, rotationSolenoid=constants.rotationSolenoid)

if not robot.setup():
    raise Exception("Robot setup failed")

# 1st build site, there is the most amount of space to build
buildSite = BuildSite(0, constants.buildLocations[1][0], constants.buildLocations[1][1])

if not buildSite.setup():
    raise Exception("Build site setup failed")

# set up all the block feeders
blockFeeders = []
for num, blockFeederInfo in enumerate(zip(constants.blockFeederLocations, constants.blockFeederSolenoids)):
    blockFeeders.append(BlockFeeder(blockFeederInfo[0], blockFeederInfo[1], num, dpiSolenoid))



# Create the robot manager
robotManager = RobotManager([buildSite], blockFeeders)


def main():
    # Stack the bottom layer of the build site to know where the blocks go
    while buildSite.currentBlock < 6:
        robot.process(minuteHandPosition=0)
        [blockFeeder.process() for blockFeeder in blockFeeders]
        # Don't proces the build sites

    # Move the robot to home
    robot.dpiRobot.homeRobot(True)

    # Now that we have stacked the bottom layer, we have 2 minutes to build up to the top
    for i in range(2 * 120):
        print(f'{i} seconds elapsed')
        sleep(1)

    # Start testing the dodging obstacle.
    rMovement = np.average([buildSite.location0[0], buildSite.location1[0]])
    initialTheta = buildSite.location0[1] + constants.robotHeadRadiusDegrees + 20
    finalTheta = buildSite.location1[1] - constants.robotHeadRadiusDegrees - 20
    zHeight = -1375

    initialPoint = (rMovement, initialTheta, zHeight)
    finalPoint = (rMovement, finalTheta, zHeight)

    # Move to intersection Point
    robot.movePolar((rMovement, initialTheta, zHeight))

    # Update the buildSite intersection rectangle to reflect the tower we are building
    buildSite.intersectionRectangle[2] = (buildSite.intersectionRectangle[2][0], buildSite.intersectionRectangle[2][1], constants.blockSize * 5)
    buildSite.intersectionRectangle[3] = (buildSite.intersectionRectangle[3][0], buildSite.intersectionRectangle[3][1], constants.blockSize * 5)


    # Check the intersection
    intersection, intersectionPoint = robotManager.checkIntersection(initialPoint, finalPoint)
    print(f'Intersection: {intersection}')

    if not intersection:
        raise Exception('No intersection detected')

    # Dodge around the obstacle
    path = robotManager.dodgeObstacle(initialPoint=initialPoint,
                                      finalPoint=finalPoint,
                                      obstacle=buildSite.intersectionRectangle,
                                      intersectionPoint=intersectionPoint,
                                      direction=True)

    # Move along the path
    robot.queueWaypoints(path)


if __name__ == '__main__':
    main()




