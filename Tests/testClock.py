from main.clock import Clock
from time import sleep, localtime

clock = Clock()


def main():
    clock.initialize()
    print(clock.getPositionDegrees())
    sleep(1)

    clock.setSpeeds(clock.HOUR_HAND_MAX_SPEED, clock.MINUTE_HAND_MAX_SPEED)

    hourHandSteps, minuteHandSteps = clock.convertTimeToSteps(3, 15, 0)

    clock.moveToPositionsRelative(hourHandSteps, minuteHandSteps, True)

    print(clock.getPositionDegrees())

    sleep(1)

    t = localtime()
    hourHandSteps, minuteHandSteps = clock.convertTimeToSteps(t.tm_hour, t.tm_min, t.tm_sec)
    clock.moveToPositionsRelative(hourHandSteps, minuteHandSteps, True)

    while True:
        clock.process()


if __name__ == '__main__':
    main()

