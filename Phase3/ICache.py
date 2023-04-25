
import math
import numpy as np

instruction_mem = np.zeros((2**32), dtype='uint8') # instruction memory

class ICache:
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
        
        # set number_of_ways
        self.setNumberOfWays(numberOfWays, mapping, cacheSize, blockSize)

        # set replacement policy
        self.setReplacementPolicy(policyName)

        


        # LRU policy
        # number of ways x 3, 3 is for the Valid bit, status bit and tag bit
        self.LRU = np.zeros((self.number_of_ways), dtype='uint32')

        # FIFO policy
        self.FIFO = np.zeros((self.number_of_ways), dtype='uint32')

        # LFU policy
        # self.LFU = np.zeros((numberOfWays,2), dtype='uint32')
        self.LFU = {}

        # Random policy
        self.Random = np.zeros((self.number_of_ways), dtype='uint32')

        self.cache_access = {} # dictionary to store all the cache accesses
        self.mct = {} # miss classification table

        
        # total tag arrays -> number of ways and each array is a dictionary 
        self.tag_arrays = np.full((numberOfWays), {}, dtype=object)

        # number of instruction arrays = number of ways. each array has <number of blocks> rows and <block size> columns
        self.instruction_cache = np.full((numberOfWays, cacheSize//blockSize, blockSize), 0, dtype='uint8')

    def setNumberOfWays(self, numberOfWays:int, mapping:str, cacheSize:int, blockSize:int):
        if(mapping not in self.__mapping):
            raise Exception("Invalid Mapping")
        
        elif(mapping == "direct"):
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

    def WriteInstructionInMain(self, address:int, instruction:int):
        '''
        This function is used to set instruction in the main memory
        Considering instruction to be of 32 bits/4 Bytes or max value of int to be 2^31 - 1
        '''
        instructionInBinary = bin(instruction)[2:].zfill(32) # converting instruction to a 32 bit binary string
        # set instruction in main memory
        for i in range(4):
            instruction_mem[address+i] = int(instructionInBinary[i*8:i*8+8],2)
        
        
         
    def getFromMain(self, address:int):
        '''
        This function is used to get instruction from the main memory

        address: the address of the instruction

        returns: binary string of instruction of size `blocksize` from main memory
        '''
        # return instruction from main memory, considering main memory to be a dictionary
        # we have to take blocksize amount of bytes from main memory
        instructionFromMain = ''
        for i in range(self.block_size):
            instructionFromMain += bin(instruction_mem[address+i])[2:].zfill(8) # taking 8 bits/1byte at a time 
        
    
        return instructionFromMain
    
    def write_instruction(self, address:int, instruction:int, func3:int):
        '''
        This function is used to write instruction in the cache
        first the instruction is written in the cache then subsequently in the main memory at that particular address

        address: the address of the instruction
        instruction: the instruction to be written
        '''

        Tag, Index, blockOffset = self.break_address(address)



    def get_instruction(self,address:int):

        '''
        This function is used to get instruction from the cache
        if the instruction is not in the cache then it will get it from the main memory

        address: the address of the instruction
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
                # so we look into the MCT to find out if it's a conflict or capacity miss
                if(Tag in self.mct): # if tag is there in MCT, so it was once in the cache -> conflict miss
                    self.conflict_misses += 1
                else: # capacity miss
                    self.capacity_misses += 1
            else:
                # else the instruction is present in the cache -> hit
                self.hits += 1

            # check type of load instruction
            if(func3==0): # lb
                return self.readByte(address, 0)
            
            elif(func3==1): # lh
                for i in range(2):
                    InstructionFound += bin(self.readByte(address, 0))[2:].zfill(8) # convert to binary and pad with zeros
                    address+=1 # increment address by 1 to get new address
                return int(InstructionFound,2)
            
            elif(func3==2): # lw
                for i in range(4):
                    InstructionFound += bin(self.readByte(address, 0))[2:].zfill(8) # convert to binary and pad with zeros
                    address += 1 # increment address by 1 to get new address
                return int(InstructionFound,2)
            
        elif self.mapping == "set-associative":

            # check type of miss
            ColdMiss = True
            CapacityORConflict = False
            wayNum = None

            # look into all the ways to find the instruction
            for i in range(len(self.tag_arrays)):
                if(self.tag_arrays[i].get(Index, -1)==Tag): # hit
                    ColdMiss = False
                    CapacityORConflict = False
                    wayNum = i # way number where instruction is found
                    self.hits =+ 1 # increment hits
                    break
                if(self.tag_arrays[i].get(Index, -1)==-1): # cold miss
                    ColdMiss = True # not a cold miss
                    CapacityORConflict = False # not a capacity miss
                    wayNum = i # way number where instruction is to be stored
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
                    wayNum = LRUWay # way number where instruction is to be replaced from and return the updated instruction
                    self.LRU.insert(0,LRUWay) # insert it at the start to make it the most recently used
                elif(self.replacement_policy=='FIFO'):
                    FIFOWay = self.FIFO.pop(0) # get the first entry in the queue
                    wayNum = FIFOWay
                    self.FIFO.append(FIFOWay) # append it to the end of the queue
                elif(self.replacement_policy=='random'):
                    pass
                    # apply the easiet policy here
                    
                elif(self.replacement_policy=='LFU'):
                    # apply the LFU policy here
                    MIN = min(self.LFU, key=self.LFU.get) # get the key with the maximum value
                    wayNum = MIN # way number where instruction is to be replaced from and return the updated instruction
                    self.LFU[MIN] += 1 # increment the value of the key
                
                if(Tag in self.mct):
                    self.conflict_misses += 1
                else:
                    self.capacity_misses += 1
            # ---------------------------------------------------------------
            # once you know the wayNumber, now go to that way and get instruction from there
            # check type of load instruction
            if(func3==0): # lb
                return self.readByte(address, wayNum)
            
            elif(func3==1): # lh
                for _ in range(2):
                    InstructionFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                    address+=1 # increment address by 1 to get new address
                return int(InstructionFound,2)
            
            elif(func3==2): # lw
                for _ in range(4):
                    InstructionFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                    address += 1 # increment address by 1 to get new address
                return int(InstructionFound,2)
            else:
                raise ValueError("Invalid func3 value, expected 0, 1 or 2 but got "+str(func3)+" instead")

        
        elif self.mapping == "fully-associative":
            # check type of miss
            ColdMiss = True
            CapacityORConflict = False
            wayNum = None

            # look into all the ways to find the instruction
            for i in range(len(self.tag_arrays)):
                if(self.tag_arrays[i].get(Index, -1)==Tag): # hit
                    ColdMiss = False
                    CapacityORConflict = False
                    wayNum = i # way number where instruction is found
                    self.hits =+ 1 # increment hits
                    break
                if(self.tag_arrays[i].get(Index, -1)==-1): # cold miss
                    ColdMiss = True # not a cold miss
                    CapacityORConflict = False # not a capacity miss
                    wayNum = i # way number where instruction is to be stored
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
                    wayNum = LRUWay # way number where instruction is to be replaced from and return the updated instruction
                    self.LRU.insert(0,LRUWay) # insert it at the start to make it the most recently used
                elif(self.replacement_policy=='FIFO'):
                    FIFOWay = self.FIFO.pop(0) # get the first entry in the queue
                    wayNum = FIFOWay
                    self.FIFO.append(FIFOWay) # append it to the end of the queue
                elif(self.replacement_policy=='random'):
                    pass
                    # apply the easiet policy here
                    
                elif(self.replacement_policy=='LFU'):
                    # apply the LFU policy here
                    MIN = min(self.LFU, key=self.LFU.get) # get the key with the maximum value
                    wayNum = MIN # way number where instruction is to be replaced from and return the updated instruction
                    self.LFU[MIN] += 1 # increment the value of the key
                
                if(Tag in self.mct):
                    self.conflict_misses += 1
                else:
                    self.capacity_misses += 1
            # ---------------------------------------------------------------
            # once you know the wayNumber, now go to that way and get instruction from there
            # check type of load instruction
            if(func3==0): # lb
                return self.readByte(address, wayNum)
            
            elif(func3==1): # lh
                for _ in range(2):
                    InstructionFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                    address+=1 # increment address by 1 to get new address
                return int(InstructionFound,2)
            
            elif(func3==2): # lw
                for _ in range(4):
                    InstructionFound += bin(self.readByte(address, wayNum))[2:].zfill(8) # convert to binary and pad with zeros
                    address += 1 # increment address by 1 to get new address
                return int(InstructionFound,2)
            else:
                raise ValueError("Invalid func3 value, expected 0, 1 or 2 but got "+str(func3)+" instead")

        

            return None

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


if __name__ =='__main__':
    L1 = ICache(32, 32, "direct", "LRU", 0)
    L1.WriteInstructionInMain(0, 2**31-1)

    instruction = L1.get_instruction(0, 2)
    print(instruction)













