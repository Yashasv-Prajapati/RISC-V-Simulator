import sys
# sys.set_int_max_str_digits(0)

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
    counter=0
    t=1
    print("MEM=",MEM)
    while(1):
        fetch()
        if(instruction_word>=4294967291):
            print("EXITING\n")
            break
        register[0]=0
        decode()
        register[0] = 0
        execute()
        register[0]=0
        mem()
        register[0]=0
        write_back()
        register[0] = 0

        print('\n\n')
        counter=counter+1
        print("Instruction number is",counter)
        t=t+1
    print("PRINTING REGISTER VALUES")
    i=0
    while(i<32):
        print("X[",i,"]=",register[i])
        i=i+1


def write_word(address, instruction):
    '''
        Write Word
    '''
    global MEM
    index = address/4
    MEM[int(index)] = instruction

# Fetch Stage

def fetch():
    '''
        Fetch Instruction
    '''
    print("FETCH")
    print("PC: ", pc)
    global instruction_word
    instruction_word = read_word(pc)
    print("instruction_word in fetch after read_Word=",instruction_word)

def read_word(address):
    '''
        Read Word
    '''
    global MEM
    print("address=",address,"MEM[address]=",MEM[address])
    
    return MEM[(address)]

# Decode Stage
def decode():
    '''
        Decode Instruction
    '''
    print("DECODE")
    global operand1, operand2
    global instruction_word, opcode, rs1, rs2, rd, func3, func7, imm, immS, immB, immU, immJ, ALUop, immFinal
    print("instruction word in binary=",bin(instruction_word))
    print("instruction word in decimal=", instruction_word)

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

    immS=instruction_word
    immS1=immS>>7
    immS2=immS>>25
    immS_mask1=0b11111
    immS_mask2=0b1111111
    immS=(immS1 & immS_mask1)+((immS2 & immS_mask2)<<5)

    # IMM B Generation
    immB=instruction_word
    immB1=instruction_word>>7
    print("instruction word=",bin(instruction_word),"and instruction word<<5=",bin(instruction_word<<5),"and instruction_word>>5=",bin(instruction_word>>5))
    immB_mask1=0b1#for 11th
    immB2=instruction_word>>7
    immB_mask2=0b11110
    immB3=instruction_word>>25
    immB_mask3=0b111111
    immB4=instruction_word>>31
    immB_mask4=0b1#for 12th

    immB=((immB1 & immB_mask1)<<11) + ((immB2 & immB_mask2)) + ((immB3 & immB_mask3)<<5) +((immB4& immB_mask4)<<12)
    print("immB=",immB,"and immB in binary=",bin(immB))


    immU=instruction_word>>12
    immU_mask=0b11111111111111111111
    immU=((immU&immU_mask)<<12)


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
    
    print("-12 =",bin(-12))
    #Generate immS, immB, ImmU, immJ done
    print("opcode here=",bin(opcode))
    inst_type = getInstructionType(opcode)

    immFinal = getFinalImmediate(inst_type, imm,immS,immB,immU,immJ) 

    ALUop = getALUop(inst_type, func3, func7) 

    op2selectMUX(inst_type, rs1, rs2, immFinal)
    BranchTargetSelectMUX(inst_type, immFinal)
    getMemOp(inst_type, opcode)
    ResultSelectMUX(opcode, inst_type)
    isBranchInstruction(opcode, inst_type, func3)

    printOperationDetails(inst_type, immFinal) # Left
    
    # print(inst_type, immFinal, ALUop)
    
    # print(bin(rs1), bin(rs2), bin(rd))


def getFinalImmediate(inst_type, imm,immS, immB, immU, immJ):
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

def getInstructionType(opcode):
    '''Get Type of Instruction from opcode'''
    inst_type = ''
    print("opcode in getinstructiontype=",bin(opcode))
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
    if inst_type=='I':
        if ((func3== 0x0) or  (func3==0x2) or (func3==0x1)):
            ALUop=1
        elif func3== 0x6:
            ALUop=4
        elif func3 == 0x7:
            ALUop=3
    if inst_type=='S':
        ALUop=1
    if inst_type=='B':
        ALUop=2
    if inst_type=='U' or inst_type=='J':
        ALUop=1
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
    
    print("inst_type=", inst_type)
    print("Operand1 is: ",operand1)
    print("ImmFinal is: ", immFinal,"immFinal in binary=",bin(immFinal))   
    print("Write Register rd is: ", rd) 
    print("rs1=",rs1)
    print("opcode in binary=",bin(opcode))
    print("operand2=",operand2)
    

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
    print("EXECUTE")
    global ALUop, ALUResult, BranchTargetAddress

    print()
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
    print("BranchTargetResult=",BranchTargetResult)
    BranchTargetAddress=BranchTargetResult+(pc*4)
    
# Memory access stage
def mem():
    '''
    MemOp operation
    0 - Do nothing (skip)
    1 - Write in memory --> Store
    2 - Read from memory --> Load
    '''
    global MemOp, ReadData, rs2

    print("MEMORY")
    print("MemOp=",MemOp)
    if (MemOp == 0):
        print("There is no Memory Operation")
        ReadData = ALUResult
    elif (MemOp == 1): 
        # Store

        # unsigned int *data_p;
        # data_p = (unsigned int*)(DataMEM + ALUResult);
        data_mem[ALUResult] = register[rs2]
        ReadData = data_mem[ALUResult]
        # int rs2Value = BintoDec(rs2,5);
        # *data_p = X[rs2Value];
        # ReadData = X[rs2Value];
        print("There is a Store Operation to be done from memory")
    elif (MemOp == 2):
        # Load
        # int *data_p;
        # data_p = (int*)(DataMEM + ALUResult);
        # ReadData = *data_p;
        ReadData = data_mem[ALUResult]
        print("There is a Read Operation to be done from memory")

    MemOp = 0

# Write back stage
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
    print("RESULTSELECT",ResultSelect)

    if (RFWrite):
        if (ResultSelect == 0):
            register[rd] =4 * (pc + 1)
            print("Write Back  ", 4*(pc+1), "to R", rd)
        elif (ResultSelect == 1):
            register[rd] = immFinal
            print("Write Back to ", immFinal, "to R", rd)
        elif (ResultSelect == 2):
            register[rd] = pc*4 + immFinal
            print("Write Back to ", immFinal, "to R", rd)
        elif (ResultSelect == 3):
            register[rd] = ReadData
            print("Write Back  ", ReadData, "to R", rd)
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
    print("Isbranch is ",isBranch)
    if (isBranch == 0):
        print("ALUResult=",ALUResult)
        pc = ALUResult
        pc//=4
    elif (isBranch == 1):
        print("BranchTargetAddress=",BranchTargetAddress)
        pc = BranchTargetAddress
        pc//=4
    else:
        pc += 1
    