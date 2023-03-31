import multiprocessing as mp
import time
from multiprocessing import Manager
import sys
import os



register = [0] * 32


# MEM = [0] * 4000
# data_mem = [0] * 100000000

preparation_status = {
    # 1 - Ready
    # 0 - Not Ready
    'pc': 1,
    'instruction_word': 1,
    'rs2':1,
}

stage1 = {
    'pc': 0,
}

# dictionary for the fetch-decode stage
stage2 = {
    'instruction_word': 0,
    'pc':0,
}

# dictionary for the decode-execute stage
stage3 = {
    'operand1':0,
    'operand2':0,
    'inst_type':'R',
    'immFinal':0,
    'pc':0,
    'rs2':0,
    'rd':0,
}

# dictionary for the execute-memory stage
stage4 = {
    'inst_type':'R',
    'ALUResult':0,
    'rs2':0,
    'immFinal': 0,
    'rd': 0,

}

# dictionary for the memory-writeback stage
stage5 = {
    'inst_type':'R',
    'ReadData':0,
    'rd': 0,
    'immFinal': 0,
    'ALUResult':0,
}

stage6={
    'ALUResult':0,
}

# creating 4 dictionaries for each stage
# dictionary for the fetch stage

registerCheck = [1 for i in range(32)]
print("registerCheck= ")
print(registerCheck)    
# functions to be made----> fetch, decode, execute, memory, writeback


'''

Ready Bit
1 -> Ready
0 -> Not Ready

'''

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



def fetch(args):
    # destructure variables
    counter, pc, ready, MEM = args

    time.sleep(2)
    print("Fetch", counter[0])

    '''
        Fetch Instruction
    '''
    # global instruction_word

    # local_pc=stage1['pc']
    stage2['instruction_word'] = read_word(pc, MEM)
    stage2['pc']=stage1['pc']
    
    local_instruction_word=stage2['instruction_word']
    opcode_mask = 0b1111111
    opcode = local_instruction_word & opcode_mask

    # find first  source register
    rs1 = local_instruction_word
    rs1 = rs1 >> 15
    rs1_mask = 0b11111
    rs1 = rs1 & rs1_mask

    # find second source register
    rs2 = local_instruction_word
    rs2 = rs2 >> 20
    rs2_mask = 0b11111
    rs2 = rs2 & rs2_mask

    # find destination register
    rd = local_instruction_word
    rd = rd >> 7
    rd_mask = 0b11111
    rd = rd & rd_mask

    # find func3
    func3 = local_instruction_word
    func3 = func3 >> 12
    func3_mask = 0b111
    func3 = func3 & func3_mask

    # find func7
    func7 = local_instruction_word
    func7 = func7 >> 25
    func7_mask = 0b1111111
    func7 = func7 & func7_mask

    # generate Immediate --> space left intentionally








    # get instruction type
    instructionType = getInstructionType(opcode)

    if(instructionType=='S' or instructionType=='B'):
        # do nothing
        None
    else:
        # set ready bit
        ready[rd]=0

    # also return immFinal
    return [rs1, rs2, rd, func3, func7, ready, instructionType]

    
    

    # counter[0] += 1
def decode(args):

    # destructure arguments
    counter,opcode, pc, rs1, rs2, rd, func3, func7, ready, immFinal, instructionType = args
    
    time.sleep(1.5)
    print("Decode", counter[1])
    counter[1] += 1

    ALUop = getALUop(instructionType, func3, func7)  
    operand1, operand2 = op2selectMUX(instructionType, rs1, rs2, immFinal)
    BranchTargetSelect = BranchTargetSelectMUX(instructionType, immFinal) #this is left
    MemOp = getMemOp(instructionType, opcode)
    ResultSelect = ResultSelectMUX(opcode, instructionType)
    isBranch = isBranchInstruction(opcode, instructionType, func3)
    
    # printing operation details
    printOperationDetails(instructionType, immFinal) # this is not required
    
    return [ALUop, ready, immFinal, operand1, operand2, rd, BranchTargetSelect, MemOp, ResultSelect, isBranch, ready, pc]

    
def execute(args):

    # destructure arguments
    ALUop, BranchTargetResult,ResultSelect, immFinal, operand1, operand2, ready, pc, rd, MemOp, isBranch, chalo = args

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

    # chalo variable is used to check if the instruction is to be executed or not

    if (chalo):
        print("EXECUTE")
        ALUResult = 0
        
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

        # print("ALUResult: ", ALUResult)
        # print("BranchTargetResult=",BranchTargetResult)
        BranchTargetAddress=BranchTargetResult+(pc*4)

        return [BranchTargetAddress, ALUResult, pc, MemOp, isBranch, MemOp, ALUResult, pc, ResultSelect, rd, immFinal, isBranch, BranchTargetResult, ready]


    
