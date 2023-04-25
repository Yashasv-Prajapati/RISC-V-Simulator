   
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

        self.cache_access = {} # dictionary to store all the cache accesses
        self.mct = {} # miss classification table


        # set number_of_ways
        self.setNumberOfWays(numberOfWays, mapping, cacheSize, blockSize)

        # set replacement policy
        self.setReplacementPolicy(policyName)

        # total tag arrays -> number of ways and each array is a dictionary 
        self.tag_arrays = np.full((numberOfWays), {}, dtype=object)

        # number of instruction arrays = number of ways. each array has <number of blocks> rows and <block size> columns
        self.instruction_cache = np.full((numberOfWays, cacheSize//blockSize, blockSize), 0, dtype='uint8')

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
        
        if(self.tag_arrays[wayNumber].get(Index, -1)==-1):
            self.cold_misses += 1

        if self.tag_arrays[wayNumber].get(Index, -1) == Tag: # found in cache
            self.hits += 1
            # using block offset to get instruction from block
            return self.instruction_cache[wayNumber][Index][blockOffset]
        
        else: # handle miss
            self.misses += 1
            # update tag array
            self.tag_arrays[wayNumber][Index] = Tag

            # get instruction from main memory
            instructionFromMain = self.getFromMain(address)
            
            # set instruction in cache  
            # converting instructionReceived to a 256 bit binary string
            instructionInBinary = bin(instructionFromMain)[2:].zfill(256) # instruction of form '100010001...' -> 256 bits
            
            # now storing each byte in the cache
            for i in range(32):
                self.instruction_cache[wayNumber][Index][i] = int(instructionInBinary[i*8:i*8+8],2)

            return self.instruction_cache[wayNumber][Index][blockOffset]

    def getFromMain(self, address:int):
        '''
        This function is used to get instruction from the main memory
        '''
        # return instruction from main memory, considering main memory to be a dictionary
        return instruction_mem.get(address, 0)
        
    def instruction(self, address:int, func3:int):
        '''
        This function is used to set instruction from the cache
        It will set it to the main memory 

        address: the address of the instruction
        func3: depending on type of store instruction
            if func3 == 0b000 -> sb
            if func3 == 0b001 -> sh
            if func3 == 0b010 -> sw
        '''
        # add instruction here
    
    def get_instruction(self,address:int, func3:int):

        '''
        This function is used to get instruction from the cache
        if the instruction is not in the cache then it will get it from the main memory

        address: the address of the instruction
        func3: depending on type of load instruction
            if func3 == 0b000 / 0 -> lb
            if func3 == 0b001 / 1 -> lh
            if func3 == 0b010 / 2 -> lw
        '''

        Tag, Index, blockOffset = self.break_address(address)
        
        # requested instruction in binary
        InstructionFound = ""

        # storing all the cache accesses in a dictionary using its address as key
        self.cache_access[address] = True

        if self.mapping == "direct":

            # check type of miss
            if(self.tag_arrays[0].get(Index, -1)==-1): # cold miss
                self.cold_misses += 1
            elif(self.tag_arrays[0].get(Index, -1)!=Tag): # if tag != -1 and tag != Tag -> conflict miss or capacity miss
                # either a conflict or capacity miss
                pass

            if(func3==0): # lb
                return self.readByte(address, 0)
            
            elif(func3==1): # lh
                for i in range(2):
                    InstructionFound.append(bin(self.readByte(address, 0))[2:].zfill(8)) # convert to binary and pad with zeros
                    address+=1 # increment address by 1 to get new address
                return int(InstructionFound,2)
            
            elif(func3==2): # lw
                for i in range(4):
                    InstructionFound.append(bin(self.readByte(address, 0))[2:].zfill(8)) # convert to binary and pad with zeros
                    address += 1 # increment address by 1 to get new address
                return int(InstructionFound,2)
            
        elif self.mapping == "set-associative":
            # search in all of tag arrays -> n if n is the number of ways
            for i in range(len(self.tag_arrays)):
                if self.tag_arrays[i].get(Index,-1) == Tag: # found in cache
                    self.hits += 1
                    return self.blocks[i][Index][blockOffset]
            
            # not found in cache so get instruction from main memory
            self.misses += 1
            return None # this to be changed
        
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
    























