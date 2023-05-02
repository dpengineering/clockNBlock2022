import sys
sys.path.insert(0, '../')

from Objects.clock import Clock

from dpeaDPi.DPiRobot import DPiRobot

clock = Clock()
dpiRobot = DPiRobot()
dpiRobot.setBoardNumber(0)
dpiRobot.initialize()


def main():

    dpiRobot.homeRobot(True)
    clock.setup()
    # clock.setup2()
    #
    # while True:
    #     clock.process()


if __name__ == '__main__':
    main()


