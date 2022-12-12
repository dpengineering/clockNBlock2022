from robotArm import RobotArm
from time import sleep


def main():
    robotArm = RobotArm(11, 10)
    robotArm.setup()
    Z = 100
    radius = 100.0
    speed = 40
    robotArm.moveToPoint(0, 0, 200, speed)
    robotArm.waitWhileMoving()
    print(robotArm.getPosition()[3])
    sleep(1)
    robotArm.bufferWaypoints(True)
    while robotArm.getPosition()[3] > 100:
        pos = robotArm.getPosition()
        print(pos)
        print(pos[1], pos[2], pos[3] - 5, 40)
        print(robotArm.moveToPoint(pos[1], pos[2], pos[3] - 5, 40))
        sleep(0.4)
    robotArm.bufferWaypoints(False)


if __name__ == "__main__":
    main()
