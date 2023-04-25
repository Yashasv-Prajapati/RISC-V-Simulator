import math
import numpy as np

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
        self.cache_access = 0


        # set number_of_ways
        self.setNumberOfWays(numberOfWays, mapping, cacheSize, blockSize)

        # set replacement policy
        self.setReplacementPolicy(policyName)

        # total tag arrays -> number of ways and each array is a dictionary 
        self.tag_arrays = np.full((numberOfWays), {}, dtype=object)
        self.blocks = np.full((numberOfWays), {}, dtype=object)

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

    def get_cache_size(self):
        return self.cache_size
    
    def get_block_size(self):
        return self.block_size

    def get_mapping(self):
        return self.mapping
    
    def get_data(self,address:str):
        Tag, Index, blockOffset = self.break_address(address)

        if self.mapping == "direct":
            if self.tag_arrays[0].get(Index, -1) == Tag: # found in cache
                self.hits += 1
                # using block offset to get data from block
                
                return self.blocks[0][Index]
            else:
                self.misses += 1
                # get data from main memory
                return None # this to be changed
            
        elif self.mapping == "set-associative":
            # search in all of tag arrays -> n if n is the number of ways
            for i in range(len(self.tag_arrays)):
                if self.tag_arrays[i].get(Index,-1) == Tag: # found in cache
                    self.hits += 1
                    return self.blocks[i][Index]
            
            # not found in cache so get data from main memory
            self.misses += 1
            return None # this to be changed
        
        elif self.mapping == "fully-associative":
            for i in range(len(self.tag_arrays)):
                if self.tag_arrays[i].get(Index,-1) == Tag: # found in cache
                    self.hits += 1
                    return self.blocks[i][Index]
            
            self.misses += 1
            return None

    def break_address(self, address:str):
        # considering 32 bit address
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
    
