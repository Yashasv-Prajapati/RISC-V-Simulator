import sys

register = [0] * 32

MEM = [0] * 4000
data_mem = [0] * 100000000

instruction_word = 0
pc = 0
opcode = 0
rs1 = 0
rs2 = 0
rd = 0
func3 = 0
func7 = 0
imm = 0
immS = 0
immB = 0
immU = 0
immJ = 0
operand1 = 0
operand2 = 0
MemOp = 0
BranchTargetResult = 0
ALUop = 0
RFWrite = 0
ResultSelect = 0
isBranch = 0
immFinal = 0

def reset_proc():
    pass

def load_program_memory(file):
    '''
        Load program Memory
    '''
    global MEM
    f = open(file, 'r')

    for line in f.readlines():
        address, instruction = line.split()

        address = int(address,16)
        instruction = int(instruction,16)

        write_word(address, instruction)

    f.close()

def run_riscvsim():
    global instruction_word, pc

    while(1):
        fetch()
        if(instruction_word>=4294967291):
            break
        
        decode()
        execute()
        mem()
        write_back()
        print('\n\n')


def write_word(address, instruction):
    '''
        Write Word
    '''
    global MEM
    index = address/4
    MEM[int(index)] = instruction

def fetch():
    '''
        Fetch Instruction
    '''
    global instruction_word
    instruction_word = read_word(pc);

def read_word(address):
    '''
        Read Word
    '''
    global MEM
    return MEM[address]

def decode():
    '''
        Decode Instruction
    '''
    global operand1, operand2
    global instruction_word, opcode, rs1, rs2, rd, func3, func7, imm, immS, immB, immU, immJ, ALUop, immFinal

    opcode_mask = 0b1111111
    opcode = instruction_word & opcode_mask

    rs1 = instruction_word
    rs1 = rs1 >> 15
    rs1_mask = 0b11111
    rs1 = rs1 & rs1_mask
    
    rs2 = instruction_word
    rs2 = rs2 >> 20
    rs2_mask = 0b11111
    rs2 = rs2 & rs2_mask

    rd = instruction_word
    rd = rd >> 7
    rd_mask = 0b11111
    rd = rd & rd_mask

    func3 = instruction_word
    func3 = func3 >> 12
    func3_mask = 0b111
    func3 = func3 & func3_mask

    func7 = instruction_word
    func7 = func7 >> 25
    func7_mask = 0b1111111
    func7 = func7 & func7_mask

    imm = instruction_word
    imm = imm >> 20
    imm_mask = 0b111111111111
    imm = imm & imm_mask

    #Generate immS, immB, ImmU, immJ

    inst_type = getInstructionType(opcode)

    immFinal = getFinalImmediate(inst_type, imm) # immS, immB, ImmU, immJ

    ALUop = getALUop(inst_type, func3, func7) #Some Part Left

    op2selectMUX(inst_type, rs1, rs2, immFinal)
    BranchTargetSelectMUX(inst_type, immFinal)
    getMemOp(inst_type, opcode)
    ResultSelectMUX(opcode, inst_type)
    isBranchInstruction(opcode, inst_type, func3)

    printOperationDetails(inst_type, immFinal) # Left

    #print(inst_type, immFinal, ALUop)
    
    #print(bin(rs1), bin(rs2), bin(rd))

def getFinalImmediate(inst_type, imm):
    immFinal = 0
    if inst_type == 'I':
        immFinal = imm

    return immFinal

def getInstructionType(opcode):
    '''Get Type of Instruction from opcode'''
    inst_type = ''

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
        sys.exit(1)
    
    return inst_type

def getALUop(inst_type, func3, func7):
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
            ALUop  = 5
        elif (func3 == 0x5):
            ALUop = 6
    elif (inst_type == 'I'):
        if (func3 == 0x0):
            ALUop = 1
        elif (func3 == 0x7):
            ALUop = 3

    return ALUop

def op2selectMUX(inst_type, rs1, rs2, imm_final):
    '''
        Op2SelectMUX
    '''
    global operand1, operand2
    operand1 = register[rs1]
    if (inst_type == 'S' or inst_type == 'I'):
        operand2 = imm_final
    else:
        operand2 = register[rs2]

def BranchTargetSelectMUX(inst_type, imm_final):
    '''
        Branch Target Select MUX
    '''
    global BranchTargetResult
    BranchTargetResult = imm_final

def getMemOp(instType, opcode):
    '''
        Get Mem Op
    '''
    global MemOp
    if (instType == 'S'):
        MemOp = 1
    elif (opcode == 0b0000011):
        MemOp = 2
    else:
        MemOp = 0

