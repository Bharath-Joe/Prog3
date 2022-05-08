import sys

def main():
    inputFile = sys.argv[1]
    frameNums = sys.argv[2]
    algorithm = sys.argv[3]
    algorithmList = ["FIFO", "LRU", "OPT"]
    if algorithm not in algorithmList:
        algorithm = "FIFO"
    if frameNums.isdigit() == False or int(frameNums) <= 0 or int(frameNums) > 256:
        frameNums = 256
    print(inputFile, frameNums, algorithm)

if __name__ == '__main__':
    main()
    