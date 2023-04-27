import math
import numpy as np
import random
import json

# MEM = np.zeros((2**32), dtype='uint8') # main memory
# MEM = {3456:567899, 4566: 456764, 545:563657} # main memory
# MEM = [0]*4000
MEM = np.zeros((2**12), dtype='uint8') # instruction memory 12 bit address

class ICache:
    __policies = ["LRU", "FIFO", "random", "LFU"]
    __mapping = ["direct", "set-associative", "fully-associative"]

    __JSONArr = []
    __VictimBlocks = []
    __SetAccessed = []
    __CacheContent = []

    def __init__(self, blockSize:int, cacheSize:int, mapping:str, policyName:str, numberOfWays:int) -> None:
        self.cache = {}
        self.cache_size = cacheSize
        self.block_size = blockSize
        self.mapping = mapping
        self.replacement_policy = policyName
        self.cache_miss_penalty = 0
        self.cache_hit_time = 0
        self.hits = 0

        self.misses = 0
        self.cold_misses = 0
        self.capacity_misses = 0
        self.conflict_misses = 0

        self.readHitOrMiss = None # 0 for miss, 1 for hit

        # set number_of_ways
        self.setNumberOfWays(numberOfWays, mapping, cacheSize, blockSize)

        # set replacement policy
        self.setReplacementPolicy(policyName)

        # LRU policy
        # number of ways x 3, 3 is for the Valid bit, status bit and tag bit
        self.LRU = [0]*self.number_of_ways

        # FIFO policy
        # self.FIFO = np.zeros((self.number_of_ways), dtype='uint32')
        self.FIFO = [0]*self.number_of_ways

        # LFU policy
        self.LFU = {}

        # Random policy
        # self.Random = np.zeros((self.number_of_ways), dtype='uint32')

        self.cache_access = {} # dictionary to store all the cache accesses
        self.mct = {} # miss classification table

        # total tag arrays -> number of ways and each array is a dictionary 
        self.tag_arrays = [{} for i in range(self.number_of_ways)]
        # number of data arrays = number of ways. each array has <number of blocks> rows and <block size> columns
        self.instruction_cache = np.full((self.number_of_ways, cacheSize//blockSize, blockSize), 0, dtype='uint8')

    def setNumberOfWays(self, numberOfWays:int, mapping:str, cacheSize:int, blockSize:int):
        if(mapping not in self.__mapping):
            raise Exception("Invalid Mapping")
        
        if(mapping == "direct"):
            self.number_of_ways = 1
        elif mapping == "set-associative":
            self.number_of_ways = numberOfWays
        elif mapping == "fully-associative":
            self.number_of_ways = cacheSize//blockSize # total Blocks
        
    def setReplacementPolicy(self, policyName:str):
        if(policyName not in self.__policies):
            raise Exception("Invalid Replacement Policy")
        
        self.replacement_policy = policyName
    
    def readByte(self, address:int, wayNumber:int):
        '''
        This function is used to read a byte from the cache
        if the byte is not in the cache then it will get it from the main memory

        address: the address of the byte
        '''
        Tag, Index, blockOffset = self.break_address(address)
        # TotalSets = self.cache_size//(self.block_size*self.number_of_ways)
        

        if self.tag_arrays[wayNumber].get(Index, -1) == Tag: # found in cache
            # using block offset to get data from block
            self.__VictimBlocks.append({"wayNum":0, "Index":0})
            return self.instruction_cache[wayNumber][Index][blockOffset]
            
        
        else: # handle miss, by getting data from main memory

            # add the victim block 
            self.__VictimBlocks.append({"wayNum":wayNumber, "Index":Index})

            # check if there was something in the cache at that index
            if(self.tag_arrays[wayNumber].get(Index, -1)!=-1): # if there was something, then add that tag to MCT and then evict it
                self.mct[self.tag_arrays[wayNumber][Index]] = True
            
            # update tag array
            self.tag_arrays[wayNumber][Index] = Tag

            tempAddress = address

            # how many bits to make 0 -> log2(block_size)
            bitsToMakeZero = int(math.log2(self.block_size))
            tempAddress = bin(tempAddress)[2:].zfill(32)
            tempAddress = tempAddress[:-bitsToMakeZero] + '0'*bitsToMakeZero
            tempAddress = int(tempAddress, 2)

            # get data from main memory
            binaryDataFromMain = self.getFromMain(tempAddress)

            for i in range(self.block_size):
                _, tempIndex, tempBO = self.break_address(tempAddress)
                
                self.instruction_cache[wayNumber][tempIndex][tempBO] = int(binaryDataFromMain[i*8:i*8+8],2)
                tempAddress += 1
            
            return self.instruction_cache[wayNumber][Index][blockOffset]


            # # get data from instruction memory - considering 4 bytes of data
            # binaryInstructionsFromMain = self.getFromMain(address)
            
            # # set data in cache  
            # # converting dataReceived to a 256 bit binary string
            # for i in range(self.block_size):
            #     self.instruction_cache[wayNumber][Index][i] = int(binaryInstructionsFromMain[i*8:i*8+8],2)
            
            # print("Data in cache block: ", self.instruction_cache[wayNumber][Index])
            
            # return self.instruction_cache[wayNumber][Index][blockOffset]

    def WriteDataInMain(self, address:int, data:int):
        '''
        This function is used to set data in the main memory
        Considering data to be of 32 bits/4 Bytes or max value of int to be 2^31 - 1
        '''

        MEM[address] = data
        
    def getFromMain(self, address:int):
        '''
        This function is used to get data from the main memory

        address: the address of the data

        returns: binary string of data of size `blocksize` from main memory
        '''
        # return data from main memory, considering main memory to be a dictionary
        # we have to take blocksize amount of bytes from main memory

        # My instruction memory is MEM

        dataBytes = ""
        for i in range(self.block_size):
            dataBytes += bin(MEM[address+i])[2:].zfill(8)                

        return dataBytes     
    
    def writeByte(self, address:int, data:int, wayNumber:int):
        '''
        This function is used to write a byte in the cache
        the byte is written in the cache

        address: the address of the byte
        data: the byte to be written - 1 byte - expected data to be in range 0-255
        '''

        if(data<0 or data>255):
            raise Exception("Invalid data, expected data to be in range 0-255 but got "+str(data))
        
        _, Index, blockOffset = self.break_address(address)
        

        # set this data on this address
        self.instruction_cache[wayNumber][Index][blockOffset] = data

    def get_data(self,address:int, func3:int):

        '''
        This function is used to get data from the cache
        if the data is not in the cache then it will get it from the main memory

        address: the address of the data
        func3: always 2
        '''

        func3 = 2

        # the content of all the sets of the cache
        cacheContent = {}
        for i in range(self.number_of_ways):
            for j in range(len(self.tag_arrays[i])):
                if(self.tag_arrays[i].get(j, -1)!=-1):
                    cacheContent["wayNum"] = i
                    cacheContent["Index"]=j
                    cacheContent["Blocks"] = self.instruction_cache[i][j].tolist()
        
        self.__CacheContent.append(cacheContent)

        Tag, Index, blockOffset = self.break_address(address)
        print("Tag: ", Tag, "Index: ", Index, "blockOffset: ", blockOffset)

        JSONDict = {"Tag":Tag, "Index":Index, "blockOffset":blockOffset}
        self.__JSONArr.append(JSONDict)

        # requested data in binary
        DataFound = ""

        # storing all the cache accesses in a dictionary using its address as key
        self.cache_access[address] = True

        if self.mapping == "direct":

            # check type of miss
            if(self.tag_arrays[0].get(Index, -1)==-1): # cold miss
                self.cold_misses += 1
                print("HERE COLD MISS ")
                self.readHitOrMiss = 0 # cache miss
            elif(self.tag_arrays[0].get(Index, -1)!=Tag): # if tag != -1 and tag != Tag -> conflict miss or capacity miss
                # so we look into the MCT to find out if it's a conflict or capacity miss
                
                self.readHitOrMiss = 0 # cache miss
                
                if(Tag in self.mct): # if tag is there in MCT, so it was once in the cache -> conflict miss
                    self.conflict_misses += 1
                else: # capacity miss
                    self.capacity_misses += 1
            else:
                # else the data is present in the cache -> hit
                print("HERE HIT")
                self.hits += 1 
                self.readHitOrMiss=1 # cache hit

            # lw
            print("VALUE OF FUNC3: ", func3)

            # get 4 bytes from cache

            for i in range(4):
                DataFound += bin(self.readByte(address, 0))[2:].zfill(8) # convert to binary and pad with zeros
                address += 1 # increment address by 1 to get new address
            return int(DataFound,2)
            
        elif self.mapping == "set-associative":
            
            # check for possible errors
            if(self.number_of_ways%2!=0 and self.number_of_ways==0):
                raise Exception("Invalid number of ways, expected number of ways to be even but got "+str(self.number_of_ways))
            
            # set that is accessed is same as the index
            self.__SetAccessed.append({"set":Index})

            # check type of miss
            ColdMiss = True
            CapacityORConflict = False
            wayNum = None

            # look into all the ways to find the data
            for i in range(len(self.tag_arrays)):
                if(self.tag_arrays[i].get(Index, -1)==Tag): # hit
                    ColdMiss = False
                    CapacityORConflict = False
                    wayNum = i # way number where data is found
                    self.hits =+ 1 # increment hits
                    break
                if(self.tag_arrays[i].get(Index, -1)==-1): # cold miss
                    ColdMiss = True # not a cold miss
                    CapacityORConflict = False # not a capacity miss
                    wayNum = i # way number where data is to be stored
                    break
                else: # either capacity miss or conflict miss
                    CapacityORConflict = True
                    ColdMiss = False
            

            # ---------------------------------------------------------------
            if(ColdMiss): # if cold miss
                self.cold_misses += 1
                self.readHitOrMiss=0 # cache miss
            elif(CapacityORConflict): # either conflict miss or capacity miss

                self.readHitOrMiss=0 # cache miss

                # check if replacement policy is valid
                if(self.replacement_policy not in self.__policies):
                    raise ValueError("Invalid replacement policy")
                
                # evict according to given policy
                if(self.replacement_policy=="LRU"):
                    LRUWay = self.LRU.pop(-1) # get the least recently used way
                    wayNum = LRUWay # way number where data is to be replaced from and return the updated data
                    self.LRU.insert(0,LRUWay) # insert it at the start to make it the most recently used
                elif(self.replacement_policy=='FIFO'):
                    FIFOWay = self.FIFO.pop(0) # get the first entry in the queue
                    wayNum = FIFOWay
                    self.FIFO.append(FIFOWay) # append it to the end of the queue
                elif(self.replacement_policy=='random'):
                    # apply the easiet policy here
                    # simply choose a random number between 0 to number_of_ways - 1
                    wayNum = random.randint(0, self.number_of_ways-1)
                    
                elif(self.replacement_policy=='LFU'):
                    # apply the LFU policy here
                    MIN = min(self.LFU, key=self.LFU.get) # get the key with the maximum value
                    wayNum = MIN # way number where data is to be replaced from and return the updated data
                    self.LFU[MIN] += 1 # increment the value of the key
                
                if(Tag in self.mct):
                    self.conflict_misses += 1
                else:
                    self.capacity_misses += 1
            else: # hit
                self.hits += 1
                self.readHitOrMiss = 1 # cache hit

                if(self.replacement_policy=="LRU"):
                    self.LRU.append(wayNum) # append it to the end of the List
                elif(self.replacement_policy=='FIFO'):
                    self.FIFO.append(wayNum) # append it to the end of the queue
                elif(self.replacement_policy=='random'):
                    pass
                elif(self.replacement_policy=='LFU'):
                    if(wayNum in self.LFU):
                        self.LFU[wayNum] += 1
                    else:
                        self.LFU[wayNum] = 1
            
            # ---------------------------------------------------------------
            # once you know the wayNumber, now go to that way and get data from there
            # check type of load instruction
            
            # lw
            for _ in range(4):
                DataFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                address += 1 # increment address by 1 to get new address
            return int(DataFound,2)
        
        
        elif self.mapping == "fully-associative":
            # check type of miss
            ColdMiss = True
            CapacityORConflict = False
            wayNum = None

            # look into all the ways to find the data
            for i in range(len(self.tag_arrays)):
                if(self.tag_arrays[i].get(Index, -1)==Tag): # hit
                    ColdMiss = False
                    CapacityORConflict = False
                    wayNum = i # way number where data is found
                    self.hits =+ 1 # increment hits
                    break
                if(self.tag_arrays[i].get(Index, -1)==-1): # cold miss
                    ColdMiss = True # not a cold miss
                    CapacityORConflict = False # not a capacity miss
                    wayNum = i # way number where data is to be stored
                    break
                else: # either capacity miss or conflict miss
                    CapacityORConflict = True

            # ---------------------------------------------------------------
            if(ColdMiss): # if cold miss
                self.cold_misses += 1
            elif(CapacityORConflict): # either conflict miss or capacity miss
                
                # check if replacement policy is valid
                if(self.replacement_policy not in self.__policies):
                    raise ValueError("Invalid replacement policy")
                
                # evict according to given policy
                if(self.replacement_policy=="LRU"):
                    LRUWay = self.LRU.pop(-1) # get the least recently used way
                    wayNum = LRUWay # way number where data is to be replaced from and return the updated data
                    self.LRU.insert(0,LRUWay) # insert it at the start to make it the most recently used
                elif(self.replacement_policy=='FIFO'):
                    FIFOWay = self.FIFO.pop(0) # get the first entry in the queue
                    wayNum = FIFOWay
                    self.FIFO.append(FIFOWay) # append it to the end of the queue
                elif(self.replacement_policy=='random'):
                    # apply the easiet policy here
                    # simply choose a random number between 0 to number_of_ways - 1
                    wayNum = random.randint(0, self.number_of_ways-1)
                    
                elif(self.replacement_policy=='LFU'):
                    # apply the LFU policy here
                    MIN = min(self.LFU, key=self.LFU.get) # get the key with the maximum value
                    wayNum = MIN # way number where data is to be replaced from and return the updated data
                    self.LFU[MIN] += 1 # increment the value of the key
                
                if(Tag in self.mct):
                    self.conflict_misses += 1
                else:
                    self.capacity_misses += 1
            else: # hit
                self.hits += 1
                self.readHitOrMiss = 1 # cache hit

                if(self.replacement_policy=="LRU"):
                    self.LRU.append(wayNum) # append it to the end of the List
                elif(self.replacement_policy=='FIFO'):
                    self.FIFO.append(wayNum) # append it to the end of the queue
                elif(self.replacement_policy=='random'):
                    pass
                elif(self.replacement_policy=='LFU'):
                    if(wayNum in self.LFU):
                        self.LFU[wayNum] += 1
                    else:
                        self.LFU[wayNum] = 1
            # ---------------------------------------------------------------
            # once you know the wayNumber, now go to that way and get data from there
            # check type of load instruction
            
            # lw
            for _ in range(4):
                DataFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                address += 1 # increment address by 1 to get new address
            return int(DataFound,2)
        
    def break_address(self, address:int):
        # considering 12 bit address
        address = bin(address)[2:].zfill(12) # converting to binary and padding with zeros to make it 32 bits
        numberOfBlocks = self.cache_size / self.block_size
        numberOfSets = numberOfBlocks / self.number_of_ways
        
        # Calculating the number of bits for tag, index and block offset
        IndexBitsNum = int(math.log(numberOfSets, 2))
        blockOffsetBitsNum = int(math.log(self.block_size, 2))
        TagBitsNum = int(12 - IndexBitsNum - blockOffsetBitsNum) # remaining bits are tag bits

        # Calculating the tag, index and block offset
        if(address[0:TagBitsNum]==""):
            Tag = 0
        else:
            Tag = int(address[0:TagBitsNum],2)
        
        if(address[TagBitsNum:IndexBitsNum + TagBitsNum]==""):
            Index = 0
        else:
            Index = int(address[TagBitsNum:IndexBitsNum + TagBitsNum],2)
        
        if(address[TagBitsNum+IndexBitsNum:TagBitsNum+IndexBitsNum+blockOffsetBitsNum]==""):
            blockOffset = 0  
        else:
            blockOffset = int(address[TagBitsNum+IndexBitsNum:TagBitsNum+IndexBitsNum+blockOffsetBitsNum],2)

        return Tag, Index, blockOffset

    def showAccessTable(self):
        print("Access Table: ", self.cache_access)

    def printStats(self):
        print("Total hits: ", self.hits)
        print("Total cold misses: ", self.cold_misses)
        print("Total capacity misses: ", self.capacity_misses)
        print("Total conflict misses: ", self.conflict_misses)
        print("Total misses: ", self.cold_misses + self.capacity_misses + self.conflict_misses)
        print("Hit rate: ", self.hits/(self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses))
        print("Miss rate: ", (self.cold_misses + self.capacity_misses + self.conflict_misses)/(self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses))
        print("Number of Access: ", self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses)
        # saving all this stats in a json file
        file = open("./Istats/stats.json", "w")
        StatDict = {
            "total_hits": self.hits,
            "total_misses": self.cold_misses + self.capacity_misses + self.conflict_misses,
            "total_cold_misses": self.cold_misses,
            "total_capacity_misses": self.capacity_misses,
            "total_conflict_misses": self.conflict_misses,
            "hit_rate": self.hits/(self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses),
            "miss_rate": (self.cold_misses + self.capacity_misses + self.conflict_misses)/(self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses),
            "number_of_access": self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses
        }
        json.dump(StatDict, file, indent=4)
        file.close()

        # Stores Split of Tag Index and Block Offset
        file = open("./Istats/JSONArr.json", "w")
        json.dump(self.__JSONArr, file, indent=4)
        file.close()

        # stores the victim blocks
        file = open("./Istats/VictimBlocks.json", "w")
        json.dump(self.__VictimBlocks, file, indent=4)
        file.close()
        
        # stores the sets accessed
        file = open("./Istats/SetsAccessed.json", "w")
        json.dump(self.__SetAccessed, file, indent=4)
        file.close()

        # stores the cache content
        file = open("./Istats/CacheContent.json", "w")
        json.dump(self.__CacheContent, file, indent=4)
        file.close()

    def getCacheHitOrMiss(self):
        '''
        if cache hit, return 1
        if cache miss, return 0
        else return None
        '''
        return self.readHitOrMiss

    def load_program_memory(self,file, MEM):
        """
            Load program Memory
        """
        f = open(file, "r")

        for line in f.readlines():
            address, instruction = line.split()

            address = int(address, 16)
            instruction = int(instruction, 16)

            self.write_word(address, instruction, MEM)

        f.close()

    def write_word(self,address:int, instruction:int, MEM:list):
        """
            Write Word
        """
        
        index = address // 4
        MEM[int(index)] = instruction



# if __name__ =='__main__':
    
#     file = "Phase 2/TestFiles/output.mem"
#     L1 = ICache(32, 256, "direct", "LFU", 0)

#     L1.load_program_memory(file, MEM)


#     data = L1.get_data(0, 2)
#     print(data)
#     data = L1.get_data(0, 2)
#     print(data)
#     data = L1.get_data(0, 2)
#     print(data)
#     data = L1.get_data(0, 2)
#     print(data)
#     data = L1.get_data(0, 2)
#     print(data)
#     data = L1.get_data(0, 2)
#     print(data)
#     data = L1.get_data(56, 2)
#     print(data)
#     data = L1.get_data(567, 0)
#     print(data)
#     print()
#     L1.printStats()













