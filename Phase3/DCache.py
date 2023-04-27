import math
import numpy as np
import random
import json

# data_mem = np.zeros((2**32), dtype='uint8') # main memory
data_mem = {} # main memory

class DCache:
    __policies = ["LRU", "FIFO", "random", "LFU"]
    __mapping = ["direct", "set-associative", "fully-associative"]

    JSONArr = []
    VictimBlocks = []
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
        self.writeHitOrMiss = None # 0 for miss, 1 for hit

        # set number_of_ways
        self.setNumberOfWays(numberOfWays, mapping, cacheSize, blockSize)

        # set replacement policy
        self.setReplacementPolicy(policyName)

        # LRU policy
        # number of ways x 3, 3 is for the Valid bit, status bit and tag bit
        # self.LRU = np.zeros((self.number_of_ways), dtype='uint32')
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
        #self.tag_arrays = np.full((self.number_of_ways), {}, dtype=object)
        self.tag_arrays = [{} for i in range(self.number_of_ways)]
        # number of data arrays = number of ways. each array has <number of blocks> rows and <block size> columns
        self.data_cache = np.full((self.number_of_ways, cacheSize//blockSize, blockSize), 0, dtype='uint8')

    def setNumberOfWays(self, numberOfWays:int, mapping:str, cacheSize:int, blockSize:int):
        if(mapping not in self.__mapping):
            raise Exception("Invalid Mapping")
        
        if(mapping == "direct"):
            self.number_of_ways = 1
        elif mapping == "set-associative":
            self.number_of_ways = numberOfWays
        elif mapping == "fully-associative":
            self.number_of_ways = numberOfWays # total Blocks
        
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
        if self.tag_arrays[wayNumber].get(Index, -1) == Tag: # found in cache
            # using block offset to get data from block
            # self.VictimBlocks.append({"wayNum":0, "Index":0})
            return self.data_cache[wayNumber][Index][blockOffset]
        
        else: # handle miss, by getting data from main memory
            
            # add the victim block 
            self.VictimBlocks.append({"wayNum":wayNumber, "Index":Index})

            # check if there was something in the cache at that index
            if(self.tag_arrays[wayNumber].get(Index, -1)!=-1): # if there was something, then add that tag to MCT and then evict it
                self.mct[self.tag_arrays[wayNumber][Index]] = True
            
            # update tag array
            self.tag_arrays[wayNumber][Index] = Tag

            
            # set data in cache  
            # converting dataReceived to a 256 bit binary string
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
                
                self.data_cache[wayNumber][tempIndex][tempBO] = int(binaryDataFromMain[i*8:i*8+8],2)
                tempAddress += 1
            
            return self.data_cache[wayNumber][Index][blockOffset]

    def WriteDataInMain(self, address:int, data:int):
        '''
        This function is used to set data in the main memory
        Considering data to be of 32 bits/4 Bytes or max value of int to be 2^31 - 1
        '''

        data_mem[int(address)] = data
          
    def getFromMain(self, address:int):
        '''
        This function is used to get data from the main memory

        address: the address of the data

        returns: binary string of data of size `blocksize` from main memory
        '''
        # return data from main memory, considering main memory to be a dictionary
        # we have to take blocksize amount of bytes from main memory

        dataBytes = ""

        for i in range(self.block_size):
            AddressInDataDict = address - (address%4) # address of the first byte of the block

            dataFromMem = data_mem.get(AddressInDataDict,0) # get 4byte int from the dictionary or else get 0 of 32 bits
            dataInBinary = bin(dataFromMem)[2:].zfill(32) # converting data to a 32 bit binary string
            dataBytes += dataInBinary[8*(address%4):8*(address%4)+8]
            
            address += 1 # update address, go to next byte

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
        self.data_cache[wayNumber][Index][blockOffset] = data

    def write_data(self, address:int, data:int, func3:int):
        '''
        This function is used to write data in the cache
        first the data is written in the cache then subsequently in the main memory at that particular address

        Using Write through policy

        address: the address of the data
        data: the data to be written - 1/2/4 bytes
        func3: depending on type of store data
            if func3 == 0b000 / 0 -> sb
            if func3 == 0b001 / 1 -> sh
            if func3 == 0b010 / 2 -> sw
        '''

        # check for possible errors
        if(func3 not in [0,1,2]):
            raise Exception("Invalid func3, expected 0, 1 or 2 but got "+str(func3))

        if(data<0 or data>2**31-1):
            raise Exception(f"Invalid data, expected data to be in range 0-{2**31 -1} but got "+str(data))

        if(self.mapping not in self.__mapping):
            raise Exception("Invalid Mapping, expected direct, set-associative or fully-associative but got "+self.mapping)

        Tag, Index, blockOffset = self.break_address(address)

        JSONDict = {"Tag":Tag, "Index":Index, "blockOffset":blockOffset}
        self.JSONArr.append(JSONDict)

        self.VictimBlocks.append({"wayNum":0, "Index":0})

        # dataInBinary = bin(data)[2:].zfill(32) # converting data to a 32 bit binary string
        if(self.mapping=="direct"):
            #  match the tag with the tag array
            if(self.tag_arrays[0].get(Index, -1) == Tag): # found in cache
                if(func3==0):
                    dataInBinary = bin(data)[2:].zfill(8) # converting data to a 8 bit binary string
                elif(func3==1):
                    dataInBinary = bin(data)[2:].zfill(16)
                elif(func3==2):
                    dataInBinary = bin(data)[2:].zfill(32)

                for i in range(2**func3): # writing data in the cache either a byte, half word or a word
                    self.writeByte(address, int(dataInBinary[i*8:i*8+8], 2), 0)
                    address += 1
            
        elif(self.mapping=="set-associative"):
            for i in range(len(self.tag_arrays)):
                if(self.tag_arrays[0].get(Index,-1)==Tag):
                    if(func3==0):
                        dataInBinary = bin(data)[2:].zfill(8) # converting data to a 8 bit binary string
                    elif(func3==1):
                        dataInBinary = bin(data)[2:].zfill(16)
                    elif(func3==2):
                        dataInBinary = bin(data)[2:].zfill(32)

                    for j in range(2**func3):
                        self.writeByte(address, int(dataInBinary[j*8:j*8+8], 2), i)
                        address += 1
                    break
            
        elif(self.mapping=="fully-associative"):
            for i in range(len(self.tag_arrays)):
                if(self.tag_arrays[0].get(Index,-1)==Tag):
                    if(func3==0):
                        dataInBinary = bin(data)[2:].zfill(8) # converting data to a 8 bit binary string
                    elif(func3==1):
                        dataInBinary = bin(data)[2:].zfill(16)
                    elif(func3==2):
                        dataInBinary = bin(data)[2:].zfill(32)

                    for j in range(2**func3):
                        self.writeByte(address, int(dataInBinary[j*8:j*8+8], 2), i)
                        address += 1
                    break
            

        # writing the data to main memory after this
        self.WriteDataInMain(address, data)
        self.writeHitOrMiss = 1 # cache miss
    
    def get_data(self,address:int, func3:int):

        print("ADDRESS: ", address)

        '''
        This function is used to get data from the cache
        if the data is not in the cache then it will get it from the main memory

        address: the address of the data
        func3: depending on type of load data
            if func3 == 0b000 / 0 -> lb
            if func3 == 0b001 / 1 -> lh
            if func3 == 0b010 / 2 -> lw
        '''
        
        # the content of all the sets of the cache
        cacheContent = {}
        for i in range(self.number_of_ways):
            for j in range(len(self.tag_arrays[i])):
                if(self.tag_arrays[i].get(j, -1)!=-1):
                    cacheContent["wayNum"] = i
                    cacheContent["Index"]=j
                    cacheContent["Blocks"] = self.data_cache[i][j].tolist()
        
        self.__CacheContent.append(cacheContent)

        Tag, Index, blockOffset = self.break_address(address)
        JSONDict = {"Tag":Tag, "Index":Index, "blockOffset":blockOffset}
        self.JSONArr.append(JSONDict)

        # requested data in binary
        DataFound = ""

        # storing all the cache accesses in a dictionary using its address as key
        self.cache_access[address] = True

        if self.mapping == "direct":

            # check type of miss
            if(self.tag_arrays[0].get(Index, -1)==-1): # cold miss
                self.cold_misses += 1
                
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
                self.hits += 1 
                self.readHitOrMiss=1 # cache hit

            # check type of load instruction
            if(func3==0): # lb
                return self.readByte(address, 0)
            
            elif(func3==1): # lh
                for i in range(2):
                    DataFound += bin(self.readByte(address, 0))[2:].zfill(8) # convert to binary and pad with zeros
                    address+=1 # increment address by 1 to get new address
                return int(DataFound,2)
            
            elif(func3==2): # lw
                for i in range(4):
                    DataFound += bin(self.readByte(address, 0))[2:].zfill(8) # convert to binary and pad with zeros
                    address += 1 # increment address by 1 to get new address
                print("DataFound: ", DataFound)
                return int(DataFound,2)
            
        elif self.mapping == "set-associative" or self.mapping=="fully-associative":
            
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
            if(func3==0): # lb
                return self.readByte(address, wayNum)
            
            elif(func3==1): # lh
                for _ in range(2):
                    DataFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                    address+=1 # increment address by 1 to get new address
                return int(DataFound,2)
            
            elif(func3==2): # lw
                for _ in range(4):
                    DataFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                    address += 1 # increment address by 1 to get new address
                return int(DataFound,2)
            else:
                raise ValueError("Invalid func3 value, expected 0, 1 or 2 but got "+str(func3)+" instead")

        
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
            if(func3==0): # lb
                return self.readByte(address, wayNum)
            
            elif(func3==1): # lh
                for _ in range(2):
                    DataFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                    address+=1 # increment address by 1 to get new address
                return int(DataFound,2)
            
            elif(func3==2): # lw
                for _ in range(4):
                    DataFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                    address += 1 # increment address by 1 to get new address
                return int(DataFound,2)
            else:
                raise ValueError("Invalid func3 value, expected 0, 1 or 2 but got "+str(func3)+" instead")

    def break_address(self, address:int):
        # considering 32 bit address
        address = bin(address)[2:].zfill(32) # converting to binary and padding with zeros to make it 32 bits
        numberOfBlocks = self.cache_size / self.block_size
        numberOfSets = numberOfBlocks / self.number_of_ways
        
        # Calculating the number of bits for tag, index and block offset
        IndexBitsNum = int(math.log(numberOfSets, 2))
        blockOffsetBitsNum = int(math.log(self.block_size, 2))
        TagBitsNum = int(32 - IndexBitsNum - blockOffsetBitsNum) # remaining bits are tag bits

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
        # print("Total hits: ", self.hits)
        # print("Total cold misses: ", self.cold_misses)
        # print("Total capacity misses: ", self.capacity_misses)
        # print("Total conflict misses: ", self.conflict_misses)
        # print("Total misses: ", self.cold_misses + self.capacity_misses + self.conflict_misses)
        # print("Hit rate: ", self.hits/(self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses))
        # print("Miss rate: ", (self.cold_misses + self.capacity_misses + self.conflict_misses)/(self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses))
        # print("Number of Access: ", self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses)
        # saving all this stats in a json file
        file = open("./stats/stats.json", "w")
        hit_rateVar = (self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses)
        if(hit_rateVar==0):
            hit_rateVar = 1
        missRateVar = (self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses)
        if(missRateVar==0):
            missRateVar = 1
        
        StatDict = {
            "total_hits": self.hits,
            "total_misses": self.cold_misses + self.capacity_misses + self.conflict_misses,
            "total_cold_misses": self.cold_misses,
            "total_capacity_misses": self.capacity_misses,
            "total_conflict_misses": self.conflict_misses,
            "hit_rate": self.hits/hit_rateVar,
            "miss_rate": (self.cold_misses + self.capacity_misses + self.conflict_misses)/missRateVar,
            "number_of_access": self.hits + self.cold_misses + self.capacity_misses + self.conflict_misses
        }
        # saving the stats in a json file
        json.dump(StatDict, file, indent=4)
        file.close()

        # Stores Split of Tag Index and Block Offset
        file = open("./stats/JSONArr.json", "w")
        json.dump(self.JSONArr, file, indent=4)
        file.close()

        # stores the victim blocks
        file = open("./stats/VictimBlocks.json", "w")
        json.dump(self.VictimBlocks, file, indent=4)
        file.close()
        
        # stores the sets accessed
        file = open("./stats/SetsAccessed.json", "w")
        json.dump(self.__SetAccessed, file, indent=4)
        file.close()

        # stores the cache content
        file = open("./stats/CacheContent.json", "w")
        json.dump(self.__CacheContent, file, indent=4)
        file.close()

    def getCacheHitOrMiss(self):
        '''
        if cache hit, return 1
        if cache miss, return 0
        else return None
        '''
        return self.readHitOrMiss
    
    def getWriteHitOrMiss(self):
        '''
        if cache hit, return 1
        if cache miss, return 0
        else return None
        '''

        return self.writeHitOrMiss

# if __name__ =='__main__':
#     L1 = DCache(32, 256, "set-associative", "LFU", 4)
#     L1.write_data(0, 345, 1)

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
#     L1.printStats()













