# Crude test for DPi_ClockNBlock Board, just reads all sensors then turns light on and off

from main.DPiClockNBlock import DPiClockNBlock
from time import sleep

dpiClockNBlock = DPiClockNBlock()


def main(boardNum):
    dpiClockNBlock.setBoardNumber(boardNum)
    if not dpiClockNBlock.initialize():
        print("Initialize failed")
        return

    while True:
        print(f'Entrance: {dpiClockNBlock.readEntrance()}')
        print(f'Feed_1: {dpiClockNBlock.readFeed_1()}')
        print(f'Feed_2: {dpiClockNBlock.readFeed_2()}')
        print(f'Exit: {dpiClockNBlock.readExit()} \n')
        print(f'Arrow On: {dpiClockNBlock.arrowOn()}')
        sleep(0.5)
        print(f'Arrow Off: {dpiClockNBlock.arrowOff()}')
        sleep(0.5)


if __name__ == "__main__":
    main(1)

