import time

from dpeaDPi.DPiRobot import DPiRobot
import Objects.constants as constants
from Objects.robotManager import RobotManager


class RobotArm:

    # States
    _STATE_MOVE_TO_FEEDER     = 0
    _STATE_PICKUP_BLOCK       = 1
    _STATE_ROTATE_BLOCK       = 2
    _STATE_MOVE_TO_BUILD_SITE = 3
    _STATE_PLACE_BLOCK        = 4
    _STATE_IDLE               = 5

    def __init__(self, dpiSolenoid, magnetSolenoid, rotationSolenoid, buildSites=None, blockFeeders=None):

        self.dpiSolenoid = dpiSolenoid
        self.MAGNET_SOLENOID = magnetSolenoid
        self.ROTATING_SOLENOID = rotationSolenoid

        # For testing purposes
        if buildSites is not None or blockFeeders is not None:
            self.robotManager = RobotManager(buildSites, blockFeeders)

        # Create our dpiRobot object
        self.dpiRobot = DPiRobot()

        # State machine
        self.state = self._STATE_IDLE
        self.newState = False
        self.target = None
        self.start = None

        # Flags
        self.rotationPositionFlg = False  # False is the position to pick up blocks, True is there to place
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

        self.setState(self._STATE_MOVE_TO_FEEDER)

        return True


    def process(self):

        _status, robotState = self.dpiRobot.getRobotStatus()

        if robotState == self.dpiRobot.STATE_E_STOPPED_PRESSED or robotState == self.dpiRobot.STATE_NOT_HOMED:
            self.isHomedFlg = False

        currentPosition = self.getPositionPolar()

        if self.state == self._STATE_MOVE_TO_FEEDER:
            if self.newState:
                # Try getting a block 3 times.
                for _ in range(3):
                    waypoints = self.robotManager.moveToFeeder(currentPosition)
                    if waypoints is not None and waypoints:
                        self.queueWaypoints(waypoints, robotState=robotState)
                        self.target = waypoints[-1]
                        self.newState = False
                        self.start = time.time()
                        return self.target[1]
                self.setState(self._STATE_IDLE)
                return None

            # In this state, we will need to rotate the block before we pick it up
            # This does break our method for having the states be do something -> wait -> next state
            # But this also saves us from having to create a whole new state to rotate the block
            elif time.time() - self.start > 1 and self.rotationPositionFlg:
                self.rotate()
                print('rotated')
                return None

            elif self.isAtLocation(self.target) and robotState == self.dpiRobot.STATE_STOPPED:
                self.setState(self._STATE_PICKUP_BLOCK)
                print('at location')
                return None

        elif self.state == self._STATE_PICKUP_BLOCK:
            if self.newState:
                self.dpiSolenoid.switchDriverOnOrOff(constants.magnetSolenoid, True)
                self.start = time.time()
                self.newState = False
                print('picking up block')
                return None

            elif time.time() - self.start > 0.5:
                self.setState(self._STATE_MOVE_TO_BUILD_SITE)
                return None

        elif self.state == self._STATE_MOVE_TO_BUILD_SITE:
            if self.newState:
                # Try placing a block 3 times.
                for _ in range(3):
                    waypoints = self.robotManager.moveToBuildSite(currentPosition)
                    if waypoints is not None:
                        self.queueWaypoints(waypoints, robotState=robotState)
                        self.target = waypoints[-1]
                        self.newState = False
                        self.start = time.time()
                        return self.target[1]

                self.setState(self._STATE_IDLE)
                return None

            # In this state, we will need to rotate the block after it clear the hole
            # This does break our method for having the states be do something -> wait -> next state
            # But this also saves us from having to create a whole new state to rotate the block
            elif time.time() - self.start > 1 and not self.rotationPositionFlg:
                self.rotate()
                print('rotated')
                return None

            elif self.isAtLocation(self.target) and robotState == self.dpiRobot.STATE_STOPPED:
                self.setState(self._STATE_PLACE_BLOCK)
                print('at location')
                return None

        elif self.state == self._STATE_PLACE_BLOCK:
            if self.newState:
                self.dpiSolenoid.switchDriverOnOrOff(constants.magnetSolenoid, False)
                self.start = time.time()
                self.newState = False
                print('placing block')
                return None

            elif time.time() - self.start > 0.5:
                self.setState(self._STATE_MOVE_TO_FEEDER)
                return None

        elif self.state == self._STATE_IDLE:
            if self.newState:
                self.dpiRobot.homeRobot(True)
                if self.rotationPositionFlg:
                    self.rotate()

                self.dpiSolenoid.switchDriverOnOrOff(constants.magnetSolenoid, False)
                self.newState = False
                return None

            elif self.robotManager.moveToFeeder(currentPosition) is not None:
                self.setState(self._STATE_MOVE_TO_FEEDER)
                return None


    def rotate(self):
        self.rotationPositionFlg = not self.rotationPositionFlg
        self.dpiSolenoid.switchDriverOnOrOff(self.ROTATING_SOLENOID, self.rotationPositionFlg)

    def moveCartesian(self, position, speed):
        """Moves the robot arm to a cartesian position"""
        x, y, z = position
        self.dpiRobot.addWaypoint(x, y, z, speed)

    def movePolar(self, position, speed):
        """Moves the robot arm to a polar position"""
        x, y, z = constants.polarToCartesian(position)
        self.moveCartesian((x, y, z), speed)

    def getPositionCartesian(self):
        """Returns the current position of the robot arm"""
        _success_flg, x, y, z = self.dpiRobot.getCurrentPosition()
        return x, y, z

    def getPositionPolar(self):
        """Returns the current position of the robot arm in radians"""
        x, y, z = self.getPositionCartesian()
        r, theta, z = constants.cartesianToPolar((x, y, z))
        return r, theta, z

    def isAtLocation(self, position, tolerance=2):
        """Returns true if the robot arm is within a tolerance of a position
        Args:
            position: tuple of (x, y, z) position in cartesian coordinates
            tolerance: float of the tolerance in mm
        Returns:
            True if the robot arm is within the tolerance of the position
        """
        x, y, z = self.getPositionCartesian()
        position = constants.polarToCartesian(position)
        x1, y1, z1 = position

        return abs(x - x1) < tolerance and abs(y - y1) < tolerance and abs(z - z1) < tolerance

    def setState(self, state):
        """Sets the state of the robot arm"""
        self.state = state
        self.newState = True


    def queueWaypoints(self, waypoints: list, speed: int = constants.robotSpeed, robotState=-1):
        """Helper function to queue waypoints in a list.
        Args:
            waypoints (list): List of waypoints to queue all in polar coordinates
            speed (int): How fast to move robot
            robotState (int): Robot state given by DPiRobot board
        Returns:
            none
        """
        if robotState == self.dpiRobot.STATE_STOPPED:
            self.dpiRobot.bufferWaypointsBeforeStartingToMove(True)
            [self.movePolar(waypoint, speed) for waypoint in waypoints]
            self.dpiRobot.bufferWaypointsBeforeStartingToMove(False)
            return True
        else:
            print('Robot is not stopped')
            return False
