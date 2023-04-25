   
import math
import numpy as np

class DCache:
    __policies = ["LRU", "FIFO", "Random", "LFU"]
    __mapping = ["direct", "set-associative", "fully-associative"]

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


        # LRU policy
        # number of ways x 3, 3 is for the Valid bit, status bit and tag bit
        self.LRU = np.zeros((numberOfWays), dtype='uint32')

        # FIFO policy
        self.FIFO = np.zeros((numberOfWays), dtype='uint32')

        # LFU policy
        self.LFU = np.zeros((numberOfWays,2), dtype='uint32')

        # Random policy
        self.Random = np.zeros((numberOfWays), dtype='uint32')

        self.cache_access = {} # dictionary to store all the cache accesses
        self.mct = {} # miss classification table

        # set number_of_ways
        self.setNumberOfWays(numberOfWays, mapping, cacheSize, blockSize)

        # set replacement policy
        self.setReplacementPolicy(policyName)

        # total tag arrays -> number of ways and each array is a dictionary 
        self.tag_arrays = np.full((numberOfWays), {}, dtype=object)

        # number of data arrays = number of ways. each array has <number of blocks> rows and <block size> columns
        self.data_cache = np.full((numberOfWays, cacheSize//blockSize, blockSize), 0, dtype='uint8')

    def setNumberOfWays(self, numberOfWays:int, mapping:str, cacheSize:int, blockSize:int):
        if(mapping not in self.__mapping):
            raise Exception("Invalid Mapping")
        
        if(mapping == "direct"):
            self.number_of_ways = 1
        elif mapping == "set-associative":
            self.number_of_ways = numberOfWays
        elif mapping == "fully-associative":
            self.number_of_ways = cacheSize/blockSize # total Blocks
        
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
            return self.data_cache[wayNumber][Index][blockOffset]
        
        else: # handle miss, by getting data from main memory

            # check if there was something in the cache at that index
            if(self.tag_arrays[wayNumber].get(Index, -1)!=-1): # if there was something, then add that tag to MCT and then evict it
                self.mct[self.tag_arrays[wayNumber][Index]] = True
            
            # update tag array
            self.tag_arrays[wayNumber][Index] = Tag

            # get data from main memory
            dataFromMain = self.getFromMain(address)
            
            # set data in cache  
            # converting dataReceived to a 256 bit binary string
            dataInBinary = bin(dataFromMain)[2:].zfill(256) # data of form '100010001...' -> 256 bits
            
            # now storing each byte in the cache
            for i in range(32):
                self.data_cache[wayNumber][Index][i] = int(dataInBinary[i*8:i*8+8],2)

            return self.data_cache[wayNumber][Index][blockOffset]

    def getFromMain(self, address:int):
        '''
        This function is used to get data from the main memory
        '''
        # return data from main memory, considering main memory to be a dictionary
        return data_mem.get(address, 0)
        
    def data(self, address:int, func3:int):
        '''
        This function is used to set data from the cache
        It will set it to the main memory 

        address: the address of the data
        func3: depending on type of store data
            if func3 == 0b000 -> sb
            if func3 == 0b001 -> sh
            if func3 == 0b010 -> sw
        '''
        # add data here
    
    def LRU():
        pass
    
    def get_data(self,address:int, func3:int):

        '''
        This function is used to get data from the cache
        if the data is not in the cache then it will get it from the main memory

        address: the address of the data
        func3: depending on type of load data
            if func3 == 0b000 / 0 -> lb
            if func3 == 0b001 / 1 -> lh
            if func3 == 0b010 / 2 -> lw
        '''

        Tag, Index, blockOffset = self.break_address(address)
        
        # requested data in binary
        DataFound = ""

        # storing all the cache accesses in a dictionary using its address as key
        self.cache_access[address] = True

        if self.mapping == "direct":

            # check type of miss
            if(self.tag_arrays[0].get(Index, -1)==-1): # cold miss
                self.cold_misses += 1
            elif(self.tag_arrays[0].get(Index, -1)!=Tag): # if tag != -1 and tag != Tag -> conflict miss or capacity miss
                # so we look into the MCT to find out if it's a conflict or capacity miss
                if(Tag in self.mct): # if tag is there in MCT, so it was once in the cache -> conflict miss
                    self.conflict_misses += 1
                else: # capacity miss
                    self.capacity_misses += 1
            
            # else the data is present in the cache -> hit
            self.hits += 1
            # check type of load instruction
            if(func3==0): # lb
                return self.readByte(address, 0)
            
            elif(func3==1): # lh
                for i in range(2):
                    DataFound.append(bin(self.readByte(address, 0))[2:].zfill(8)) # convert to binary and pad with zeros
                    address+=1 # increment address by 1 to get new address
                return int(DataFound,2)
            
            elif(func3==2): # lw
                for i in range(4):
                    DataFound.append(bin(self.readByte(address, 0))[2:].zfill(8)) # convert to binary and pad with zeros
                    address += 1 # increment address by 1 to get new address
                return int(DataFound,2)
            
        elif self.mapping == "set-associative":

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
                    pass
                    FIFOWay = self.FIFO.pop(0) # get the first entry in the queue
                    wayNum = FIFOWay
                    self.FIFO.append(FIFOWay) # append it to the end of the queue
                elif(self.replacement_policy=='random'):
                    pass
                    # apply the easiet policy here
                elif(self.replacement_policy=='LFU'):
                    pass


                if(Tag in self.mct):
                    self.conflict_misses += 1
                else:
                    self.capacity_misses += 1
            # ---------------------------------------------------------------
            # once you know the wayNumber, now go to that way and get data from there
            # check type of load instruction
            if(func3==0): # lb
                return self.readByte(address, wayNum)
            
            elif(func3==1): # lh
                for _ in range(2):
                    DataFound.append(bin(self.readByte(address, wayNum))[2:].zfill(8)) # convert to binary and pad with zeros
                    address+=1 # increment address by 1 to get new address
                return int(DataFound,2)
            
            elif(func3==2): # lw
                for _ in range(4):
                    DataFound.append(bin(self.readByte(address, wayNum))[2:].zfill(8)) # convert to binary and pad with zeros
                    address += 1 # increment address by 1 to get new address
                return int(DataFound,2)
            else:
                raise ValueError("Invalid func3 value, expected 0,1 or 2 but got "+str(func3)+" instead")

        
        elif self.mapping == "fully-associative":
            for i in range(len(self.tag_arrays)):
                if self.tag_arrays[i].get(Index,-1) == Tag: # found in cache
                    self.hits += 1
                    return self.blocks[i][Index]
            
            self.misses += 1
            return None

    def break_address(self, address:int):
        # considering 32 bit address
        address = bin(address)[2:].zfill(32) # converting to binary and padding with zeros to make it 32 bits
        
        numberOfBlocks = self.cache_size / self.block_size
        numberOfSets = numberOfBlocks / self.number_of_ways
        
        # Calculating the number of bits for tag, index and block offset
        IndexBitsNum = math.log(numberOfSets, 2)
        blockOffsetBitsNum = math.log(self.block_size, 2)
        TagBitsNum = 32 - IndexBitsNum - blockOffsetBitsNum # remaining bits are tag bits

        # Calculating the tag, index and block offset
        Tag = int(address[0:TagBitsNum],2)
        Index = int(address[TagBitsNum:IndexBitsNum + TagBitsNum],2)
        blockOffset = (address[TagBitsNum+IndexBitsNum:TagBitsNum+IndexBitsNum+blockOffsetBitsNum],2)

        return Tag, Index, blockOffset
    























