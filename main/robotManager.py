# Controls how the robot arm moves

import numpy as np
import main.constants as constants
import main.main


class RobotManager:

    # The robot arm will ask us to do two things:
    # Move to a feeder
    # Move to a build site
    #
    # We need to make these two actions interesting - have the robot arm do different things each time it goes to the locations.
    # A few of the ways we can move will overlap:
    #     Move in an interesting pattern on the way to the location.
    #     i.e. move in a circle, square, any polygon,
    #     Move in a spiral for all the upwards moves
    #     Move in a zigzag to the location
    #     Move in a straight line to the location
    #     Move in a straight polar move to the location.
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
    #    The build site will be chosen psudeo randomly based on the following:
    #        We assign weights to each build site based on how far away the clock hand is
    #        And how many blocks need to be placed at said build site.
    #        Additionally, we add a default weight based on how many blocks the build site can hold
    #
    # The robotManager will always return a list of waypoints for the robot arm to follow.
    # The robot arm does not do any logic on its own.
    # Also, the robot arm will always move to polar coordinates. Even if it is going in a straight line
    # cartesian wise.

    def __init__(self):
        self.blockFeeders = main.main.blockFeeders
        self.buildSites = main.main.buildSites
        self.robotPos = None

    def getCommand(self, robotPos, command):
        _STATE_MOVE_TO_FEEDER = 0
        _STATE_MOVE_TO_BUILD_SITE = 3

        if command == _STATE_MOVE_TO_FEEDER:
            return self.moveToFeeder(robotPos)
        elif command == _STATE_MOVE_TO_BUILD_SITE:
            return self.moveToBuildSite(robotPos)
        else:
            return None

    def moveToFeeder(self, robotPos):
        """Moves to a feeder

        Args:
            robotPos (tuple): (x, y) position of the robot arm

        Returns:
            waypoints (list): List of waypoints for the robot arm to follow
        """

        # Different fun things we can do:
        # TODO: Change these to stuff with more personality - organic movements
        Nothing = 0
        NothingPolarMove = 1
        Spiral = 1
        ZigZag = 2
        Circle = 3
        Square = 4
        Triangle = 5
        GetRandomBlock = 6

        # Choose a fun thing to do
        funThingToDo = np.random.choice([Nothing, NothingPolarMove, Spiral, ZigZag, Circle, Square, Triangle, GetRandomBlock])

        # Get the feeder to move to
        if funThingToDo != GetRandomBlock:
            feeder = self.chooseFeeder()
            if feeder is None:
                return None
            finalLocation = feeder.location
        else:
            # Find a build site with a block
            buildSitesWithBlocks = [buildSite for buildSite in self.buildSites if buildSite.currentBlock != 0]
            buildSite = np.random.choice(buildSitesWithBlocks)
            buildSite.currentBlock -= 1
            finalLocation = buildSite.blockPlacements[buildSite.currentBlock - 1]




    def chooseFeeder(self):
        """Chooses a feeder to move to based on the following
            If a feeder is ready, choose a random one
            If no feeder is ready, return None

        Returns:
            feeder (Feeder): Feeder to move to
        """
        # Get a list of all the feeders that are ready
        readyFeeders = [feeder for feeder in self.blockFeeders if feeder.isReady()]

        # If there are no ready feeders, return None
        if len(readyFeeders) == 0:
            return None

        # Choose a random feeder
        feeder = np.random.choice(readyFeeders)

        return feeder

    def chooseBuildSite(self, clockPos):
        """Chooses a build site to move to based on the following
            If a build site is ready, assign weights to each then choose a random one
            If no build site is ready, return None

        Returns:
            buildSite (BuildSite): Build site to move to
        """
        # Get a list of all the build sites that are ready
        readyBuildSites = [buildSite for buildSite in self.buildSites if buildSite.isReady()]

        # If there are no ready build sites, return None
        if len(readyBuildSites) == 0:
            return None

        # Assign weights to each build site
        # The weight is based on how far away the clock hand is and how many blocks are left to place
        # We also add a default weight based on how many blocks the build site can hold
        weights = []
        for index, buildSite in enumerate(readyBuildSites):
            # Get the distance from the clock hand to the build site
            buildSiteTheta = buildSite.location[1]

            # We only want the distance from one side of the clock hand to the build site.
            # The clock hand's degree value should be GREATER THAN the build site's degree value
            distance = clockPos - buildSiteTheta

            # If the distance is less than 90 degrees, it is a priority to finish building
            # Add a 3% weight per block left to place. Max is 98%
            if distance < 90:
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