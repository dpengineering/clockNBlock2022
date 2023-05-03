# This file chooses which version of the project to run.
# Currently an example of what this does, this file will not live in this location on the RPi
# In the project

import sys
import os

from imbuingPersonality.DPi_ClockNBlock_Python.DPiClockNBlock import DPiClockNBlock


def main():
    dpiClockNBlockBoards = []
    for _ in range(4):
        dpiClockNBlockBoards.append(DPiClockNBlock())

    for i, board in enumerate(dpiClockNBlockBoards):
        board.setBoardNumber(i)
        if not board.initialize():
            raise Exception(f"ClockNBlock initialization failed {i}")

    # Check all the entrance sensors. If they are all true run imbuingPersonality
    for board in dpiClockNBlockBoards:
        if not board.readEntrance():
            os.chdir('regularMoves/')
            os.system('python3 main.py')
            sys.exit()

    # Otherwise run imbuingPersonality
    os.chdir('imbuingPersonality/')
    os.system('python3 main.py')
    sys.exit()


if __name__ == '__main__':
    main()




