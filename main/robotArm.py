#      ******************************************************************
#      *                                                                *
#      *                        Robot Arm Object                        *
#      *                                                                *
#      *            Arnav Wadhwa                   12/03/2022           *
#      *                                                                *
#      ******************************************************************
import math
import sys

from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiSolenoid import DPiSolenoid
from time import sleep, gmtime, strftime
import pygame

# Constants go here

dpiRobot = DPiRobot()
dpiSolenoid = DPiSolenoid()

pygame.init()
display = pygame.display.set_mode((300, 300))


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
        speed = 40
        magnet = False
        rotation = False
        locationsFile = open("locations.txt", "w")
        time = strftime("%Y-%m-%d %H:%M", gmtime())
        locationsFile.write(f'Locations saved at {time} \n')
        locationsFile.close()

        while (True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    pos = dpiRobot.getCurrentPosition()
                    if event.key == pygame.K_LEFT:
                        # Move robot a little to the left
                        print('-x')
                        dpiRobot.addWaypoint(pos[1] - 0.5, pos[2], pos[3], speed)
                    if event.key == pygame.K_RIGHT:
                        print('+x')
                        dpiRobot.addWaypoint(pos[1] + 0.5, pos[2], pos[3], speed)
                    if event.key == pygame.K_UP:
                        print('+y')
                        dpiRobot.addWaypoint(pos[1], pos[2] + 0.5, pos[3], speed)
                    if event.key == pygame.K_DOWN:
                        print('-y')
                        dpiRobot.addWaypoint(pos[1], pos[2] - 0.5, pos[3], speed)
                    if event.key == pygame.K_z:
                        print('-z')
                        dpiRobot.addWaypoint(pos[1], pos[2], pos[3]-0.5, speed)
                    if event.key == pygame.K_x:
                        print('z')
                        dpiRobot.addWaypoint(pos[1], pos[2], pos[3]+0.5, speed)
                    if event.key == pygame.K_SPACE:
                        print("magnet")
                        dpiSolenoid.switchDriverOnOrOff(not magnet)
                        magnet = not magnet
                    if event.key == pygame.K_r:
                        print('rotate')
                        dpiSolenoid.switchDriverOnOrOff(not rotation)
                        rotation = not rotation
                    if event.key == pygame.K_s:
                        print("write")
                        locationsFile = open("locations.txt", "w")
                        name = input("What point is this")
                        pos = self.cartesianToPolar(dpiRobot.getCurrentPosition())
                        locationsFile.write(f'{name}: {pos} \n')
                        locationsFile.close()
                    if event.key == pygame.K_ESCAPE:
                        print("done")
                        pygame.quit()
                        return


# def testKeys():
#
#     while (True):
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_LEFT:
#                     print('-x')
#                 if event.key == pygame.K_RIGHT:
#                     print('+x')
#                 if event.key == pygame.K_UP:
#                     print('+y')
#                 if event.key == pygame.K_DOWN:
#                     print('-y')
#                 if event.key == pygame.K_z:
#                     print('-z')
#                 if event.key == pygame.K_x:
#                     print('z')
#                 if event.key == pygame.K_SPACE:
#                     print("magnet")
#                 if event.key == pygame.K_r:
#                     print('rotate')
#                 if event.key == pygame.K_s:
#                     print("write")
#                 if event.key == pygame.K_ESCAPE:
#                     print("done")
#                     pygame.quit()
#                     return

def main():
    robotArm = RobotArm(11, 10)
    robotArm.setup()
    robotArm.train()
    pygame.quit()


if __name__ == "__main__":
    main()



