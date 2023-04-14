from Objects.buildSite import BuildSite
import Objects.constants as constants

# Tests functions in buildSite.py
# to be run with debugger to see how the functions work and store data

def main():
    blockPlacementArr = constants.placementArrays[0]
    location = constants.buildLocations[0][0]
    location1 = constants.buildLocations[0][1]
    BuildSite0 = BuildSite(0, location, location1)

    # Setup buildSite
    BuildSite0.setup()
    print(f'block Placements: {BuildSite0.blockPlacements}')
    print(f'current block: {BuildSite0.currentBlock}')
    print(f'intersection plane: {BuildSite0.intersectionRectangle}')


if __name__ == '__main__':
    main()


