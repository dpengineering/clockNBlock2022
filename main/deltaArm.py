"""deltaArm functions for the ClockNBlock tower"""

from dpeaDPi.DPiRobot import DPiRobot
from time import sleep

class deltaArm:


    dpiRobot = DPiRobot()

    """Constructor for delta arm"""
    def __init__(self, boardNumber: int):
        dpiRobot.setBoardNumber(boardNumber)
        
