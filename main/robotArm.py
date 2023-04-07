import numpy as np
from dpeaDPi.DPiRobot import DPiRobot
from robotManager import RobotManager


class RobotArm:

    # States
    _STATE_MOVE_TO_FEEDER     = 0
    _STATE_PICKUP_BLOCK       = 1
    _STATE_ROTATE_BLOCK       = 2
    _STATE_MOVE_TO_BUILD_SITE = 3
    _STATE_PLACE_BLOCK        = 4
    _STATE_IDLE               = 5

    def __init__(self, dpiSolenoid, magnetSolenoid, rotationSolenoid):

        self.dpiSolenoid = dpiSolenoid
        self.MAGNET_SOLENOID = magnetSolenoid
        self.ROTATING_SOLENOID = rotationSolenoid

        # Create our dpiRobot object
        self.dpiRobot = DPiRobot()

        # State machine
        self.state = self._STATE_IDLE
        self.newState = False

        # Flags
        self.rotationPositionFlg = False
        self.isHomedFlg = False

        self.initialize()

    def initialize(self):
        """Set up the robot arm"""
        self.dpiRobot.setBoardNumber(0)

        if not self.dpiRobot.initialize():
            raise Exception("Robot arm initialization failed")

        # Prime the solenoid
        self.dpiSolenoid.switchDriverOnOrOff(self.ROTATING_SOLENOID, True)
        self.dpiSolenoid.switchDriverOnOrOff(self.ROTATING_SOLENOID, False)


    def setup(self):
        """Set up robot arm"""

        # Homes robot
        if not self.dpiRobot.homeRobot(True):
            print("Homing failed.")

            _success_flg, status = self.dpiRobot.getRobotStatus()
            if status == self.dpiRobot.STATE_E_STOPPED_PRESSED:
                print("E-Stop button is pressed.")
            return False

        self.isHomedFlg = True

        # Reset rotation position
        if not self.rotationPositionFlg:
            self.rotate()


    def rotate(self):
        self.rotationPositionFlg = not self.rotationPositionFlg
        self.dpiSolenoid.switchDriverOnOrOff(self.ROTATING_SOLENOID, self.rotationPositionFlg)

    def cartesianToPolar(self, position: tuple):
        """Helper function to change cartesian coordinates to polar
        Args:
            position (tuple): Current robot position in cartesian plane
        Returns:
            r, theta, z (tuple (float)): Returns the polar coordinates that correspond to the cartesian coordinates
        """
        x, y, z = position
        # Convert to Polar Coords
        r = np.sqrt(x ** 2 + y ** 2)
        theta = np.arctan2(y, x)
        print(theta)
        theta = np.rad2deg(theta)
        print(theta)

        # Adjust for negative values
        if x < 0 < y:
            theta += 180
        elif x < 0 and y < 0:
            theta += 360
        elif y < 0 < x:
            theta += 360

        return r, theta, z

    def polarToCartesian(self, position: tuple):
        """Converts polar coordinates to cartesian coordinates"""
        r, theta, z = position
        theta = np.deg2rad(theta)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y, z

    def moveCartesian(self, position, speed):
        """Moves the robot arm to a cartesian position"""
        x, y, z = position
        self.dpiRobot.addWaypoint(x, y, z, speed)

    def movePolar(self, position, speed):
        """Moves the robot arm to a polar position"""
        x, y, z = self.polarToCartesian(position)
        self.moveCartesian((x, y, z), speed)

    def getPositionCartesian(self):
        """Returns the current position of the robot arm"""
        _success_flg, x, y, z = self.dpiRobot.getCurrentPosition()
        return x, y, z

    def getPositionPolar(self):
        """Returns the current position of the robot arm in radians"""
        x, y, z = self.getPositionCartesian()
        r, theta, z = self.cartesianToPolar((x, y, z))
        return r, theta, z

    def isAtLocation(self, position, tolerance):
        """Returns true if the robot arm is within a tolerance of a position
        Args:
            position: tuple of (x, y, z) position in cartesian coordinates
            tolerance: float of the tolerance in degrees
        Returns:
            True if the robot arm is within the tolerance of the position
        """
        x, y, z = self.getPositionCartesian()
        x1, y1, z1 = position

        return abs(x - x1) < tolerance and abs(y - y1) < tolerance and abs(z - z1) < tolerance

    def setState(self, state):
        """Sets the state of the robot arm"""
        self.state = state
        self.newState = True