def ResultSelectMUX(opcode, inst_type):
    '''
    ResultSelect
    5 - None
    0 - PC+4
    1 - ImmU_lui
    2 - ImmU_auipc
    3 - LoadData - essentially same as ReadData
    4 - ALUResult
    '''
    
    global RFWrite, ResultSelect
    RFWrite = 0

    if (opcode == 0b0110111):
        ResultSelect = 1
        RFWrite = 1
    elif (opcode == 0b0010111):
        ResultSelect = 2
        RFWrite = 1
    elif(opcode == 0b1101111 or opcode == 0b1100111):
        ResultSelect = 0
        RFWrite = 1
    elif (opcode == 0b0000011):
        ResultSelect = 3
        RFWrite = 1
    elif (opcode == 0b0100011 or inst_type == 'B'):
        RFWrite = 0
    else:
        ResultSelect = 4
        RFWrite = 1

def isBranchInstruction(opcode, inst_type, func3):
    '''
        Check weather the condition is a branch instruction

        IsBranch=0 => ALUResult
        =1         => BranchTargetAddress
        =2         => pc+4(default)
    '''
    global isBranch
    if (opcode == 0b1100111): 
        isBranch = 0
    elif (inst_type == 'B'):
        isBranch = 2
        if (func3 == 0x0 and operand1 == operand2):
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

def printOperationDetails(inst_type, immFinal):
    '''
        Print Operation Details
    '''
    global ALUop

    if (inst_type == 'R'):
        if (ALUop == 1):
            print("Instruction Type is ADD")
        elif (ALUop == 3):
            print("Instruction Type is AND")

        print("Operands are: ",operand1, operand2)   
        print("Write Register is: ", rd) 
    elif (inst_type == 'I'):
        if (ALUop == 1):
            print("Instruction Type is ADDI")
        elif (ALUop == 3):
            print("Instruction Type is ANDI")

        print("Operand is: ",operand1)
        print("Immediate is: ", immFinal)   
        print("Write Register is: ", rd) 

def execute():
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
    global ALUop, ALUResult, BranchTargetAddress

    if (ALUop == 1):
        ALUResult = operand1 + operand2
    elif (ALUop == 2):
        ALUResult = operand1 - operand2
    elif (ALUop == 3):
        ALUResult = operand1 & operand2
    elif (ALUop == 4):
        ALUResult = operand1 | operand2
    elif (ALUop == 5):
        ALUResult = operand1 << operand2
    elif (ALUop == 6):
        ALUResult = operand1 >> operand2
    elif (ALUop == 7):
        ALUResult = operand1 ^ operand2
    elif (ALUop == 8):
        ALUResult = 1 if (operand1 < operand2) else 0

    print("ALUResult: ", ALUResult)
    
    BranchTargetAddress=BranchTargetResult+pc
    
def mem():
    '''
    MemOp operation
    0 - Do nothing (skip)
    1 - Write in memory --> Store
    2 - Read from memory --> Load
    '''
    global MemOp, ReadData, rs2

    print("MEMORY")

    if (MemOp == 0):
        print("There is no Memory Operation\n")
        ReadData = ALUResult
    elif (MemOp == 1): 
        # Store

        # unsigned int *data_p;
        # data_p = (unsigned int*)(DataMEM + ALUResult);
        data_mem[ALUResult] = rs2
        ReadData = data_mem[ALUResult]
        # int rs2Value = BintoDec(rs2,5);
        # *data_p = X[rs2Value];
        # ReadData = X[rs2Value];
        print("There is a Store Operation to be done from memory\n")
    elif (MemOp == 2):
        # Load
        # int *data_p;
        # data_p = (int*)(DataMEM + ALUResult);
        # ReadData = *data_p;
        ReadData = data_mem[ALUResult]
        print("There is a Read Operation to be done from memory\n")

    MemOp = 0

def write_back():
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

    global RFWrite, rd, immFinal, ReadData, ALUResult
    print(ResultSelect)

    if (RFWrite):
        if (ResultSelect == 0):
            register[rd] = pc + 1
            print("Write Back to ", pc+4, "to R", rd)
        elif (ResultSelect == 1):
            register[rd] = immFinal
            print("Write Back to ", immFinal, "to R", rd)
        elif (ResultSelect == 2):
            register[rd] = pc + immFinal/4
            print("Write Back to ", immFinal, "to R", rd)
        elif (ResultSelect == 3):
            register[rd] = ReadData
            print("Write Back to ", ReadData, "to R", rd)
        elif (ResultSelect == 4):
            register[rd] = ALUResult
            print("Write Back to ", ALUResult, "to R", rd)
    else:
        print("There is no Write Back")

    isBranchMUX()

def isBranchMUX():
    '''
        IsBranch=0 => ALUResult
        =1         => BranchTargetAddress
        =2         => pc+4(default)
    '''
    global isBranch, pc, ALUResult, BranchTargetAddress
    if (isBranch == 0):
        pc = ALUResult
    elif (isBranch == 1):
        pc = BranchTargetAddress
    else:
        pc += 1
    