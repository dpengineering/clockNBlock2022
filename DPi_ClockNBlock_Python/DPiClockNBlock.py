#      ******************************************************************
#      *                                                                *
#      *                   DPiClockNBlock Library                       *
#      *                                                                *
#      *            Arnav Wadhwa                   11/27/2022           *
#      *                                                                *
#      ******************************************************************

from dpeaDPi.DPiNetwork import DPiNetwork

dpiNetwork = DPiNetwork()

#
# DPiNetwork DPiClockNBLock commands
#
_CMD_DPi_CLOCKNBLOCK__PING                  = 0x00
_CMD_DPi_CLOCKNBLOCK__INITIALIZE            = 0x01
_CMD_DPi_CLOCKNBLOCK__READ_ENTRANCE         = 0x02
_CMD_DPi_CLOCKNBLOCK__READ_FEED_1           = 0x03
_CMD_DPi_CLOCKNBLOCK__READ_FEED_2           = 0x04
_CMD_DPi_CLOCKNBLOCK__READ_EXIT             = 0x05
_CMD_DPi_CLOCKNBLOCK__ARROW_ON              = 0x06
_CMD_DPi_CLOCKNBLOCK__ARROW_OFF             = 0x07

#
# other constants used by this class
#
_NUMBER_OF_DPi_CLOCKNBLOCK_SENSORS = 4
_DPiNETWORK_TIMEOUT_PERIOD_MS = 3
_DPiNETWORK_BASE_ADDRESS = 0x3C

class DPiClockNBlock:
    #
    # attributes local to this class
    #
    _slaveAddress = _DPiNETWORK_BASE_ADDRESS
    _commErrorCount = 0

    #
    # constructor for the DPiClockNBlock class
    #
    def __init__(self):
        pass

    # ---------------------------------------------------------------------------------
    #                                 Private functions
    # ---------------------------------------------------------------------------------

    #
    # send a command to the DPiSolenoid, command's additional data must have already been "Pushed".
    # After this function returns data from the device is retrieved by "Popping"
    #    Enter:  command = command byte
    #    Exit:   True returned on success, else False
    #
    def __sendCommand(self, command: int):
        (results, failedCount) = dpiNetwork.sendCommand(self._slaveAddress, command, _DPiNETWORK_TIMEOUT_PERIOD_MS)
        self._commErrorCount += failedCount
        return results

    # ---------------------------------------------------------------------------------
    #                                Public functions
    # ---------------------------------------------------------------------------------

    #
    # set the DPiSolenoid board number
    #    Enter:  boardNumber = DPiSolenoid board number (0 - 3)
    #
    def setBoardNumber(self, boardNumber: int):
        if (boardNumber < 0) or (boardNumber > 3):
            boardNumber = 0
        self._slaveAddress = _DPiNETWORK_BASE_ADDRESS + boardNumber

    #
    # ping the board
    #    Exit:   True returned on success, else False
    #
    def ping(self):
        return self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__PING)

    #
    # initialize the board to its "power on" configuration
    #    Exit:   True returned on success, else False
    #
    def initialize(self):
        return self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__INITIALIZE)

    #
    # read from entrance sensor
    #   Exit: True if on, else false
    #
    def readEntrance(self):
        self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__READ_ENTRANCE)
        return not dpiNetwork.popUint8()


    #
    # read from feed 1 sensor
    #   Exit: True if on, else false
    #
    def readFeed_1(self):
        self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__READ_FEED_1)
        return not dpiNetwork.popUint8()


    #
    # read from feed 2 sensor
    #   Exit: True if on, else false
    #
    def readFeed_2(self):
        self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__READ_FEED_2)
        return not dpiNetwork.popUint8()


    #
    # read from exit sensor
    #   Exit: True if on, else false
    #
    def readExit(self):
        self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__READ_EXIT)
        return not dpiNetwork.popUint8()

    #
    # Turn arrow on
    #   Exit: True on success, else False
    #
    def arrowOn(self):
        return self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__ARROW_ON)

    #
    # Turn arrow off
    #   Exit: True on success, else False
    #
    def arrowOff(self):
        return self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__ARROW_OFF)


    #
    # Toggle arrow
    #   Exit: True on success, else False
    #
    def arrowToggle(self, onOffValue: bool):
        if onOffValue:
            return self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__ARROW_ON)
        else:
            return self.__sendCommand(_CMD_DPi_CLOCKNBLOCK__ARROW_OFF)