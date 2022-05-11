import sys

TLB = []
pageTable = {}

def main():
    inputFile = sys.argv[1]
    frameNums = sys.argv[2]
    algorithm = sys.argv[3]
    algorithmList = ["FIFO", "LRU", "OPT"]
    if algorithm not in algorithmList:
        algorithm = "FIFO"
    if frameNums.isdigit() == False or int(frameNums) <= 0 or int(frameNums) > 256:
        frameNums = 256
    # print(inputFile, frameNums, algorithm)
    addressList = readFile(inputFile)
    if algorithm == "FIFO":
        doFIFO(addressList, frameNums)
    elif algorithm == "LRU":
        doLRU(addressList, frameNums)
    elif algorithm == "OPT":
        doOPT(addressList, frameNums)

def readFile(inputFile):
    try:
        f = open(inputFile, "r")
    except FileNotFoundError:
        print("Wrong file or file path")
        exit()
    content = f.read()
    listOfAddresses = content.split("\n")
    if listOfAddresses[len(listOfAddresses) - 1] == "":
        del listOfAddresses[len(listOfAddresses) - 1]
    return listOfAddresses

def doFIFO(addressList, numOfFrames):
    f = open("BACKING_STORE.bin", "rb")
    line = f.readline()
    print(line)

def doLRU(addressList, numOfFrames):
    print("You are in LRU function.")

def doOPT(addressList, numOfFrames):
    print("You are in LRU function.")


if __name__ == '__main__':
    main()
    