def Memory(args):

    # destructure arguments
    MemOp, ALUResult, data_mem, rs2, pc, RFWrite, ResultSelect, rd, immFinal, ReadData, isBranch, BranchTargetAddress, chalo, ready = args

    '''
    MemOp operation
    0 - Do nothing (skip)
    1 - Write in memory --> Store
    2 - Read from memory --> Load
    '''
    if (chalo):
        ReadData = 0

        print("MEMORY")

        if (MemOp == 0):
            print("There is no Memory Operation")
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
            print("There is a Store Operation to be done from memory")
        elif (MemOp == 2):
            # Load
            # int *data_p;
            # data_p = (int*)(DataMEM + ALUResult);
            # ReadData = *data_p;
            ReadData = data_mem[ALUResult]
            print("There is a Read Operation to be done from memory")

        MemOp = 0

        return [RFWrite, pc, ResultSelect, rd, immFinal, ReadData, ALUResult, isBranch, BranchTargetAddress, ready]
    
def Write(args):

    # destructure arguments
    RFWrite, pc, ResultSelect, rd, immFinal, ReadData, ALUResult, isBranch, BranchTargetAddress, ready, chalo = args

    '''
        ResultSelect
        5 - None
        0 - PC+4
        1 - ImmU_lui
        2 - ImmU_auipc
        3 - LoadData - essentially same as ReadData
        4 - ALUResult
    '''

    if (chalo):
        print("WRITEBACK ")

        print("RESULTSELECT",ResultSelect)

        if (RFWrite):
            if (ResultSelect == 0):
                register[rd] = pc + 1
                print("Write Back to ", pc+1, "to R", rd)
            elif (ResultSelect == 1):
                register[rd] = immFinal
                print("Write Back to ", immFinal, "to R", rd)
            elif (ResultSelect == 2):
                register[rd] = pc + immFinal
                print("Write Back to ", immFinal, "to R", rd)
            elif (ResultSelect == 3):
                register[rd] = ReadData
                print("Write Back to ", ReadData, "to R", rd)
            elif (ResultSelect == 4):
                register[rd] = ALUResult
                print("Write Back to ", ALUResult, "to R", rd)
        else:
            print("There is no Write Back")

        '''
            IsBranch=0 => ALUResult
            =1         => BranchTargetAddress
            =2         => pc+4(default)
        '''

        print("Isbranch is ",isBranch)
        if (isBranch == 0):
            print("ALUResult=",ALUResult)
            pc = ALUResult
        elif (isBranch == 1):
            print("BranchTargetAddress=",BranchTargetAddress)
            pc = BranchTargetAddress
            pc//=4
        else:
            pc += 1

        return pc, chalo, ready


def op2selectMUX(inst_type, rs1, rs2, imm_final):
    '''
        Op2SelectMUX
    '''
    # global operand1, operand2
    operand1 = register[rs1]
    if (inst_type == 'S' or inst_type == 'I'):
        operand2 = imm_final
    else:
        operand2 = register[rs2]
    
    return operand1, operand2

    
    
if __name__ == "__main__":
    
    with Manager() as manager:

        process_list = []

        # for i in range(10):
        #     p =  mp.Process(target= fetch(counter))
        #     p.start()
        #     process_list.append(p)
        # p1 =  mp.Process(target= fetch, args=[counter])

        l = manager.list([0]*5)

        load_program_memory(file, MEM)
                
        for i in range(3):
            p1 =  mp.Process(target= fetch, args=[l])
            p2 =  mp.Process(target= decode, args=[l])
            p3 =  mp.Process(target= execute, args=[l])
            p4 =  mp.Process(target= Memory, args=[l])
            p5 =  mp.Process(target= Write, args=[l])
            
            p1.start()
            p2.start()
            p3.start()
            p4.start()
            p5.start()

            process_list.append(p1)
            process_list.append(p2)
            process_list.append(p3)
            process_list.append(p4)
            process_list.append(p5)

            for process in process_list:
                process.join()
            print("---------------")



# fetch helper functions


def write_word(address, instruction, MEM):
    '''
        Write Word
    '''
    index = address/4
    MEM[int(index)] = instruction

def read_word(address, mem):
    '''
        Read Word
    '''
    print("address=",address,"MEM[address]=",MEM[address])
    
    return MEM[(address)]


# decode helper functions

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


def BranchTargetSelectMUX(inst_type, imm_final):
    '''
        Branch Target Select MUX
    '''

    BranchTargetResult = imm_final

    return BranchTargetResult

def getMemOp(instType, opcode):
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
    else:
        ResultSelect = 4
        RFWrite = 1

    return RFWrite, ResultSelect

def isBranchInstruction(opcode, inst_type, func3, operand1, operand2):
    '''
        Check weather the condition is a branch instruction

        IsBranch=0 => ALUResult
        =1         => BranchTargetAddress
        =2         => pc+4(default)
    '''

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

    return isBranch


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


def printOperationDetails(inst_type, immFinal, operand1, operand2, rd, ALUop):
    '''
        Print Operation Details
    '''

    if (inst_type == 'R'):
        if (ALUop == 1):
            print("Instruction Type is ADD")
        elif (ALUop == 3):
            print("Instruction Type is AND")

        print("Operands are: ", operand1, operand2)
        print("Write Register is: ", rd)
    elif (inst_type == 'I'):
        if (ALUop == 1):
            print("Instruction Type is ADDI")
        elif (ALUop == 3):
            print("Instruction Type is ANDI")

        print("Operand is: ", operand1)
        print("Immediate is: ", immFinal)
        print("Write Register is: ", rd)
