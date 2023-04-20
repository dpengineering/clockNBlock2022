# Controls how the robot arm moves
import numpy as np
import Objects.constants as constants
import math


class RobotManager:

    # The robot arm will ask us to do two things:
    # Move to a feeder
    # Move to a build site

    # The robotManager will always return a list of waypoints for the robot arm to follow.
    # The robot arm does not do any logic on its own.
    # Also, the robot arm will always move to polar coordinates. Even if it is going in a straight line
    # cartesian wise.

    def __init__(self, buildSites=None, blockFeeders=None):
        """Initializes the robot manager
        Args:
            buildSites (list): List of build sites
            blockFeeders (list): List of block feeders
        """

        self.blockFeeders = blockFeeders
        self.buildSites = buildSites
        self.robotPos = (0, 0, 0)

        # To move to a position from the side, we need to go to a position next to the target value
        # This is how far away we will be
        self.offSetAngle = 20

        self.maximumMovingR = constants.maximumMovingRadius


    def moveToFeeder(self, robotPos):
        """Moves to a feeder
        Args:
            robotPos (tuple): (r, theta, z) position of the robot arm
        Returns:
            waypoints (list): List of waypoints for the robot arm to follow
        """

        # Choose a feeder to move to
        feeder = self.chooseFeeder()
        finalLocation = feeder.location

        waypoints = self.planMove(robotPos, finalLocation)
        waypoints = self.ensureStraightLine(waypoints)

        return waypoints


    def moveToBuildSite(self, robotPos):
        """Moves to a build site
        Args:
            robotPos (tuple): (r, theta, z) position of the robot arm
        Returns:
            waypoints (list): List of waypoints for the robot arm to follow
        """

        # Get the buildSite to move to
        buildSite = self.chooseBuildSite()


        # If there are no build sites, return None
        if buildSite is None:
            return None

        finalLocation = buildSite.placeNextBlock()
        if finalLocation is None:
            return None

        waypoints = self.planMove(robotPos, finalLocation)
        waypoints = self.ensureStraightLine(waypoints)

        return waypoints


    def chooseFeeder(self):
        """Chooses a feeder to move to based on the following
            If a feeder is ready, choose a random one
            If no feeder is ready, return None

        Returns:
            feeder (Feeder): Feeder to move to
        """
        # Get a list of all the feeders that are ready
        readyFeeders = [feeder for feeder in self.blockFeeders if feeder.isReadyFlg]
        print(f'Ready Feeders {[feeder.index for feeder in readyFeeders]}')

        # If there are no ready feeders, return None
        if len(readyFeeders) == 0:
            return None

        # Choose a random feeder
        feeder = np.random.choice(readyFeeders)

        return feeder

    def chooseBuildSite(self):
        """Chooses a build site to move to based on the following
            If a build site is ready, assign weights to each then choose a random one
            If no build site is ready, return None

        Returns:
            buildSite (BuildSite): Build site to move to
        """
        # Get a list of all the build sites that are ready
        readyBuildSites = [buildSite for buildSite in self.buildSites if buildSite.isReadyFlg]
        print(f'Ready Build Site {[buildSite.index for buildSite in readyBuildSites]}')

        # If there are no ready build sites, return None
        if len(readyBuildSites) == 0:
            return None

        # Choose a random build site
        buildSite = np.random.choice(readyBuildSites)

        return buildSite

    def ensureStraightLine(self, waypoints: list) -> list:
        """Ensures that the robot arm moves in a straight line
        This ensures that the robot will travel in a straight line as it does not do so with a long move.
        Check DPi_Robot firmware to see why. Alternatively, google how linear delta arms work.
        This makes the robot move in a straight line for cartesian coordinates. (As in no arcs)
        Args:
            waypoints (list): List of polar waypoints with possible long moves
        Returns:
            straightWaypoints (list): List of waypoints with long moves broken up in polar coordinates
        """
        # Create our list of waypoints to return
        # Also, add our current position to the list
        straightWaypoints = []

        # Convert our list of waypoints in polar coordinates to a list in cartesian coordinates

        # Note: this operation is fairly slow because of the nested for loops.
        #   If this moves us in a straight line, it might be worth refactoring
        #   The code to work in cartesian coordinates
        for point in range(len(waypoints) - 1):
            x1, y1, z1 = constants.polarToCartesian(waypoints[point])
            x2, y2, z2 = constants.polarToCartesian(waypoints[point + 1])

            # Calculating the distance between our last point and the next point we need to go to
            distance = abs(math.dist((x1, y1, z1), (x2, y2, z2)))

            # If the distance is greater than 20mm, split the move into many steps
            if distance > 20:
                numSteps = int(distance / 20)

                # Split our move into a bunch of steps
                xSteps = np.linspace(x1, x2, numSteps, False)
                ySteps = np.linspace(y1, y2, numSteps, False)
                zSteps = np.linspace(z1, z2, numSteps, False)

                # Add these points to our list
                [straightWaypoints.append(point) for point in zip(xSteps, ySteps, zSteps)]

            straightWaypoints.append((x2, y2, z2))

        [print(f'index: {idx}, xyz: {point}') for idx, point in enumerate(straightWaypoints)]

        # Convert our list of waypoints in cartesian coordinates to a list in polar coordinates
        straightWaypoints = [constants.cartesianToPolar(waypoint) for waypoint in straightWaypoints]

        return straightWaypoints


    def planMove(self, currentPos, targetPos):
        """ Plans a path from the current position to the target position
        Args:
            currentPos (tuple): Current position of the robot
            targetPos (tuple): Target position of the robot
        Returns:
            waypoints (list): List of waypoints to travel to
        """
        waypoints = []
        checkWaypointsUpUntil = 0
        currentR, currentTheta, currentZ = currentPos
        targetR, targetTheta, targetZ = targetPos

        # Move to this location in our polar coordinate system
        travelHeight = currentZ + 100

        # The first move will always be moving up.
        waypoints.append((currentR, currentTheta, travelHeight))

        # Next, check if we need to move in towards the center
        if currentR > self.maximumMovingR:
            # Move in towards the center
            waypoints.append((self.maximumMovingR, currentTheta, travelHeight))


        # Then, move next to and above the target location
        sign = np.random.choice([-1, 1])
        waypoints.append((targetR, targetTheta + sign * self.offSetAngle, travelHeight))

        # So we don't check waypoints that will place a block.
        checkWaypointsUpUntil = len(waypoints) - 1

        # Go down to 5mm above the target location
        waypoints.append((targetR, targetTheta + sign * self.offSetAngle, targetZ + 5))

        # Go over the location
        waypoints.append((targetR, targetTheta, targetZ + 5))

        # Go down to the target location
        waypoints.append((targetR, targetTheta, targetZ))

        # Check if we are intersecting any obstacles
        if self.buildSites is not None:
            maxZ = -np.inf
            for building in self.buildSites:
                obstacle = building.intersectionRectangle
                for i in range(checkWaypointsUpUntil - 1):
                    # Check if the line intersects the obstacle
                    intersection, zHeight = self.checkIntersection(waypoints[i], waypoints[i + 1], obstacle)
                    if intersection:
                        print("Found intersection")
                        if zHeight > maxZ:
                            maxZ = zHeight


            # If we found an intersection, change all the waypoints that move at travelHeight to move at maxZ
            if maxZ != -np.inf:
                for i in range(len(waypoints)):
                    if waypoints[i][2] == travelHeight:
                        waypoints[i] = (waypoints[i][0], waypoints[i][1], maxZ)


        return waypoints


    def checkIntersection(self, initialPoint, finalPoint, rectangle):
        """Checks if a line intersects a polygon
        Args:
            initialPoint (tuple): The starting point of the line in polar coordinates
            finalPoint (tuple): The ending point of the line in polar coordinates
            rectangle(list): The rectangle to check for intersection, in the form [point0, point1, point2, point3], All in polar coordinates
        Returns:
            intersection (bool): True if the line intersects the polygon, False otherwise
            zHeight (float): The height of the intersection, if there is one
        """
        # Implements answer from https://stackoverflow.com/questions/8812073/ray-and-square-rectangle-intersection-in-3d/8862483#8862483

        # First, we need to convert our points to cartesian coordinates
        initialPoint = constants.polarToCartesian(initialPoint)
        finalPoint = constants.polarToCartesian(finalPoint)

        # Transform our line into a vector of the form v0 + t * d
        # Where v0 is the initial point, d is the direction vector, and t is the scalar
        vectorInitial = np.array(initialPoint)
        d = (np.array(finalPoint) - vectorInitial) / np.linalg.norm(np.array(finalPoint) - vectorInitial)

        # The t is never used, just there for completeness
        t = np.linalg.norm(np.array(finalPoint) - vectorInitial)

        # Converto to cartesian coordinates
        rectangle = [constants.polarToCartesian(point) for point in rectangle]

        # Represent our rectangle as an initial point and 2 vectors. r0 is the initial point, s0 and s1 are the vectors
        # The initial point is the bottom left corner of the rectangle (point0)
        r0 = np.array(rectangle[0])
        s0 = np.array(rectangle[1]) - r0
        s1 = np.array(rectangle[2]) - r0

        # We also need the normal vector of the rectangle
        n = np.cross(s0, s1)

        # Assuming our intersection point is P; P = v0 + a * d where a is how far away from v0 the intersection is
        a = ((r0 - vectorInitial).dot(n)) / (d.dot(n))

        # All we need to do now is check if our point is within the rectangle
        # To do this, we project the vector from point0 of the rectangle onto the s0 and s1 vectors
        rectOriginToIntersection = (vectorInitial + a * d) - r0

        projectionOntoS0 = np.dot(rectOriginToIntersection, s0) / np.linalg.norm(s0)
        projectionOntoS1 = np.dot(rectOriginToIntersection, s1) / np.linalg.norm(s1)

        if 0 <= np.linalg.norm(projectionOntoS0) <= np.linalg.norm(s0) and 0 <= np.linalg.norm(projectionOntoS1) <= np.linalg.norm(s1):
            print(f'Intersection at {vectorInitial + a * d}')
            # Find Z height to move at
            zMovingHeight = rectangle[2][2] + constants.robotMovingPadding
            return True, zMovingHeight

        return False, None
