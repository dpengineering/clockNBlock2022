import sys
sys.path.insert(0, "..")

from Objects.clock import Clock
from time import sleep, localtime

clock = Clock()


def main():
    print('initializing')
    clock.initialize()
    print('setting up')
    clock.setup()
    print(clock.getPositionDegrees())
    sleep(1)

    clock.setSpeeds(clock.HOUR_HAND_MAX_SPEED, clock.MINUTE_HAND_MAX_SPEED)
    print(f'we are currently at {clock.dpiStepper.getCurrentPositionInSteps(0)}')

    print('moving to 3:15')
    hourHandSteps, minuteHandSteps = clock.convertTimeToSteps(3, 15, 0)

    clock.moveToPositionsRelative(hourHandSteps, minuteHandSteps, True)

    print(f'Hour hand targeted steps {hourHandSteps}')
    print(f'Hour hand steps per rev {clock.HOUR_HAND_STEPS_PER_REVOLUTION}')
    print(f'ratio between them {round((hourHandSteps / clock.HOUR_HAND_STEPS_PER_REVOLUTION), 3)}')
    print(f'we are actually at {clock.dpiStepper.getCurrentPositionInSteps(0)}')

    print(clock.getPositionDegrees())

    print('waiting for 10 seconds')
    sleep(10)


    t = localtime()
    print(f'moving to Local time {t.tm_hour}:{t.tm_min}:{t.tm_sec}')
    clock.moveToTime(t.tm_hour, t.tm_min, t.tm_sec, True)

    # while True:
    #     clock.process()


if __name__ == '__main__':
    main()
