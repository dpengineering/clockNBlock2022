import math
import numpy as np


def ensureStraightLine(waypoints: list) -> list:
    """Helper function to split up long moves in r, theta to a list of short moves.
    Used for the robot to move with more 'authority'.
    This ensures that the robot will travel in a straight line as it does not do so with a long move.
    Check DPi_Robot firmware to see why. Alternatively, google how linear delta arms work.

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
        distance = math.sqrt(r1 * r1 + r2 * r2 - 2 * r1 * r2 * math.cos(theta1 - theta2))
        # If the distance is greater than 20mm, split our moves up into 20mm segments
        if distance > 20:
            # Number of steps to split our line into
            numSteps = int(distance / 20)

            # To generate the intermediary waypoints, np.linspace() is used on r, theta, and z values individually
            #   We create the points by merging the same index of each array into a tuple, and add it to our list

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


def pathToTarget(currentPos: tuple, target: tuple, offset: float):
    """Helper function to generate the path the robot takes to a target position (With radius offset)

    Args:
        currentPos (tuple): Current position of robot arm in polar coordinates
        target (tuple): Final position the robot moves to
        offset (float): How far away from final position we want to move down
            This is so the robot does not crash into potentially stacked blocks

    Returns:
        list: List of waypoints (tuple) to move the robot to
        tuple: Final position to move, used to check completion of robot's state
    """
    movingPath = []
    targetR, targetTheta, targetZ = target
    # If we are too low, bring the robot up to over the working height.
    if currentPos[2] < 100:
        waypoint = currentPos[0], currentPos[1], 100
        currentPos = waypoint
        movingPath.append(waypoint)

    # Add actual moving points:
    # Go next to point and hover above
    waypoint = targetR - offset, targetTheta, currentPos[2]
    movingPath.append(waypoint)
    currentPos = waypoint

    # Go down to right next to point
    waypoint = currentPos[0], currentPos[1], targetZ + 10
    movingPath.append(waypoint)
    currentPos = waypoint

    # slide over to point
    waypoint = targetR, targetTheta, currentPos[2]
    movingPath.append(waypoint)

    movingPath.append(target)

    return movingPath, target


def polarToCartesian(position: tuple):
    """Helper function to change polar coordinates to cartesian

    Args:
        position (tuple): Current robot position in polar plane

    Returns:
        x, y, z (tuple (float)): Returns the cartesian coordinates that correspond to the polar coordinates

    """
    r, theta, z = position
    x = r*math.cos(theta)
    y = r*math.sin(theta)
    return x, y, z


def main():

    x, y, z = -276.7, -210.1, -63
    # Convert to Polar Coords
    r = math.sqrt(x ** 2 + y ** 2)
    theta = math.atan2(y, x)
    print(r, theta, z)

if __name__ == "__main__":
    main()
