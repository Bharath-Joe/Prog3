import sys

tlb = [] # [(logical memory page num, physical memory frame number), ...]
pageTable = {} # pageNum: [FrameNum, validBit]
physicalMemory = [] # (frameNum, page)

def main():
    inputFile = sys.argv[1]
    frameNums = sys.argv[2]
    algorithm = sys.argv[3]
    algorithmList = ["FIFO", "LRU", "OPT"]
    if algorithm not in algorithmList:
        algorithm = "FIFO"
    if frameNums.isdigit() == False or int(frameNums) <= 0 or int(frameNums) > 256:
        frameNums = 256
    for j in range(256):
        pageTable[j] = None
    addressList = readFile(inputFile)
    driver(addressList, frameNums, algorithm)

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

def updateTLB(pageNum, frameNumber):
    if len(tlb) < 16:
        tlb.append((pageNum, frameNumber))
    elif len(tlb) == 16:
        tlb.pop(0)
        tlb.append((pageNum, frameNumber))

def updatePM(pageNum, frameNumber, numOfFrames, algorithm):
    if len(physicalMemory) < numOfFrames:
        physicalMemory.append((frameNumber, pageNum))
        frameNumber += 1
    elif len(physicalMemory) == numOfFrames:
        if algorithm == "FIFO":
            frameNumber = doFIFO(physicalMemory, pageNum)
        elif algorithm == "LRU":
            frameNumber = doLRU(physicalMemory, pageNum, frameNumber)
        elif algorithm == "OPT":
            frameNumber = doOPT(physicalMemory, pageNum, frameNumber)
    return frameNumber

def driver(addressList, numOfFrames, algorithm):
    frameNumber = 0
    pageFaultCount = 0
    missCount = 0
    hitCount = 0
    numOfFrames = int(numOfFrames)
    f = open("BACKING_STORE.bin", "rb")
    for address in addressList:
        f.seek(int(address))
        byteReferenced = f.read(1)
        byteReferenced = int(byteReferenced.hex(), 16)
        pageNum = int(address) // 256
        if byteReferenced >= 128:
            byteReferenced = byteReferenced - 256
        f.seek((int(address)//256)*256)
        contents = f.read(256)

        hitCountBefore = hitCount
        for ting in tlb:
            if pageNum == ting[0]:
                hitCount += 1
                break
        if hitCountBefore == hitCount: # Not a hit
            if pageTable[pageNum] == None or pageTable[pageNum][1] == 0: # Page Fault
                pageFaultCount += 1
                missCount += 1
                pageTable[pageNum] = (frameNumber, 1)
                updateTLB(pageNum, frameNumber)
                frameNumber = updatePM(pageNum, frameNumber, numOfFrames, algorithm)
            else: # Soft Miss
                missCount += 1
                updateTLB(pageNum, frameNumber)
                frameNumber = updatePM(pageNum, frameNumber, numOfFrames, algorithm)
    
        # print("TLB:",tlb)
        # print("Physical Memory Representation", physicalMemory)
        for item in physicalMemory:
            if item[1] == pageNum:
                finalFrameValue = item[0]
        print(address + ", " + str(byteReferenced) + ", " + str(finalFrameValue))
        print(contents.hex())

    print("Number of Translated Addresses = ", len(addressList))
    print("Page Faults =", pageFaultCount)
    print("Page Fault Rate = %3.3f" %(pageFaultCount/len(addressList)))
    print("TLB Hits =", hitCount)
    print("TLB Misses =", missCount)
    print("TLB Hit Rate = %3.3f" %(hitCount/len(addressList)))


def doFIFO(physicalMemory, pageNum):
    invalidPageNum = physicalMemory.pop(0)
    physicalMemory.append((invalidPageNum[0], pageNum))
    pageTable[invalidPageNum[1]] = (invalidPageNum[0], 0)
    for i in range(len(tlb)):
        if tlb[i][0] == invalidPageNum[1]:
            del tlb[i]
            break
    # print("You are in FIFO function.")
    return invalidPageNum[0]

def doLRU(physicalMemory):
    print("You are in LRU function.")

def doOPT(physicalMemory):
    print("You are in OPT function.")


if __name__ == '__main__':
    main()