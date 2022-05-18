from re import M
import sys

from numpy import empty

# When the thing from memory gets swapped out, do you update your TLB by removing the item?

tlb = [] # [(logical memory page num, physical memory frame number), ...]
pageTable = {} # pageNum: [FrameNum, validBit]
physicalMemory = [] # (frameNum, page)

LRUqueue = []
jobList = []

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
    for i in range(int(frameNums)):
        physicalMemory.append(None)
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

def updatePM(pageNum, frameNumber, numOfFrames, algorithm, LRUqueue, jobList):
    for i in range(len(physicalMemory)):
        if physicalMemory[i] is None:
            physicalMemory[i] = (i, pageNum)
            return i
    if len(physicalMemory) == numOfFrames:
        if algorithm == "FIFO":
            frameNumber = doFIFO(physicalMemory, pageNum)
        elif algorithm == "LRU":
            frameNumber = doLRU(physicalMemory, pageNum, LRUqueue)
        elif algorithm == "OPT":
            frameNumber = doOPT(physicalMemory, pageNum, jobList)
    return frameNumber

def driver(addressList, numOfFrames, algorithm):
    frameNumber = 0
    pageFaultCount = 0
    missCount = 0
    hitCount = 0
    curAddressCount = 0
    numOfFrames = int(numOfFrames)
    f = open("BACKING_STORE.bin", "rb")
    for address in addressList:
        curAddressCount += 1
        jobList = addressList[curAddressCount:]
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
                for i in range(len(LRUqueue)): # check if pageNum already in queue
                    if LRUqueue[i][1] == pageNum:
                        val = LRUqueue.pop(i)
                        break
                print("Val: ", val)
                LRUqueue.append((pageTable[val[1]][0], pageNum)) # move pageNum to most recently used (end of queue)
                break
        if hitCountBefore == hitCount: # Not a hit
            if pageTable[pageNum] == None or pageTable[pageNum][1] == 0: # Page Fault
                pageFaultCount += 1
                missCount += 1
                frameNumber = updatePM(pageNum, frameNumber, numOfFrames, algorithm, LRUqueue, jobList)
                updateTLB(pageNum, frameNumber) # moved from before updatePM
                pageTable[pageNum] = (frameNumber, 1) # moved from before frame number update above
            else: # Soft Miss
                missCount += 1
                frameNumber = updatePM(pageNum, frameNumber, numOfFrames, algorithm, LRUqueue, jobList)
                updateTLB(pageNum, frameNumber) # moved from before updatePM
            # print("Page Table: ", pageTable)
            LRUqueue.append((pageTable[pageNum][0], pageNum))
            
    
        print("TLB:",tlb)
        print("Physical Memory Representation", physicalMemory)
        for item in physicalMemory:
            if item is not None:
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
    # if it is a soft miss, the page access needs to go to the end of the pM
    for i in range(len(physicalMemory)):
        if physicalMemory[i][1] == pageNum:
            invalidPageNum = physicalMemory.pop(i)
            physicalMemory.append((invalidPageNum[0], pageNum))
            return invalidPageNum[0]

    invalidPageNum = physicalMemory.pop(0)
    physicalMemory.append((invalidPageNum[0], pageNum))
    pageTable[invalidPageNum[1]] = (invalidPageNum[0], 0)
    for i in range(len(tlb)):
        if tlb[i][0] == invalidPageNum[1]:
            del tlb[i]
            break
    return invalidPageNum[0]

def doLRU(physicalMemory, pageNum, LRUqueue):
    print("LRU queue", LRUqueue)
    invalidPageNum = LRUqueue.pop(0) # head of queue is least recently used pageNum
    print("Invalid page num: ", invalidPageNum)
    # remove LRU from physical memory
    for i in range(len(physicalMemory)):
        if physicalMemory[i][1] == invalidPageNum[1]:
            physicalMemory.pop(i)
            break
    physicalMemory.append((invalidPageNum[0], pageNum))
    pageTable[invalidPageNum[1]] = (invalidPageNum[0], 0)
    for i in range(len(tlb)):
        if tlb[i][0] == invalidPageNum[1]:
            del tlb[i]
            break
    return invalidPageNum[0]

def doOPT(physicalMemory, pageNum, jobList):
    mydict = {}
    for val in physicalMemory:
        if val is not None:
            mydict[val[1]] = 10000000
    for pageVal in mydict:
        for i in range(len(jobList)):
            if pageVal == int(jobList[i]) // 256:
                mydict[pageVal] = i
                break
    # check tie-breaking rule for multiple values that never show up again
    maxVal = None
    
    if len(jobList) == 0:
        # if joblist is empty replace last frame with last job
        maxVal = max(physicalMemory, key = lambda i : i[0])[1]
        print("Max val: ", maxVal)
    
    else:
        for key in mydict:
            if maxVal is None:
                maxVal = key  #  1000000 1000000
            else:
                if mydict[key] > mydict[maxVal]:
                    maxVal = key
    print("Joblist: ", jobList)
    print("Mydict: ", mydict)
    # maxVal contains highest pageNumber
    for i in range(len(physicalMemory)):
        if physicalMemory[i][1] == maxVal:
            invalidPageNum = physicalMemory.pop(i)
            break
    # frameNum = pageTable[pageNum][0]
    physicalMemory.append((invalidPageNum[0], pageNum))
    pageTable[invalidPageNum[1]] = (invalidPageNum[0], 0)
    for i in range(len(tlb)):
        if tlb[i][0] == invalidPageNum[1]:
            del tlb[i]
            break
    
    return invalidPageNum[0]
        
    


if __name__ == '__main__':
    main()