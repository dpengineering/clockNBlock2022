#      ******************************************************************
#      *                                                                *
#      *                 Trains robot using joystick                    *
#      *                                                                *
#      *            Arnav Wadhwa                     1/30/2023          *
#      *                                                                *
#      ******************************************************************

import math
from time import strftime, gmtime

import pygame
import os
from dpeaDPi.DPiRobot import DPiRobot
from dpeaDPi.DPiSolenoid import DPiSolenoid


class Training:

    # YOU CAN CRASH THE ROBOT WITH THIS, PLEASE DON'T DRIVE IT RECKLESSLY

    # Constants:
    maxZ = 202
    minZ = -60
    #
    # This program is intended to be used to "train" points that the robot can repeatedly go to
    # In order to save our points, we will write them to a text file so the user does not have to
    # manually write these locations down. Here we are creating a text file
    # and writing the time we are saving the locations.
    #
    locationsFile = open("locations", "a")
    time = strftime("%Y-%m-%d %H:%M", gmtime())
    locationsFile.write(f'Locations saved at {time} \n')
    locationsFile.close()

    #
    # This program could be written using functional programming, however I have opted to use
    # Object-Oriented Programming as it is what I am used to.
    #
    # This is both the constructor and initialization method for our Training class
    # We first make pygame run in a headless configuration and then start our pygame project
    # Pygame is used to process the joystick inputs.
    # Then, we create, initialize, and home our DPiRobot.
    #
    def __init__(self):

        # allow ssh deploy with pygame (no screen)
        os.environ['SDL_VIDEODRIVER'] = "dummy"

        print("init pygame")
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print("init solenoid board")
        self.dpiSolenoid = DPiSolenoid()
        self.dpiSolenoid.setBoardNumber(0)
        if not self.dpiSolenoid.initialize():
            print("DPiSolenoid failed to initialize")
            exit(0)

        self.magnetVal = False
        self.rotateVal = False

        print("init robot")
        self.dpiRobot = DPiRobot()
        self.dpiRobot.setBoardNumber(0)
        if not self.dpiRobot.initialize():
            print("DPiRobot failed to initialize")
            exit(0)
        print("homing robot")
        homingStatus = self.dpiRobot.homeRobot(True)
        print(f"robot homing status {homingStatus}")

        self.movementFlag = False

    #
    # Get the axis (x, y, or z) of the joystick.
    # Returns a float from -1 to 1 of each joystick position
    # Raises ValueError if the given axis is not 'x', 'y', 'z', or 'all'
    #
    def get_axis(self, axis):

        # Ensures our axis is lowercase
        axis.lower()

        # Refreshes the joystick's current value
        self.refresh()

        if axis == "x":
            return self.joystick.get_axis(0)
        elif axis == "y":
            return self.joystick.get_axis(1)
        elif axis == "z":
            return self.joystick.get_axis(2)
        elif axis == "all":
            return self.joystick.get_axis(0), self.joystick.get_axis(1), self.joystick.get_axis(2)
        else:
            raise ValueError("Axis must be of type str and either 'x', 'y', or 'z'")

    #
    # Refreshes the current joystick value
    # Allows pygame to internally process events that we have given it
    # Doesn't need to be used if other event handlers are being used
    #
    @staticmethod
    def refresh():
        pygame.event.pump()

    #
    # Scales a value within a given range to its relative position in another range
    #
    @staticmethod
    def num_to_range(num, inMin, inMax, outMin, outMax):

        return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

    #
    # Generates target waypoint and speed based on joystick output
    # The joystick returns a value between -1 and 1 based on the location it is in
    # That value is scaled to a range between 0 and 5 which corresponds to the distance the robot will move
    # Then, we represent our joystick values as a vector and calculate the magnitude
    #  of that vector. Then we take the magnitude and scale it from 0 to 100 to get our speed
    # Then, we return the waypoint and speed
    # Raises an exception if the getCurrentPosition() of the DPiRobot fails
    #
    def generate_waypoint(self):

        # Currently, the 3 is an arbitrary number, change it as you wish
        # However, it limits the step size of the robot to be at max 27 mm
        translateX = self.num_to_range(self.get_axis('x'), -1, 1, 0, 3)
        translateY = self.num_to_range(self.get_axis('y'), -1, 1, 0, 3)
        joystickZ = self.num_to_range(self.get_axis('z'), -1, 1, self.minZ, self.maxZ)

        magnitude = math.sqrt(sum(pow(element, 2) for element in self.get_axis('all')))

        speed = self.num_to_range(magnitude, 0, math.sqrt(3), 0, 100)

        status, currentX, currentY, currentZ = self.dpiRobot.getCurrentPosition()

        translateZ = currentZ - joystickZ

        # Splits out Z steps into small amounts
        if translateZ > 3:
            # One line way to get the sign of translateZ but honestly this is slow and
            # Not worth it at all
            # 3 * (translateZ/abs(translateZ))
            translateZ = 3
        elif translateZ < -3:
            translateZ = -3
        elif abs(translateZ) < 0.3:
            translateZ = 0

        if status:
            return translateX + currentX, translateY + currentY, currentZ + translateZ, speed
        else:
            raise Exception("Could not get current position from DPiRobot")

    #
    # Checks if the robot is at least 1 millimeter away from our target position
    # This ensures we don't overflow the waypoint queue
    #
    def ready_for_next_point(self, target: tuple) -> bool:
        status, currentX, currentY, currentZ = self.dpiRobot.getCurrentPosition()
        if status:
            currentPos = currentX, currentY, currentZ
        else:
            raise Exception("Could not get current position from DPiRobot")

        return math.dist(currentPos, target) <= 2

    #
    # Adds the generated waypoint after the robot is close enough to the previous waypoint
    # Again, ensures that we don't overflow the queue with waypoints and "think" too far into the future
    # Returns the waypoint in order to be able to set it as a previous waypoint
    #
    def add_waypoint(self):
        X, Y, Z, speed = self.generate_waypoint()
        self.dpiRobot.addWaypoint(X, Y, Z, speed)

        return (X, Y, Z), speed

    @staticmethod
    def cartesianToPolar(position: tuple):
        """Helper function to change cartesian coordinates to polar
        Args:
            position (tuple): Current robot position in cartesian plane
        Returns:
            r, theta, z (tuple (float)): Returns the polar coordinates that correspond to the cartesian coordinates
        """
        x, y, z = position
        # Convert to Polar Coords
        r = math.sqrt(x ** 2 + y ** 2)
        theta = math.atan2(y, x)
        return r, theta, z

    #
    # Checks if we have pressed other buttons.
    # The trigger saves the location the robot is currently at
    # The middle button on the top of the joystick rehomes the robot
    #
    def check_other_buttons(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if self.joystick.get_button(0):
                    status, x, y, z = self.dpiRobot.getCurrentPosition()
                    r, theta, z = self.cartesianToPolar((x, y, z))
                    if status:
                        print("Write to file")
                        locationsFile = open("locations", "a")
                        name = input("What point is this? ")
                        locationsFile.write(f'{name}: ({r}, {theta}, {z} \n')
                        locationsFile.close()
                    else:
                        raise Exception("Could not get current position from DPiRobot")

                elif self.joystick.get_button(1):
                    print("Homing")
                    self.dpiRobot.homeRobot(True)

                elif self.joystick.get_button(2):
                    print("magnet")
                    self.dpiSolenoid.switchDriverOnOrOff(11, self.magnetVal)
                    self.magnetVal = not self.magnetVal

                elif self.joystick.get_button(3):
                    print("rotating")
                    self.dpiSolenoid.switchDriverOnOrOff(10, self.rotateVal)
                    self.rotateVal = not self.rotateVal

                elif self.joystick.get_button(4):
                    print("toggling movement")
                    self.movementFlag = not self.movementFlag


# Runs our main loop
def main():

    # Creating out joystick object
    print("starting")
    joystick = Training()

    # Gets current location and saves it as our previous target.
    # This is for checking if we should add more waypoints to the buffer
    print("getting current position and setting previous target")
    status, currentX, currentY, currentZ = joystick.dpiRobot.getCurrentPosition()
    previousTarget = currentX, currentY, currentZ

    # Loop through our main function
    while True:

        # First checks if we have inputted any more moves
        joystick.check_other_buttons()

        # If we are close enough to make our next move, do so now
        if joystick.ready_for_next_point(previousTarget):
            # Sets target to the point we are going to
            target, speed = joystick.add_waypoint()
            print(f"Moving to {target}")
            previousTarget = target


if __name__ == "__main__":
    main()
