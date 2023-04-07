# Test program that runs all the feeders continuously
from main.blockFeeder import BlockFeeder
import main.constants
from dpeaDPi.DPiSolenoid import DPiSolenoid

constants = main.constants

dpiSolenoid = DPiSolenoid()
dpiSolenoid.setBoardNumber(0)
if not dpiSolenoid.initialize():
    raise Exception("Solenoid initialization failed")

blockFeeders = []
NUM_BLOCK_FEEDERS = 4

for i in range(NUM_BLOCK_FEEDERS):
    # The positions don't actually matter
    blockFeeders.append(BlockFeeder(i, constants.blockFeederSolenoids[i], i, dpiSolenoid))


def setup():
    for i in range(NUM_BLOCK_FEEDERS):
        print(f"setup blockfeeder {i}")
        if not blockFeeders[i].setup():
            raise Exception(f"BlockFeeder {i} setup failed")


def main():
    setup()
    while True:
        for i, blockFeeder in enumerate(blockFeeders):
            print(f'Running blockfeeder {i}')
            blockFeeder.process()
            print(blockFeeder.state)


if __name__ == "__main__":
    main()



