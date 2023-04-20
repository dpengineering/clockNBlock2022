from Objects.robotManager import RobotManager


def main():
    # Create the robot manager object
    robotManager = RobotManager()

    # Generate the set of points to move to
    startingPosition = (293.6, 350.570, -1442.8)
    finalPosition = (338.6, 127.862, -1471.2)

    # Generate the path
    path = robotManager.planMove(startingPosition, finalPosition)
    [print(f'index: {idx}, point: {point}') for idx, point in enumerate(path)]

    # Ensure straght line
    path = robotManager.ensureStraightLine(path)
    [print(f'index: {idx}, point: {point}') for idx, point in enumerate(path)]



if __name__ == '__main__':
    main()


