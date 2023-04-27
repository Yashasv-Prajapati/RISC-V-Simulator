import sys

# registers
register = [0]*32

# instruction memory
MEM = [0]*4000

# data memory
data_mem = {}

# knobs
# knob1 = int(input()) # 0 -> no pipeline 1 -> pipeline
# knob2 = int(input()) # 0 -> no forwarding 1 -> forwarding


def reset_proc():
    pass

# Loading instruction memory
def load_program_memory(file, MEM):
    '''
        Load program Memory
    '''
    f = open(file, 'r')

    for line in f.readlines():
        address, instruction = line.split()

        address = int(address,16) 
        instruction = int(instruction,16)

        write_word(address, instruction, MEM)

    f.close()


# function to write instructions to the instruction memory
def write_word(address, instruction, MEM):
    '''
        Write Word
    '''
    index = address/4
    MEM[int(index)] = instruction


class data_path:
    def __init__(self):
        # initial values for all stages
        self.ready = [1]*32
        self.pc = 0
        self.clock = 0
        self.cycle = 0
        self.IF = 0

        # decode initial values
        self.instructionType = ""
        self.opcode = ""
        self.rs1 = None
        self.rs2 = None
        self.rd = None
        self.immFinal = None
        self.immJ = None
        self.immU = None
        self.immB = None
        self.immS = None
        self.func3 = None
        self.func7 = None
        self.ALUop = None
        self.ResultSelect = None
        self.RFWrite = None
        self.MemOp = None
        self.isBranch = None
        self.op2Select = None
        # self.BranchTargetSelect = None

        # execute
        self.ALUResult = 0
        self.operand1 = 0
        self.operand2 = 0
        

        # memory
        self.address = ""
        self.AddressData = None
        self.ReadData = None
        self.BranchTargetResult = None
        self.BranchTargetAddress = None

    def fetch(self):
        '''
            Fetch
        '''

        self.IF = self.read_word(self.pc) # read instruction from instruction memory
        
        if(int(self.IF, 16)==0xfffffffb):
            print("ALL INSTRUCTIONS DONE, EXITING")
            sys.exit(0)    
    
    def decode(self):

        if(len(self.IF) == 0):
            print("NOTHING FOUND, RETURNING")
            return
        
        
        # converting IF(Instruction) to binary using self.IF 
        IF = int(self.IF, 2)
        
        # getting opcode using mask in integer format
        opcode_mask = 0b1111111
        self.opcode = IF & opcode_mask

        print("opcode ", bin(self.opcode))

        # get func3 and func7 in integer format
        self.func3 = (IF>>12) & 0b111
        self.func7 = (IF>>25) & 0b1111111

        # get instruction type from opcode
        self.instructionType = self.getInstructionType(self.opcode)
        print("INSTRUCTION TYPE IS ", self.instructionType)

        # rs1, rs2 and rd calculation
        # find first source register in interget format 
        rs1_mask = 0b11111
        self.rs1 =(IF>>15) & rs1_mask

        # find second source register in integer format
        rs2_mask = 0b11111
        self.rs2 = (IF>>20)&rs2_mask

        # find destination register in integer format
        rd_mask = 0b11111
        self.rd = (IF>>7) & rd_mask

        print("rs1 ", self.rs1, " rs2 ", self.rs2, " rd ", self.rd)

        # set the current destination register as busy and also check if the current instruction is a branch instruction or a store instruction, in those cases, we don't need to set the destination register as busy
        if(self.instructionType != "B" and self.instructionType != "S"):
            self.ready[self.rd] = 0

        # immediate calculation
        self.immFinal = self.getFinalImmediate(self.instructionType, IF)

        # ALUop calculation
        self.ALUop = self.getALUop(self.instructionType, self.func3, self.func7)

        # op2Select calculation
        self.operand1, self.operand2 = self.op2selectMUX(self.instructionType,self.rs1, self.rs2, self.immFinal, register)

        # BranchTargetSelect calculation
        self.BranchTargetResult = self.BranchTargetSelectMUX(self.instructionType, self.immFinal) 

        # MemOp calculation
        self.MemOp = self.getMemOp(self.instructionType, self.opcode)

        # RFWrite calculation and ResultSelect calculation
        self.RFWrite, self.ResultSelect = self.ResultSelectMUX(self.opcode, self.instructionType)
        
        # isBranch calculation
        self.isBranch = self.isBranchInstruction(self.opcode, self.instructionType, self.func3, self.operand1, self.operand2)

        register[0] = 0

    def execute(self):
        '''
        ALUop operation
        0 - perform none (skip)
        1 - add
        2 - subtract
        3 - and
        4 - or
        5 - shift left
        6 - shift right
        7 - xor
        8 - set less than
        '''

        print("EXECUTE") # execute start
        print("ALUop=",self.ALUop) # print ALUop
        print("operand1=",self.operand1, " operand2=",self.operand2) # print operand1 and operand2
        
        # calculate ALUResult by using operand1 and operand2 and ALUop
        if (self.ALUop == 1):
            self.ALUResult = self.operand1 + self.operand2
        elif (self.ALUop == 2):
            self.ALUResult = self.operand1 - self.operand2
        elif (self.ALUop == 3):
            self.ALUResult = self.operand1 & self.operand2
        elif (self.ALUop == 4):
            self.ALUResult = self.operand1 | self.operand2
        elif (self.ALUop == 5):
            self.ALUResult = self.operand1 << self.operand2
        elif (self.ALUop == 6):
            self.ALUResult = self.operand1 >> self.operand2
        elif (self.ALUop == 7):
            self.ALUResult = self.operand1 ^ self.operand2
        elif (self.ALUop == 8):
            self.ALUResult = 1 if (self.operand1 < self.operand2) else 0

        # Also at the same time set BranchTargetAddress to BranchTargetResult + pc*4
        self.BranchTargetAddress= self.BranchTargetResult + (self.pc*4)
        print("ALUResult is: ", self.ALUResult)
        
        register[0] = 0

    def memory(self):
        '''
        MemOp operation
        0 - Do nothing (skip)
        1 - Write in memory --> Store
        2 - Read from memory --> Load
        '''

        print("MEMORY")

        if (self.MemOp == 0):
            print("There is no Memory Operation")
            self.ReadData = self.ALUResult
        elif (self.MemOp == 1): 
            # Store
            print("data_mem[",self.ALUResult,"]=register[",self.rs2,"]=",register[self.rs2])
            
            data_mem[self.ALUResult] = register[self.rs2]
            
            self.ReadData = data_mem[self.ALUResult]
            
            print("There is a Store Operation to be done to memory and operand2=",self.operand2)
        elif (self.MemOp == 2):
            # Load

            # Load data from memory to ReadData, if the data is not present in dictionary, then set it to 0(default value)
            self.ReadData = data_mem.get(self.ALUResult, 0)
            print("There is a Read Operation to be done from memory")
            
            print("ReadData=data_mem[",self.ALUResult,"]")

        self.MemOp = 0
        register[0] = 0

    def write(self):
        '''
            ResultSelect
            5 - None
            0 - PC+4
            1 - ImmU_lui
            2 - ImmU_auipc
            3 - LoadData - essentially same as ReadData
            4 - ALUResult
        '''
        print("WRITEBACK ")

        print("RESULTSELECT",self.ResultSelect)

        # check if we have to write or not
        if (self.RFWrite):

            # now check for which resultselect to choose and write accordingly

            if (self.ResultSelect == 0):
                register[self.rd] = 4 * (self.pc + 1)
                print("Write Back  ", 4*(self.pc+1), "to R", self.rd)

            elif (self.ResultSelect == 1):

                register[self.rd] = self.immFinal
                print("Write Back to ", self.immFinal, "to R", self.rd)

            elif (self.ResultSelect == 2):

                register[self.rd] = self.pc*4 + self.immFinal
                print("Write Back to ", self.immFinal, "to R", self.rd)

            elif (self.ResultSelect == 3):
                
                register[self.rd] = self.ReadData
                print("Write Back  ", self.ReadData, "to R", self.rd)

            elif (self.ResultSelect == 4):

                register[self.rd] = self.ALUResult
                print("Write Back to ", self.ALUResult, "to R", self.rd)

        else:
            print("There is no Write Back")

        '''
            IsBranch=0 => ALUResult
            =1         => BranchTargetAddress
            =2         => pc+4(default)
        '''

        # check if isBranch is 1 or 0 or none of these and accordingly set pc
        if (self.isBranch == 0):
            print("ALUResult=",self.ALUResult)
            self.pc = self.ALUResult
            self.pc//=4
        elif (self.isBranch == 1):
            print("BranchTargetAddress=",self.BranchTargetAddress)
            self.pc = self.BranchTargetAddress
            self.pc//=4
        else:
            self.pc += 1
            if((self.instructionType=='J' or self.instructionType=='B')):# ie if fetch is waiting and it is not the end
                print("YES")
            else:
                print("NO")
        print("new PC is ", self.pc)

    def getInstructionType(self,opcode):
        '''Get Type of Instruction from opcode'''
        inst_type = ''

        print("opcode is ", bin(opcode))

        if (opcode == 0b0110011):
            inst_type = 'R'
        elif (opcode == 0b0010011 or opcode == 0b0000011 or opcode == 0b1100111):
            inst_type = 'I'
        elif (opcode == 0b0100011):
            inst_type = 'S'
        elif (opcode == 0b1100011):
            inst_type = 'B'
        elif (opcode == 0b0110111):
            inst_type = 'U'
        elif (opcode == 0b1101111):
            inst_type = 'J'
        else:
            print("Not valid instruction type Detected")
            print(register)
            print(data_mem)
            sys.exit(1)
        
        return inst_type
    
    def getFinalImmediate(self,inst_type, instruction_word):
        # normal immediate
        imm = instruction_word
        imm = imm >> 20
        imm_mask = 0b111111111111
        imm = imm & imm_mask

        # IMM S Generation
        immS=instruction_word
        immS1=immS>>7
        immS2=immS>>25
        immS_mask1=0b11111
        immS_mask2=0b1111111
        immS=(immS1 & immS_mask1)+((immS2 & immS_mask2)<<5)

        # IMM B Generation
        immB=instruction_word
        immB1=instruction_word>>7
        immB_mask1=0b1#for 11th
        immB2=instruction_word>>7
        immB_mask2=0b11110
        immB3=instruction_word>>25
        immB_mask3=0b111111
        immB4=instruction_word>>31
        immB_mask4=0b1#for 12th
        immB=((immB1 & immB_mask1)<<11) + ((immB2 & immB_mask2)) + ((immB3 & immB_mask3)<<5) +((immB4& immB_mask4)<<12)

        # IMM U Generation
        immU=instruction_word>>12
        immU_mask=0b11111111111111111111
        immU=((immU&immU_mask)<<12)

        # IMM J Generation
        immJ = instruction_word
        immJ1=instruction_word>>12
        immJ_mask1=0b11111111
        immJ2=instruction_word>>20
        immJ_mask2=0b1
        immJ3=instruction_word>>21
        immJ_mask3=0b1111111111
        immJ4=instruction_word>>31
        immJ_mask4=0b1
        immJ = ((immJ1 & immJ_mask1) << 12) + \
            ((immJ2 & immJ_mask2) << 11) + \
            ((immJ3 & immJ_mask3) << 1)+((immJ4 & immJ_mask4) << 20)


        immFinal = 0
        if inst_type == 'I':
            immFinal = imm
            if ((immFinal >> 11) == 1):
                immFinal = immFinal-4096
        if inst_type == 'S':
            immFinal= immS
            if((immFinal>>11)==1):
                immFinal=immFinal-4096
        if inst_type == 'B':
            immFinal = immB
            if ((immFinal >> 12) == 1):
                immFinal = immFinal-8192
        if inst_type == 'U':
            immFinal= immU
        if inst_type == 'J':
            immFinal = immJ
            if ((immFinal >> 20) == 1):
                immFinal = immFinal-2097152
        return immFinal
    
    def getALUop(self,inst_type, func3, func7):
        '''
        ALUop operation
        0 - perform none (skip)
        1 - add
        2 - subtract
        3 - and
        4 - or
        5 - shift left
        6 - shift right
        7 - xor
        8 - set less than
        '''
        ALUop = 0

        if (inst_type == 'R'):
            if (func3 == 0x0):
                if (func7 == 0x0):
                    ALUop = 1
                elif (func7 == 0x20):
                    ALUop = 2

            elif (func3 == 0x4):
                ALUop = 7
            elif (func3 == 0x6):
                ALUop = 4
            elif (func3 == 0x7):
                ALUop = 3
            elif (func3 == 0x1):
                ALUop = 5
            elif (func3 == 0x5):
                ALUop = 6
        elif (inst_type == 'I'):
            if (func3 == 0x0):
                ALUop = 1
            elif (func3 == 0x7):
                ALUop = 3
        if inst_type == 'I':
            if ((func3 == 0x0) or (func3 == 0x2) or (func3 == 0x1)):
                ALUop = 1
            elif func3 == 0x6:
                ALUop = 4
            elif func3 == 0x7:
                ALUop = 3
        if inst_type == 'S':
            ALUop = 1
        if inst_type == 'B':
            ALUop = 2
        if inst_type == 'U' or inst_type == 'J':
            ALUop = 1

        return ALUop

    def op2selectMUX(self,inst_type, rs1, rs2, imm_final, register):
        '''
            Op2SelectMUX
        '''

        operand1 = register[rs1]
        if (inst_type == 'S' or inst_type == 'I'):
            operand2 = imm_final
        else:
            operand2 = register[rs2]
        
        return operand1, operand2
    
    def BranchTargetSelectMUX(self,inst_type, imm_final):
        '''
            Branch Target Select MUX
        '''

        BranchTargetResult = imm_final

        return BranchTargetResult

    def getMemOp(self,instType, opcode):
        '''
            Get Mem Op
        '''
        if (instType == 'S'):
            MemOp = 1
        elif (opcode == 0b0000011):
            MemOp = 2
        else:
            MemOp = 0

        return MemOp

    def ResultSelectMUX(self,opcode, inst_type):
        '''
        ResultSelect
        5 - None
        0 - PC+4
        1 - ImmU_lui
        2 - ImmU_auipc
        3 - LoadData - essentially same as ReadData
        4 - ALUResult
        '''

        RFWrite = 0
        ResultSelect = None

        if (opcode == 0b0110111):
            ResultSelect = 1
            RFWrite = 1
        elif (opcode == 0b0010111):
            ResultSelect = 2
            RFWrite = 1
        elif (opcode == 0b1101111 or opcode == 0b1100111):
            ResultSelect = 0
            RFWrite = 1
        elif (opcode == 0b0000011):
            ResultSelect = 3
            RFWrite = 1
        elif (opcode == 0b0100011 or inst_type == 'B'):
            RFWrite = 0
            ResultSelect = 5
        else:
            ResultSelect = 4
            RFWrite = 1

        return RFWrite, ResultSelect

    def isBranchInstruction(self,opcode, inst_type, func3, operand1, operand2):
            '''
                Check weather the condition is a branch instruction
                IsBranch=0 => ALUResult
                =1         => BranchTargetAddress
                =2         => pc+4(default)
            '''
            # print("operand1=",operand1,"and operand2=",operand2)
            if (opcode == 0b1100111):
                isBranch = 0
            elif (inst_type == 'B'):
                isBranch = 2
                if (func3 == 0x0 and operand1 == operand2):
                    print("operand1==operand2 because operand1=",operand1," and operand2=",operand2)
                    isBranch = 1
                elif (func3 == 0x1 and operand1 != operand2):
                    isBranch = 1
                elif (func3 == 0x4 and operand1 < operand2):
                    isBranch = 1
                elif (func3 == 0x5 and operand1 >= operand2):
                    isBranch = 1
            elif (inst_type == 'J'):
                isBranch = 1
            else:
                isBranch = 2

            return isBranch

    # function to read instructions from instruction memory
    def read_word(self,address):
        '''
            Read Word
        '''
        print("address is: ", address)
        instruction =  MEM[(address)]
        instruction = bin(instruction)[2:] # convert to binary and [2:] to remove 0b
        return instruction

if(1):
<<<<<<< HEAD
    load_program_memory('TestFiles/MergeSort.mem', MEM)
=======
    # load_program_memory('TestFiles/output.mem', MEM)
>>>>>>> refs/remotes/origin/main
    non_pipeline = data_path()
    non_pipeline.pc = 0
    
    while(1):
        non_pipeline.fetch()
        non_pipeline.decode()
        non_pipeline.execute()
        non_pipeline.memory()
        non_pipeline.write()
<<<<<<< HEAD
        print("--------------------------------------------")
=======
        print("--------------------------------------------")
    
>>>>>>> refs/remotes/origin/main
