import sys
import numpy as np
from time import sleep
sys.path.append('../')

from dpeaDPi.DPiSolenoid import DPiSolenoid

from Objects.robotArm import RobotArm
from Objects.robotManager import RobotManager
import Objects.constants as constants

dpiSolenoid = DPiSolenoid()
dpiSolenoid.setBoardNumber(0)
if not dpiSolenoid.initialize():
    raise Exception("Solenoid initialization failed")

robot = RobotArm(dpiSolenoid, constants.magnetSolenoid, constants.rotationSolenoid)
if not robot.setup():
    raise Exception("Robot setup failed")

robotManager = RobotManager([], [])



def main():
    # sleep(5)
    initialPoint = (500, 260, -1350)
    finalPoint = (500, 30, -1350)

    # Run this with debugger, adding print statements as necessary
    waypoints, _ = robotManager.planZigZagMove(initialPoint, finalPoint)
    # waypoints, _ = robotManager.planStraightMove(initialPoint, finalPoint)
    print(f'Waypoints before straightening: {waypoints}')
    print(f'Length: {len(waypoints)}')
    waypoints = robotManager.ensureStraightLineCartesian(waypoints)
    print(f'Waypoints after straightening: {waypoints}')

    robot.queueWaypoints(waypoints, robotState=robot.dpiRobot.getRobotStatus()[1])



if __name__ == "__main__":
    main()
