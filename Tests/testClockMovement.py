import sys
sys.path.insert(0, '../')

from Objects.clock import Clock

clock = Clock()


def main():
    clock.setup()
    clock.setup2()

    while True:
        clock.process()


if __name__ == '__main__':
    main()


