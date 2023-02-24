from time import strftime, gmtime, sleep
import sys
sys.path.insert(0, '.')

def main():
    locationsFile = open("test", "a")
    # time = strftime("%Y-%m-%d %H:%M", gmtime())
    locationsFile.write(f'Locations saved at  \n')
    locationsFile.close()


if __name__ == "__main__":
    main()

