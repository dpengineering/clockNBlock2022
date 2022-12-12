#      ******************************************************************
#      *                                                                *
#      *                        Train Robot Arm                         *
#      *                                                                *
#      *     Arnav Wadhwa, Brian Vesper            12/10/2022           *
#      *                                                                *
#      ******************************************************************

# This can really be optimized, but it is fine for our purposes at the moment.

from robotArm import RobotArm
from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiSolenoid import DPiSolenoid

import math
import sys
from time import gmtime, strftime
import pygame

dpiSolenoid = DPiSolenoid()
dpiSolenoid.setBoardNumber(0)
dpiSolenoid.initialize()

robotArm = RobotArm(11, 10)
robotArm.setup()


pygame.init()
display = pygame.display.set_mode((300, 300))


# Can probably just run this through VNC
def train():
    speed = 40
    magnet = False
    rotation = False
    locationsFile = open("locations", "a")
    time = strftime("%Y-%m-%d %H:%M", gmtime())
    locationsFile.write(f'Locations saved at {time} \n')
    locationsFile.close()
    step = 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                pos = robotArm.getPosition()
                if event.key == pygame.K_LEFT:
                    # Move robot a little to the left
                    print('-x')
                    print(robotArm.moveToPoint(pos[1] - step, pos[2], pos[3], speed))
                    print(f"x: {pos[1] - step}, y: {pos[2]}, z: {pos[3]}, speed: {speed}")
                if event.key == pygame.K_RIGHT:
                    print('+x')
                    print(robotArm.moveToPoint(pos[1] + step, pos[2], pos[3], speed))
                    print(f"x: {pos[1] + step}, y: {pos[2]}, z: {pos[3]}, speed: {speed}")
                if event.key == pygame.K_UP:
                    print('+y')
                    print(robotArm.moveToPoint(pos[1], pos[2] + step, pos[3], speed))
                    print(f"x: {pos[1]}, y: {pos[2] + step}, z: {pos[3]}, speed: {speed}")
                if event.key == pygame.K_DOWN:
                    print('-y')
                    print(robotArm.moveToPoint(pos[1], pos[2] - step, pos[3], speed))
                    print(f"x: {pos[1]}, y: {pos[2] - step }, z: {pos[3]}, speed: {speed}")
                if event.key == pygame.K_z:
                    print('-z')
                    print(robotArm.moveToPoint(pos[1], pos[2], 100, speed))
                    print(f"x: {pos[1]}, y: {pos[2]}, z: {100}, speed: {speed}")
                if event.key == pygame.K_x:
                    print('z')
                    print(robotArm.moveToPoint(pos[1], pos[2], pos[3] + step, speed))
                    print(f"x: {pos[1] - step}, y: {pos[2]}, z: {pos[3] + step}, speed: {speed}")
                if event.key == pygame.K_SPACE:
                    print("magnet")
                    dpiSolenoid.switchDriverOnOrOff(robotArm.MAGNET_SOLENOID, not magnet)
                    magnet = not magnet
                if event.key == pygame.K_r:
                    print('rotate')
                    dpiSolenoid.switchDriverOnOrOff(robotArm.ROTATING_SOLENOID, not rotation)
                    rotation = not rotation
                if event.key == pygame.K_s:
                    print("write")
                    locationsFile = open("locations", "a")
                    name = input("What point is this")
                    pos = robotArm.cartesianToPolar()
                    locationsFile.write(f'{name}: {pos} \n')
                    locationsFile.close()
                if event.key == pygame.K_g:
                    newStep = input("Enter new step size: ")
                    step = int(newStep)
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
    train()
    pygame.quit()


if __name__ == "__main__":
    main()
