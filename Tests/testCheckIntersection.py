import time

from main.robotManager import RobotManager

robotArm = RobotManager()


def main():
    initialPoint = (1, 1, 3)
    finalPoint = (-1, -1, 3)
    rect = [(-1, 1, -1), (-1, 1, 2), (1, -1, 2), (1, -1, -1)]
    status = robotArm.checkIntersectionCartesian(initialPoint, finalPoint, rect)
    print(status)



if __name__ == '__main__':
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print(f"Time taken: {end - start}")
