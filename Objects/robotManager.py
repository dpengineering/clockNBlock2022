# Controls how the robot arm moves
import numpy as np
import Objects.constants as constants
import math


class RobotManager:

    # The robot arm will ask us to do two things:
    # Move to a feeder
    # Move to a build site
    #
    # We need to make these two actions interesting - have the robot arm do different things each time it goes to the locations.
    # A few of the ways we can move will overlap:
    #     Move in a zigzag to the location
    #     Move in a straight line to the location
    #     Move in a straight polar move to the location.
    #     Randomly do a few circles
    #
    # There will also be a few specific things that the robot arm will do based on its move
    # To pick up a block, we can choose some random block to pick up. i.e. pick up a block from a tower
    #
    # To place a block, we can either place a block at an interesting location to be picked up later
    # Or we can just go place a block.
    # This is around 7 different things we can do for each placement
    # Also, each of these moves will have to be on average 30 seconds for the whole cycle
    #
    # How we choose the feeders and build sites will be based on the following:
    #    The feeder will be chosen randomly out of the ones that are ready.
    #        If no feeder is ready, the robot arm will home. Not go to a build site to pick up a block.
    #    The build site will be chosen pseudo randomly based on the following:
    #        We assign weights to each build site based on how far away the clock hand is
    #        And how many blocks need to be placed at said build site.
    #        Additionally, we add a default weight based on how many blocks the build site can hold
    #
    # The robotManager will always return a list of waypoints for the robot arm to follow.
    # The robot arm does not do any logic on its own.
    # Also, the robot arm will always move to polar coordinates. Even if it is going in a straight line
    # cartesian wise.

    def __init__(self, buildSites, blockFeeders):
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

        # Different fun things we can do:
        Nothing = 0
        PolarMove = 1
        ZigZag = 2
        Circle = 3
        GetRandomBlock = False

        # Choose a fun thing to do
        # funThingToDo = np.random.choice([Nothing, PolarMove, ZigZag, Spiral])
        funThingToDo = np.random.choice([Nothing, PolarMove, Circle])

        # Decide if we want to get a random block, this has a 5% chance of happening
        if np.random.random() < 0.05:
            GetRandomBlock = True

        # Get the buildSite to move to
        if GetRandomBlock:
            buildSitesWithBlocks = [buildSite for buildSite in self.buildSites if buildSite.currentBlock != 0]

            # Check if list is empty
            if not buildSitesWithBlocks:
                return None

            buildSite = np.random.choice(buildSitesWithBlocks)
            buildSite.currentBlock -= 1
            finalLocation = buildSite.blockPlacements[buildSite.currentBlock]
            print(f'Robot arm getting random block from build site {buildSite.buildSiteNumber}')
        else:
            # Find a feeder with blocks
            feeder = self.chooseFeeder()
            if feeder is None:
                return None
            finalLocation = feeder.location
            print(f'Robot arm moving to feeder {feeder.index}')

        # Now that we have our final locations, we plan our route there
        if funThingToDo == PolarMove:
            print('Robot arm polar move to feeder')
            waypoints, _checkUpUntilIndex = self.planStraightMove(robotPos, finalLocation)
            waypoints = self.ensureStraightLinePolar(waypoints)

        elif funThingToDo == ZigZag:
            print('Robot arm zig zag move to feeder')
            waypoints, _checkUpUntilIndex = self.planZigZagMove(robotPos, finalLocation)
            waypoints = self.ensureStraightLineCartesian(waypoints)

        elif funThingToDo == Circle:
            print('Robot arm circle move to feeder')
            waypoints = self.planCircle(robotPos, finalLocation)
            waypoints = self.ensureStraightLineCartesian(waypoints)

        else:
            print('Robot arm straight move to feeder')
            waypoints, _checkUpUntilIndex = self.planStraightMove(robotPos, finalLocation)
            waypoints = self.ensureStraightLineCartesian(waypoints)

        return waypoints

    def moveToBuildSite(self, robotPos: tuple, clockPos: float):
        """Moves to a build site
        Args:
            robotPos (tuple): (r, theta, z) position of the robot arm
            clockPos (float): Position of the clock hand
        Returns:
            waypoints (list): List of waypoints for the robot arm to follow
        """

        # Different fun things we can do:
        Nothing = 0
        PolarMove = 1
        ZigZag = 2
        Circle = 3
        FakePlacement = 4

        # Choose a fun thing to do
        # funThingToDo = np.random.choice([Nothing, PolarMove, ZigZag, Spiral, FakePlacement])
        funThingToDo = np.random.choice([Nothing, PolarMove, Circle, FakePlacement])

        # Get the buildSite to move to
        buildSite = self.chooseBuildSite(clockPos)

        # If there are no build sites, return None
        if buildSite is None:
            return None

        finalLocation = buildSite.placeNextBlock()
        if finalLocation is None:
            return None

        # Now that we have our final locations, we plan our route there
        if funThingToDo == PolarMove:
            print('Robot arm polar move to build site')
            waypoints, _checkUpUntilIndex = self.planStraightMove(robotPos, finalLocation)
            waypoints = self.ensureStraightLinePolar(waypoints)

        elif funThingToDo == ZigZag:
            print('Robot arm zig zag move to build site')
            waypoints, _checkUpUntilIndex = self.planZigZagMove(robotPos, finalLocation)
            waypoints = self.ensureStraightLineCartesian(waypoints)

        elif funThingToDo == Circle:
            print('Robot arm circle move to build site')
            waypoints = self.planCircle(robotPos, finalLocation)
            waypoints = self.ensureStraightLineCartesian(waypoints)

        elif funThingToDo == FakePlacement:
            print('Robot arm fake placement move to build site')
            # Create our list of locations. We know our final location, so we just choose other build open build sites

            # Get a list of all ready build sites
            readyBuildSites = [buildSite for buildSite in self.buildSites if buildSite.isReadyFlg]

            # remove the build site we are going to
            readyBuildSites.remove(buildSite)

            # Choose 1-2 random build sites if we have more than 1
            if len(readyBuildSites) > 1:
                numBuildSites = np.random.choice([1, 2])
                randomBuildSites = np.random.choice(readyBuildSites, numBuildSites, replace=True)
                randomBuildSites = [buildSite.blockPlacements[buildSite.currentBlock] for buildSite in randomBuildSites]
            else:
                randomBuildSites = readyBuildSites
                randomBuildSites = [buildSite.blockPlacements[buildSite.currentBlock] for buildSite in randomBuildSites]

            # Add the final location to the list
            randomBuildSites = list(randomBuildSites)
            randomBuildSites.append(finalLocation)

            waypoints = self.planFakePlacement(robotPos, randomBuildSites)
            waypoints = self.ensureStraightLineCartesian(waypoints)

        else:
            print('Robot arm straight move to build site')
            waypoints, _checkUpUntilIndex = self.planStraightMove(robotPos, finalLocation)
            waypoints = self.ensureStraightLineCartesian(waypoints)

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

        print(f'Ready feeders: {[feeder.index for feeder in readyFeeders]}')

        # If there are no ready feeders, return None
        if len(readyFeeders) == 0:
            return None

        # Choose a random feeder
        feeder = np.random.choice(readyFeeders)

        return feeder

    def chooseBuildSite(self, clockPos: float):
        """Chooses a build site to move to based on the following
            If a build site is ready, assign weights to each then choose a random one
            If no build site is ready, return None

        Returns:
            buildSite (BuildSite): Build site to move to
        """
        # Get a list of all the build sites that are ready
        readyBuildSites = [buildSite for buildSite in self.buildSites if buildSite.isReadyFlg]

        print(f'Ready build sites: {[buildSite.index for buildSite in readyBuildSites]}')

        # If there are no ready build sites, return None
        if len(readyBuildSites) == 0:
            return None

        # Assign weights to each build site
        # The weight is based on how far away the clock hand is and how many blocks are left to place
        # We also add a default weight based on how many blocks the build site can hold
        weights = []
        for index, buildSite in enumerate(readyBuildSites):
            # Get the distance from the clock hand to the build site
            buildSiteTheta = buildSite.location0[1]

            # We only want the distance from one side of the clock hand to the build site.
            # The clock hand's degree value should be GREATER THAN the build site's degree value
            distance = (clockPos - buildSiteTheta) % 360

            # If the distance is less than 90 degrees, it is a priority to finish building
            # Add a 3% weight per block left to place. Max is 98%
            if distance < 80:
                blocksToPlace = len(buildSite.blockPlacements) - buildSite.currentBlock
                weight = 0.03 * blocksToPlace
                if weight > 0.98:
                    weight = 0.98

                weights.append(weight)
            else:
                # If the distance is greater than 90 degrees, it is not a priority to finish building
                # Add a 0.5% weight per block left to place. Max is 98%
                blocksToPlace = len(buildSite.blockPlacements) - buildSite.currentBlock
                weight = 0.005 * blocksToPlace
                if weight > 0.98:
                    weight = 0.98

                weights.append(weight)

        # We have our weights, now we need to normalize them
        weightsSum = sum(weights)
        if weightsSum != 1:
            weights = [weight / weightsSum for weight in weights]

        # Choose a random build site
        buildSite = np.random.choice(readyBuildSites, p=weights)

        return buildSite

    def planStraightMove(self, currentPos: tuple, targetPos: tuple) -> tuple[list, int]:
        """ Plans a path from the current position to the target position
        Args:
            currentPos (tuple): Current position of the robot
            targetPos (tuple): Target position of the robot
        Returns:
            waypoints (list): List of waypoints to travel to
        """
        waypoints = []
        currentR, currentTheta, currentZ = currentPos
        targetR, targetTheta, targetZ = targetPos

        if currentZ < -1400:
            travelHeight = currentZ + 100
        else:
            travelHeight = currentZ + 20

        # The first move will always be moving up.
        waypoints.append((currentR, currentTheta, travelHeight))

        # Next, check if we need to move in towards the center
        if currentR > self.maximumMovingR:
            # Move in towards the center
            waypoints.append((self.maximumMovingR, currentTheta, travelHeight))
            currentR = self.maximumMovingR

        # Then, move next to and above the target location
        sign = 1 if currentTheta > targetTheta else -1

        waypoints.append((targetR, targetTheta + sign * self.offSetAngle, travelHeight))

        # So we don't check waypoints that will place a block.
        checkWaypointsUpUntil = len(waypoints)

        # Go down to 5mm above the target location
        waypoints.append((targetR, targetTheta + sign * self.offSetAngle, targetZ + 5))

        # Go over the location
        waypoints.append((targetR, targetTheta, targetZ + 5))

        # Go down to the target location
        waypoints.append((targetR, targetTheta, targetZ))

        # Check if we are intersecting any obstacles
        dodgeDict = {}
        for building in self.buildSites:
            obstacle = building.intersectionRectangle
            for i in range(checkWaypointsUpUntil - 1):
                # Check if the line intersects the obstacle
                intersection, point = self.checkIntersection(waypoints[i], waypoints[i + 1], obstacle)
                if intersection:
                    print("Found intersection")
                    # If it does, we need to dodge it
                    direction = np.random.choice([0, 1])
                    dodgeDict[i] = self.dodgeObstacle(waypoints[i], waypoints[i + 1], obstacle, point, direction)

        for key in dodgeDict:
            waypoints = waypoints[:key] + dodgeDict[key] + waypoints[key + 1:]

        return waypoints, checkWaypointsUpUntil

    def planZigZagMove(self, currentPos: tuple, targetPos: tuple) -> tuple[list, int]:
        """ Plans a zig-zagging path from the current position to the target position
        Args:
            currentPos (tuple): Current position of the robot
            targetPos (tuple): Target position of the robot
        Returns:
            waypoints (list): List of waypoints to travel to
        """
        sign = np.random.choice([-1, 1])

        zigZagDistance = 100  # The threshold for when to zig-zag in mm
        zigZagAngleRange = (30, 60)  # The angle to zig-zag at
        zigZagAngle = np.random.randint(zigZagAngleRange[0], zigZagAngleRange[1])  # The angle to zig-zag at

        # As this is a zig-zag, we just need to alter all the straight moves
        # Get the waypoints for a straight move
        waypoints, checkWaypointsUpUntil = self.planStraightMove(currentPos, targetPos)

        checkWaypointsValue = waypoints[checkWaypointsUpUntil - 1]

        zigZagDict = {}
        # Loop through the waypoints and alter the moves
        for i in range(len(waypoints) - 1):
            # Get the current and next waypoint cartesian coordinates
            initialPoint = constants.polarToCartesian(waypoints[i])

            finalPoint = constants.polarToCartesian(waypoints[i + 1])

            # Represent our move as a vector in the form v0 + t * d
            # Where v0 is the starting point, d is the direction vector and t is a scalar corresponding to the distance
            v0 = np.array(initialPoint)
            d = (np.array(finalPoint) - v0) / np.linalg.norm(np.array(finalPoint) - v0)
            t = np.linalg.norm(np.array(finalPoint) - v0)

            # Get the two direction vectors for the zig-zag
            # The first one is at the zig-zag angle
            # And the second one is at the negative zig-zag angle
            rotationMatrix = np.array([[np.cos(np.deg2rad(zigZagAngle)), -np.sin(np.deg2rad(zigZagAngle))],
                                        [np.sin(np.deg2rad(zigZagAngle)), np.cos(np.deg2rad(zigZagAngle))]])

            zigZagDirection0 = rotationMatrix @ d
            zigZagDirection1 = -rotationMatrix @ d

            # Split the move up into segments of length zigZagDistance
            # If the move is less than zigZagDistance, do a single zig-zag
            if t < zigZagDistance:
                dist = t / 2
                point = v0 + dist * zigZagDirection0
                zigZagDict[i] = [constants.cartesianToPolar(point)]

            else:
                numSteps = round(t / zigZagDistance)
                stepDistance = t / numSteps
                intermediateStoppingPoints = []

                # Get the first move
                dist = stepDistance / 2
                point = v0 + dist * zigZagDirection0
                intermediateStoppingPoints.append(constants.cartesianToPolar(point))

                for j in range(numSteps - 2):
                    # Every other move follows this scheme
                    if j % 2 == 0:
                        dist = stepDistance
                        point = v0 + dist * zigZagDirection0
                        intermediateStoppingPoints.append(constants.cartesianToPolar(point))
                    else:
                        dist = stepDistance
                        point = v0 + dist * zigZagDirection1
                        intermediateStoppingPoints.append(constants.cartesianToPolar(point))

                # Finally, add the last move
                dist = stepDistance / 2
                point = v0 + dist * zigZagDirection1
                intermediateStoppingPoints.append(constants.cartesianToPolar(point))

                # Verify this is our target point.
                print(f'Final point: {waypoints[i + 1]}')
                print(f'Zig zag final point: {intermediateStoppingPoints[-1]}')
                # assert np.allclose(intermediateStoppingPoints[-1], waypoints[i+1], atol=10)


        for key in zigZagDict:
            waypoints = waypoints[:key] + zigZagDict[key] + waypoints[key + 1:]

        checkWaypointsUpUntil = waypoints.index(checkWaypointsValue)

        # Check if we are intersecting any obstacles
        dodgeDict = {}
        for building in self.buildSites:
            obstacle = building.intersectionRectangle
            for i in range(checkWaypointsUpUntil - 1):
                # Check if the line intersects the obstacle
                intersection, point = self.checkIntersection(waypoints[i], waypoints[i + 1], obstacle)
                if intersection:
                    print("Found intersection")
                    # If it does, we need to dodge it
                    direction = np.random.choice([0, 1])
                    dodgeDict[i] = self.dodgeObstacle(waypoints[i], waypoints[i + 1], obstacle, point, direction)

        for key in dodgeDict:
            waypoints = waypoints[:key] + dodgeDict[key] + waypoints[key + 2:]

        return waypoints, checkWaypointsUpUntil

    def planCircle(self, currentPos: tuple, targetPos: tuple) -> list:
        """ Plans a path including a circle from the current position to the target position
                Args:
                    currentPos (tuple): Current position of the robot
                    targetPos (tuple): Target position of the robot
                Returns:
                    waypoints (list): List of waypoints to travel to
                """
        waypoints = []
        currentR, currentTheta, currentZ = currentPos
        targetR, targetTheta, targetZ = targetPos

        circleRadius = 200

        if currentZ < -1400:
            travelHeight = currentZ + 100
        else:
            travelHeight = currentZ + 20

        # The first move will always be moving up.
        waypoints.append((currentR, currentTheta, travelHeight))

        # Now move inwards on the edge of the circle
        waypoints.append((circleRadius, currentTheta, travelHeight))

        # Decide how many rotations to do
        numRotations = np.random.randint(1, 3)

        # Now we move around the circle
        for i in range(numRotations):
            for j in range(360):
                currentTheta += 1
                waypoints.append((circleRadius, currentTheta, travelHeight))
            currentTheta = currentTheta % 360

        # Move along the circle to the target theta
        for i in range(currentTheta, targetTheta):
            waypoints.append((circleRadius, i, travelHeight))


        # Now we move to the target position
        pathToTarget, _checkUpUntil = self.planStraightMove(waypoints[-1], targetPos)

        waypoints += pathToTarget

        return waypoints

    def planFakePlacement(self, currentPos, targetPositions: list[tuple]) -> list:
        # This one is just a string of straight moves.
        waypoints = []
        print(f'Target positions: {targetPositions}')
        for targetPos in targetPositions:
            path, _extra = self.planStraightMove(currentPos, targetPos)
            waypoints += path
            currentPos = targetPos

        print(waypoints)
        return waypoints

    @staticmethod
    def ensureStraightLineCartesian(waypoints: list) -> list:
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

        # Convert our list of waypoints in cartesian coordinates to a list in polar coordinates
        straightWaypoints = [constants.cartesianToPolar(waypoint) for waypoint in straightWaypoints]

        return straightWaypoints

    @staticmethod
    def ensureStraightLinePolar(waypoints: list) -> list:
        """Ensures a straight line move in polar coordinates
        This will cause the robot to move in an arc and in a straight line on the polar plane
        Args:
            waypoints (list): List of polar waypoints with possible long moves
        Returns:
            straightWaypoints (list): List of waypoints with long moves broken up in polar coordinates
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
                numSteps = int(distance / 20)

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

    @staticmethod
    def checkIntersection(initialPoint: tuple, finalPoint: tuple, rectangle: list) -> tuple:
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

        if 0 <= np.linalg.norm(projectionOntoS0) <= np.linalg.norm(s0) and 0 <= np.linalg.norm(
                projectionOntoS1) <= np.linalg.norm(s1):
            print(f'Intersection at {vectorInitial + a * d}')

            return True, vectorInitial + a * d

        return False, None

    @staticmethod
    def dodgeObstacle(initialPoint: tuple, finalPoint: tuple, obstacle: list, intersectionPoint: tuple, direction: bool = True) -> list:
        """Dodge over an obstacle represented by a polygon - does not append initial or final points
        Args:
            initialPoint (tuple): The starting point of the line in polar coordinates
            finalPoint (tuple): The ending point of the line in polar coordinates
            obstacle (list): The obstacle to dodge around, in the form [point0, point1, point2, point3]. All points are in polar coordinates
            intersectionPoint (tuple): The point where the line intersects the obstacle
            direction (bool): The direction we are dodging the obstacle: True -> up, False -> around
        Returns:
            waypoints (list): List of waypoints to dodge around the polygon in polar coordinates
        """

        waypoints = []

        # Convert the points to cartesian coordinates
        initialPoint = constants.polarToCartesian(initialPoint)
        finalPoint = constants.polarToCartesian(finalPoint)

        # Calculate vector from initial point to intersection point
        vectorInitial = np.array(initialPoint)

        # Split this vector up into the form v0 + t * d
        # Where v0 is the initial point, d is the direction vector, and t is the scalar that corresponds to the length of the vector
        d = (np.array(intersectionPoint) - vectorInitial) / np.linalg.norm(np.array(intersectionPoint) - vectorInitial)
        t = np.linalg.norm(np.array(intersectionPoint) - vectorInitial)

        # Find the point where we want to stop the robot in order to dodge the obstacle
        # To do this, we will shorten the distance, t by the robotHeadRadius + blockSize / 2 + robotMovingPadding
        # The 10mm is just padding to make sure we don't hit the obstacle

        # First, calculate the distance we need to shorten the vector by
        distanceToShorten = constants.robotHeadRadius + constants.blockSize / 2 + constants.robotMovingPadding

        # Do the same thing as above, but with the final point
        vectorFinal = np.array(finalPoint)
        dFinal = (np.array(intersectionPoint) - vectorFinal) / np.linalg.norm(np.array(intersectionPoint) - vectorFinal)
        tFinal = np.linalg.norm(np.array(intersectionPoint) - vectorFinal)

        # Calculate the distance we need to shorten the vector by
        distanceToShortenFinal = constants.robotHeadRadius + constants.blockSize / 2 + constants.robotMovingPadding

        # Then, calculate the new vector
        if distanceToShorten > t:
            # If the distance is greater than the length of the vector, we can't dodge the obstacle
            # So, we will just go straight up and around it.
            # This case should never actually happen, but it's here just in case
            zHeight = obstacle[2][2] + 10

            waypoints.append((initialPoint[0], initialPoint[1], zHeight))
            # Then just go over and above the final point
            waypoints.append((finalPoint[0], finalPoint[1], zHeight))
            # Then go down to the final point
            waypoints.append(finalPoint)
            return waypoints

        elif distanceToShortenFinal > tFinal:
            # If the distance is greater than the length of the vector, we can't dodge the obstacle
            # So, we will just go straight up and around it.
            # This case should never actually happen, but it's here just in case
            zHeight = obstacle[2][2] + 10

            waypoints.append((initialPoint[0], initialPoint[1], zHeight))
            # Then just go over and above the final point
            waypoints.append((finalPoint[0], finalPoint[1], zHeight))

            # Don't go down, this will crash the robot

            return waypoints


        # Calculate the new vector
        initialStoppingPoint = vectorInitial + (t - distanceToShorten) * d
        finalStoppingPoint = vectorFinal + (tFinal - distanceToShortenFinal) * dFinal

        # Go to this point
        waypoints.append((initialStoppingPoint[0], initialStoppingPoint[1], initialStoppingPoint[2]))

        if direction:
            zHeight = obstacle[2][2] + 10
            print(f'Z height: {zHeight}')

            # Go up
            waypoints.append((initialStoppingPoint[0], initialStoppingPoint[1], zHeight))

            # Go over and above the finalStoppingPoint
            waypoints.append((finalStoppingPoint[0], finalStoppingPoint[1], zHeight))

            # Go down to the finalStoppingPoint
            waypoints.append((finalStoppingPoint[0], finalStoppingPoint[1], finalStoppingPoint[2]))

            # Convert all the waypoints to polar coordinates
            for i, waypoint in enumerate(waypoints):
                waypoints[i] = constants.cartesianToPolar(waypoint)
        else:

            # Convert to polar coordinates
            initialStoppingPoint = constants.cartesianToPolar(initialStoppingPoint)
            finalPoint = constants.cartesianToPolar(finalPoint)

            # Dodge around the obstacle by moving towards the center
            waypoints.append(
                (obstacle[0][0] + constants.robotMovingPadding, initialStoppingPoint[1], initialStoppingPoint[2]))

            # Go over
            waypoints.append((obstacle[0][0] + constants.robotMovingPadding,
                              initialStoppingPoint[1] + constants.degreesPerBlock, initialStoppingPoint[2]))

            # Go back
            waypoints.append(
                (initialStoppingPoint[0], initialStoppingPoint[1] + constants.degreesPerBlock, initialStoppingPoint[2]))

            # Go to final point
            waypoints.append(finalPoint)

        return waypoints
