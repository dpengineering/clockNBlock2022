#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *            Arnav Wadhwa                   12/03/2022           *
#      *                                                                *
#      ******************************************************************
import math

from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiSolenoid import DPiSolenoid
from time import sleep
from time import gmtime, strftime
import tty, sys, termios
# Constants go here

dpiRobot = DPiRobot()
dpiSolenoid = DPiSolenoid()

class RobotArm:

    _MAGNET_SOLENOID = 0
    _ROTATING_SOLENOID = 0

    def __init__(self, magnetSolenoid: int, rotatingSolenoid: int):
        self._MAGNET_SOLENOID = magnetSolenoid
        self._ROTATING_SOLENOID = rotatingSolenoid

    def setup(self) -> bool:

        dpiRobot.setBoardNumber(0)
        dpiSolenoid.setBoardNumber(0)

        if not dpiRobot.initialize():
            print("Communication with the DPiRobot board failed.")
            return False

        if not dpiSolenoid.initialize():
            print("Communication with the DPiSolenoid board failed.")
            return False

        if not dpiRobot.homeRobot(True):
            print("Homing failed.")
            return False

        return True

    def cartesianToPolar(self, robotCords: tuple):

        # Get x, y, z from our tuple
        x = robotCords[1]
        y = robotCords[2]
        z = robotCords[3] / 31

        # Convert to Polar Coords and rotate plane
        r = math.sqrt(x ** 2 + y ** 2) / 31
        theta = math.atan2(y, x) - math.pi / 2

        return r, theta, z

    def train(self):
        pos = dpiRobot.getCurrentPosition()
        speed = 40
        magnet = False
        rotation = False
        locationsFile = open("locations.txt", "w")
        time = strftime("%Y-%m-%d %H:%M", gmtime())
        locationsFile.write(f'Locations saved at {time} \n')
        locationsFile.close()
        filedescriptors = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)
        while (True):

            x = sys.stdin.read(1)[0]
            print(x)
            if x == 'a':
                # Move robot a little to the left
                print('-x')
                dpiRobot.addWaypoint(pos[1] - 0.5, pos[2], pos[3], speed)
            if x == 'd':
                print('+x')
                dpiRobot.addWaypoint(pos[1] + 0.5, pos[2], pos[3], speed)
            if x == 'w':
                print('+y')
                dpiRobot.addWaypoint(pos[1], pos[2] + 0.5, pos[3], speed)
            if x == 's':
                print('-y')
                dpiRobot.addWaypoint(pos[1], pos[2] - 0.5, pos[3], speed)
            if x == 'm':
                print("magnet")
                dpiSolenoid.switchDriverOnOrOff(not magnet)
                magnet = not magnet
            if x == 'r':
                print('rotate')
                dpiSolenoid.switchDriverOnOrOff(not rotation)
                rotation = not rotation
            if x == 'x':
                print("write")
                locationsFile = open("locations.txt", "w")
                name = input("What point is this")
                pos = self.cartesianToPolar(dpiRobot.getCurrentPosition())
                locationsFile.write(f'{name}: {pos} \n')
                locationsFile.close()
            if x == 'e':
                print("done")
                break

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)

def main():
    robotArm = RobotArm(11, 10)
    robotArm.setup()
    robotArm.train()


if __name__ == "__main__":
    main()



