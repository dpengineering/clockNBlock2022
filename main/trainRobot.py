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

    # Step sizes for all our moves, order is radius, theta, Z
    steps = [1, 1, 1]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                pos = robotArm.getPosition()
                polarPos = robotArm.cartesianToPolar(pos[1], pos[2])
                if event.key == pygame.K_LEFT:
                    # Change Theta
                    print('-theta')
                    cartesian = robotArm.polarToCartesian(polarPos[0], polarPos[1] - steps[1])
                    print(robotArm.moveToPoint(cartesian[0], cartesian[1], pos[3], speed))
                if event.key == pygame.K_RIGHT:
                    print('+theta')
                    cartesian = robotArm.polarToCartesian(polarPos[0], polarPos[1] + steps[1])
                    print(robotArm.moveToPoint(cartesian[0], cartesian[1], pos[3], speed))
                if event.key == pygame.K_UP:
                    print('+radius')
                    cartesian = robotArm.polarToCartesian(polarPos[0] + steps[0], polarPos[1])
                    print(robotArm.moveToPoint(cartesian[0], cartesian[1], pos[3], speed))
                if event.key == pygame.K_DOWN:
                    print('-radius')
                    cartesian = robotArm.polarToCartesian(polarPos[0] - steps[0], polarPos[1])
                    print(robotArm.moveToPoint(cartesian[0], cartesian[1], pos[3], speed))
                if event.key == pygame.K_z:
                    print('-z')
                    print(robotArm.moveToPoint(pos[1], pos[2], pos[3] - steps[2], speed))
                if event.key == pygame.K_x:
                    print('+z')
                    print(robotArm.moveToPoint(pos[1], pos[2], pos[3] + steps[2], speed))
                if event.key == pygame.K_SPACE:
                    print("magnet")
                    dpiSolenoid.switchDriverOnOrOff(robotArm.MAGNET_SOLENOID, not magnet)
                    magnet = not magnet
                if event.key == pygame.K_r:
                    print('rotate')
                    dpiSolenoid.switchDriverOnOrOff(robotArm.ROTATING_SOLENOID, not rotation)
                    rotation = not rotation
                if event.key == pygame.K_g:
                    print("Changing steps")
                    stepToChange = input("Which step are you changing? (0: radius, 1: theta, 2: Z, 3: all) ")
                    if int(stepToChange) in range(0, 2):
                        value = input("step value: ")
                        steps[stepToChange] = value
                    elif stepToChange == 3:
                        rStep = input("Value for r: ")
                        tStep = input("Value for theta:")
                        zStep = input("Value for Z: ")
                        steps = [rStep, tStep, zStep]
                    else:
                        print("you entered an incorrect value, try again please")
                if event.key == pygame.K_s:
                    print("write")
                    locationsFile = open("locations", "a")
                    name = input("What point is this")
                    savePos = robotArm.cartesianToPolar(pos[1], pos[2])
                    locationsFile.write(f'{name}: {savePos}, {pos[3]} \n')
                    locationsFile.close()
                if event.key == pygame.K_ESCAPE:
                    print("done")
                    pygame.quit()
                    return


def main():
    train()
    pygame.quit()


if __name__ == "__main__":
    main()
