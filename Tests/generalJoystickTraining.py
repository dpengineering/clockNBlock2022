#      ******************************************************************
#      *                                                                *
#      *                 Trains robot using joystick                    *
#      *                                                                *
#      *            Arnav Wadhwa                     1/30/2023          *
#      *                                                                *
#      ******************************************************************
from time import strftime, gmtime, sleep

import pygame
import os
from dpeaDPi.DPiRobot import DPiRobot


class TrainingCartesian:

    # YOU CAN CRASH THE ROBOT WITH THIS, PLEASE DON'T DRIVE IT RECKLESSLY

    locationsFile = open("locations", "a")
    time = strftime("%Y-%m-%d %H:%M", gmtime())
    locationsFile.write(f'Locations saved at {time} \n')
    locationsFile.close()

    minX = -610
    maxX = 610
    minY = -610
    maxY = 610
    minZ = -70
    maxZ = 210

    def __init__(self):

        # allow ssh deploy with pygame (no screen)
        os.environ['SDL_VIDEODRIVER'] = "dummy"

        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        self.dpiRobot = DPiRobot()
        self.dpiRobot.setBoardNumber(0)
        self.dpiRobot.homeRobot(True)

    def get_axis(self, axis):
        """
        Get the axis (x or y) of the joystick.
        :raises: ValueError If the given axis isn't 'x' 'y'
        :param axis: axis to get value of
        :rtype: float
        :return: All the way to the right=1, fully up=-1
        """
        axis.lower()
        self.refresh()
        if axis == "x":
            return self.joystick.get_axis(0)
        elif axis == "y":
            return self.joystick.get_axis(1)
        elif axis == "z":
            return self.joystick.get_axis(2)
        else:
            raise ValueError("Axis must be of type str and either 'x', 'y', or 'z'")

    @staticmethod
    def refresh():
        """
        Refresh the joysticks current value
        :return: None
        """
        pygame.event.pump()

    @staticmethod
    def num_to_range(num, inMin, inMax, outMin, outMax):

        return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

    def generate_waypoint(self):

        # Currently, the 5 is an arbitrary number, change it as you wish
        translateX = self.num_to_range(self.get_axis('x'), -1, 1, self.minX, self.maxX)
        translateY = self.num_to_range(self.get_axis('y'), -1, 1, self.minY, self.maxY)
        translateZ = self.num_to_range(self.get_axis('z'), 1, -1, self.minZ, self.maxZ)

        return translateX, translateY, translateZ

    def add_waypoint(self, waypoint: tuple, speed: int = 50):
        self.dpiRobot.addWaypoint(waypoint[0], waypoint[1], waypoint[2], speed)

    def check_other_buttons(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if self.joystick.get_button(0):
                    print("write to file")
                    locationsFile = open("locations", "a")
                    name = input("What point is this")
                    status, x, y, z = self.dpiRobot.getCurrentPosition()
                    locationsFile.write(f'{name}: ({x}, {y}, {z} \n')
                    locationsFile.close()


def main():
    joystick = TrainingCartesian()
    joystick.dpiRobot.bufferWaypointsBeforeStartingToMove(True)
    while True:
        joystick.add_waypoint(joystick.generate_waypoint())
        joystick.check_other_buttons()


if __name__ == "__main__":
    main()
