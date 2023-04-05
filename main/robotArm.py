import numpy as np
from dpeaDPi.DPiRobot import DPiRobot


class RobotArm:

    # States
    STATE_MOVE_TO_FEEDER     = 0
    STATE_PICKUP_BLOCK       = 1
    STATE_ROTATE_BLOCK       = 2
    STATE_MOVE_TO_BUILD_SITE = 3
    STATE_PLACE_BLOCK        = 4
    STATE_IDLE               = 5

    def __init__(self, dpiSolenoid, magnetSolenoid, rotationSolenoid):

        self.dpiSolenoid = dpiSolenoid
        self.MAGNET_SOLENOID = magnetSolenoid
        self.ROTATING_SOLENOID = rotationSolenoid

        # Create our dpiRobot object
        self.dpiRobot = DPiRobot()

        # State machine
        self.state = self.STATE_IDLE
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
            self.rotateSolenoid()


    def rotateSolenoid(self):
        self.rotationPositionFlg = not self.rotationPositionFlg
        self.dpiSolenoid.switchDriverOnOrOff(self.ROTATING_SOLENOID, self.rotationPositionFlg)

    def cartesianToPolar(self, position: tuple):
        """Converts cartesian coordinates to polar coordinates"""
        x, y, z = position
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        theta = round(np.rad2deg(theta), 3)
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

    def ensureStraightLineCartesian(self, waypoints: list) -> list:
        """Ensures that the robot arm moves in a straight line
        This ensures that the robot will travel in a straight line as it does not do so with a long move.
        Check DPi_Robot firmware to see why. Alternatively, google how linear delta arms work.

        This makes the robot move in a straight line for cartesian coordinates. (As in no arcs)

        Args:
            waypoints (list): List of waypoints with possible long moves
        Returns:
            straightWaypoints (list): List of waypoints with long moves broken up
        """
        # Create our list of waypoints to return
        # Also, add our current position to the list
        straightWaypoints = [self.getPositionCartesian()]

        # Convert our list of waypoints in polar coordinates to a list in cartesian coordinates

        # Note: this operation is fairly slow because of the nested for loops.
        #   If this moves us in a straight line, it might be worth refactoring
        #   The code to work in cartesian coordinates
        for waypoint in waypoints:
            nextPoint = self.polarToCartesian(waypoint)
            # Calculating the distance between our last point and the next point we need to go to
            distance = abs(np.dist(straightWaypoints[-1], nextPoint))

            # If the distance is greater than 25mm, split the move into many steps
            if distance > 25:
                numSteps = int(distance / 25)
                # Current x, y, z values
                cX, cY, cZ = straightWaypoints[-1]
                # target x, y, z
                tX, tY, tZ = nextPoint

                # Split our move into a bunch of steps
                xSteps = np.linspace(cX, tX, numSteps, False)
                ySteps = np.linspace(cY, tY, numSteps, False)
                zSteps = np.linspace(cZ, tZ, numSteps, False)

                # Add these points to our list
                for i in range(len(xSteps)):
                    straightWaypoints.append((xSteps[i], ySteps[i], zSteps[i]))

            straightWaypoints.append(nextPoint)
        return straightWaypoints

    def ensureStraightLinePolar(self, waypoints: list) -> list:
        """Ensures a straight line move in polar coordinates
        This will cause the robot to move in an arc and in a straight line on the polar plane
        Args:
            waypoints (list): List of waypoints with possible long moves
        Returns:
            straightWaypoints (list): List of waypoints with long moves broken up
        """
        straightWaypoints = []

        # Loop through our list to find which moves are too far to be a straight line
        #   We don't need to check how far the points are away in Z because the robot moves downwards in a straight line
        for point in range(len(waypoints) - 1):
            r1, theta1, z1 = waypoints[point]
            r2, theta2, z2 = waypoints[point + 1]
            theta1, theta2 = np.deg2rad(theta1), np.deg2rad(theta2)
            distance = np.sqrt(r1 * r1 + r2 * r2 - 2 * r1 * r2 * np.cos(theta1 - theta2))
            # If the distance is greater than 20mm, split our moves up into 20mm segments
            if distance > 20:
                # Number of steps to split our line into
                numSteps = distance // 5

                # To generate the intermediary waypoints, np.linspace() is used on r, theta, and z values individually
                #   We create the points by merging the same index of each array into a tuple, and add it to our list
                
                # Convert theta back to degrees
                theta1, theta2 = np.rad2deg(theta1), np.rad2deg(theta2)
                
                rSteps = np.linspace(r1, r2, numSteps)
                thetaSteps = np.linspace(theta1, theta2, numSteps)
                zSteps = np.linspace(z1, z2, numSteps)

                # Add our points to the list
                #   Final point is omitted as it will  get added in the next iteration of the loop or at the very end
                for i in range(len(rSteps) - 1):
                    straightWaypoints.append((rSteps[i], thetaSteps[i], zSteps[i]))
            else:
                straightWaypoints.append(waypoints[point])

        # Add final point to list
        straightWaypoints.append(waypoints[-1])

        return straightWaypoints




