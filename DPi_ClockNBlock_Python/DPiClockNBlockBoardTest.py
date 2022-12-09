# Rough test for functionality of the DPi ClockNBlock board

from main.DPiClockNBlock import DPiClockNBlock
from time import sleep


def main():
    dpiClockNBlock = DPiClockNBlock()

    dpiClockNBlock.setBoardNumber(0)

    if not dpiClockNBlock.initialize():
        print("Communication with board failed")
        return

    dpiClockNBlock.arrowOn()

    while True:
        print(dpiClockNBlock.readEntrance())
        sleep(0.1)


if __name__ == "__main__":
    main()
