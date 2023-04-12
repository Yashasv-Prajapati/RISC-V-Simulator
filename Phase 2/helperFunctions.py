def makeDictEqual(dict1, dict2):
    """Make 2 dictionaries equal"""
    for key in dict1:
        dict2[key] = dict1[key]


def write_word(address, instruction, MEM):
    """
    Write Word
    """
    index = address / 4
    MEM[int(index)] = instruction


def read_word(address, MEM):
    """
    Read Word
    """

    return MEM[(address)]


# Decode helper functions


def splitInstruction(instruction_word):
    opcode_mask = 0b1111111
    opcode = instruction_word & opcode_mask

    # find first  source register
    rs1 = instruction_word
    rs1 = rs1 >> 15
    rs1_mask = 0b11111
    rs1 = rs1 & rs1_mask
    # print("rs1: ", rs1)

    # find second source register
    rs2 = instruction_word
    rs2 = rs2 >> 20
    rs2_mask = 0b11111
    rs2 = rs2 & rs2_mask

    # find destination register
    rd = instruction_word
    rd = rd >> 7
    rd_mask = 0b11111
    rd = rd & rd_mask
    # print("rd: ", rd)

    # find func3
    func3 = instruction_word
    func3 = func3 >> 12
    func3_mask = 0b111
    func3 = func3 & func3_mask

    # find func7
    func7 = instruction_word
    func7 = func7 >> 25
    func7_mask = 0b1111111
    func7 = func7 & func7_mask

    # generate Immediate --> space left intentionally

    imm = instruction_word
    imm = imm >> 20
    imm_mask = 0b111111111111
    imm = imm & imm_mask

    immS = instruction_word
    immS1 = immS >> 7
    immS2 = immS >> 25
    immS_mask1 = 0b11111
    immS_mask2 = 0b1111111
    immS = (immS1 & immS_mask1) + ((immS2 & immS_mask2) << 5)

    # IMM B Generation
    immB = instruction_word
    immB1 = instruction_word >> 7
    immB_mask1 = 0b1  # for 11th
    immB2 = instruction_word >> 7
    immB_mask2 = 0b11110
    immB3 = instruction_word >> 25
    immB_mask3 = 0b111111
    immB4 = instruction_word >> 31
    immB_mask4 = 0b1  # for 12th
    immB = (
        ((immB1 & immB_mask1) << 11)
        + ((immB2 & immB_mask2))
        + ((immB3 & immB_mask3) << 5)
        + ((immB4 & immB_mask4) << 12)
    )

    immU = instruction_word >> 12
    immU_mask = 0b11111111111111111111
    immU = (immU & immU_mask) << 12

    immJ = instruction_word
    immJ1 = instruction_word >> 12
    immJ_mask1 = 0b11111111
    immJ2 = instruction_word >> 20
    immJ_mask2 = 0b1
    immJ3 = instruction_word >> 21
    immJ_mask3 = 0b1111111111
    immJ4 = instruction_word >> 31
    immJ_mask4 = 0b1
    immJ = (
        ((immJ1 & immJ_mask1) << 12)
        + ((immJ2 & immJ_mask2) << 11)
        + ((immJ3 & immJ_mask3) << 1)
        + ((immJ4 & immJ_mask4) << 20)
    )

    return opcode, rs1, rs2, rd, func3, func7, imm, immS, immB, immU, immJ


def getFinalImmediate(inst_type, imm, immS, immB, immU, immJ):
    immFinal = 0
    if inst_type == "I":
        immFinal = imm
        if (immFinal >> 11) == 1:
            immFinal = immFinal - 4096
    if inst_type == "S":
        immFinal = immS
        if (immFinal >> 11) == 1:
            immFinal = immFinal - 4096
    if inst_type == "B":
        immFinal = immB
        if (immFinal >> 12) == 1:
            immFinal = immFinal - 8192
    if inst_type == "U":
        immFinal = immU
    if inst_type == "J":
        immFinal = immJ
        if (immFinal >> 20) == 1:
            immFinal = immFinal - 2097152
    return immFinal


def getInstructionType(opcode):
    """Get Type of Instruction from opcode"""
    inst_type = ""
    if opcode == 0b0110011:
        inst_type = "R"
    elif opcode == 0b0010011 or opcode == 0b0000011 or opcode == 0b1100111:
        inst_type = "I"
    elif opcode == 0b0100011:
        inst_type = "S"
    elif opcode == 0b1100011:
        inst_type = "B"
    elif opcode == 0b0110111:
        inst_type = "U"
    elif opcode == 0b1101111:
        inst_type = "J"
    else:
        print("Not valid instruction type Detected")
        sys.exit(1)

    return inst_type


def BranchTargetSelectMUX(inst_type, imm_final):
    """
    Branch Target Select MUX
    """

    BranchTargetResult = imm_final

    return BranchTargetResult


def getMemOp(instType, opcode):
    """
    Get Mem Op
    """
    if instType == "S":
        MemOp = 1
    elif opcode == 0b0000011:
        MemOp = 2
    else:
        MemOp = 0

    return MemOp


def ResultSelectMUX(opcode, inst_type):
    """
    ResultSelect
    5 - None
    0 - PC+4
    1 - ImmU_lui
    2 - ImmU_auipc
    3 - LoadData - essentially same as ReadData
    4 - ALUResult
    """

    RFWrite = 0
    ResultSelect = None

    if opcode == 0b0110111:
        ResultSelect = 1
        RFWrite = 1
    elif opcode == 0b0010111:
        ResultSelect = 2
        RFWrite = 1
    elif opcode == 0b1101111 or opcode == 0b1100111:
        ResultSelect = 0
        RFWrite = 1
    elif opcode == 0b0000011:
        ResultSelect = 3
        RFWrite = 1
    elif opcode == 0b0100011 or inst_type == "B":
        RFWrite = 0
        ResultSelect = 5
    else:
        ResultSelect = 4
        RFWrite = 1

    return RFWrite, ResultSelect


def isBranchInstruction(opcode, inst_type, func3, operand1, operand2):
    """
    Check weather the condition is a branch instruction
    IsBranch=0 => ALUResult
    =1         => BranchTargetAddress
    =2         => pc+4(default)
    """
    print("operand1=", operand1, "and operand2=", operand2)
    if opcode == 0b1100111:
        isBranch = 0
    elif inst_type == "B":
        isBranch = 2
        if func3 == 0x0 and operand1 == operand2:
            print("operand1==operand2 because operand1=", operand1, " and operand2=", operand2)
            isBranch = 1
        elif func3 == 0x1 and operand1 != operand2:
            isBranch = 1
        elif func3 == 0x4 and operand1 < operand2:
            isBranch = 1
        elif func3 == 0x5 and operand1 >= operand2:
            isBranch = 1
    elif inst_type == "J":
        isBranch = 1
    else:
        isBranch = 2

    return isBranch


def getALUop(inst_type, func3, func7):
    """
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
    """
    ALUop = 0

    if inst_type == "R":
        if func3 == 0x0:
            if func7 == 0x0:
                ALUop = 1
            elif func7 == 0x20:
                ALUop = 2

        elif func3 == 0x4:
            ALUop = 7
        elif func3 == 0x6:
            ALUop = 4
        elif func3 == 0x7:
            ALUop = 3
        elif func3 == 0x1:
            ALUop = 5
        elif func3 == 0x5:
            ALUop = 6
    elif inst_type == "I":
        if func3 == 0x0:
            ALUop = 1
        elif func3 == 0x7:
            ALUop = 3
    if inst_type == "I":
        if (func3 == 0x0) or (func3 == 0x2) or (func3 == 0x1):
            ALUop = 1
        elif func3 == 0x6:
            ALUop = 4
        elif func3 == 0x7:
            ALUop = 3
    if inst_type == "S":
        ALUop = 1
    if inst_type == "B":
        ALUop = 2
    if inst_type == "U" or inst_type == "J":
        ALUop = 1

    return ALUop


# def printOperationDetails(inst_type, immFinal, operand1, operand2, rd, ALUop):
#     """
#     Print Operation Details
#     """
#     print("inst_type in DECODE=", inst_type)
#     if inst_type == "R":
#         if ALUop == 1:
#             print("Instruction Type is ADD")
#         elif ALUop == 3:
#             print("Instruction Type is AND")

#         print("Operands are: ", operand1, operand2)
#         print("Write Register is: ", rd)
#     elif inst_type == "I":
#         if ALUop == 1:
#             print("Instruction Type is ADDI")
#         elif ALUop == 3:
#             print("Instruction Type is ANDI")
#         print("Operand1 is: ", operand1)
#         print("Immediate is: ", immFinal)
#         print("Write Register(rd) is: ", rd)
#     elif inst_type == "S":
#         print("Decode has Store instruction!")
#         print("immFinal in DECODE=", immFinal, "and operand1 in DECODE=", operand1, "and operand2 in DECODE=", operand2)


def print_data_mem(data_mem):
    for i in range(0, 1000000000):
        if data_mem[i] != 0:
            print("data_mem[", i, "]=", data_mem[i])


def reset_proc():
    pass


def load_program_memory(file, MEM):
    """
    Load program Memory
    """
    f = open(file, "r")

    for line in f.readlines():
        address, instruction = line.split()

        address = int(address, 16)
        instruction = int(instruction, 16)

        write_word(address, instruction, MEM)

    f.close()


def op2selectMUX(inst_type, rs1, rs2, imm_final, register):
    """
    Op2SelectMUX
    """
    # global operand1, operand2
    operand1 = register[rs1]
    if inst_type == "S" or inst_type == "I":
        operand2 = imm_final
    else:
        operand2 = register[rs2]

    return operand1, operand2


def printDetails(opcode, immFinal, rs1, rs2, rd, func3, func7, inst_type):  # To be Completed
    """
    Print Details
    """
    if inst_type == "R":
        if func3 == 0x0 and func7 == 0x00:
            print("ADD ", rd, " ", rs1, " ", rs2)
        elif func3 == 0x0 and func7 == 0x20:
            print("SUB ", rd, " ", rs1, " ", rs2)
        elif func3 == 0x4:
            print("XOR ", rd, " ", rs1, " ", rs2)
        elif func3 == 0x6:
            print("OR ", rd, " ", rs1, " ", rs2)
        elif func3 == 0x7:
            print("AND ", rd, " ", rs1, " ", rs2)
        elif func3 == 0x1:
            print("SLL ", rd, " ", rs1, " ", rs2)
        elif func3 == 0x5:
            print("SRL ", rd, " ", rs1, " ", rs2)
        elif func3 == 0x5 and func7 == 0x20:
            print("SRA ", rd, " ", rs1, " ", rs2)
        elif func3 == 0x2:
            print("SLT ", rd, " ", rs1, " ", rs2)

    elif inst_type == "I" and opcode == 0b0010011:
        if func3 == 0x0:
            print("ADDI ", rd, " ", rs1, " ", immFinal)
        elif func3 == 0x7:
            print("ANDI ", rd, " ", rs1, " ", immFinal)
        elif func3 == 0x6:
            print("ORI ", rd, " ", rs1, " ", immFinal)

    elif inst_type == "I" and opcode == 0b0000011:
        if func3 == 0x0:
            print("LB ", rd, " ", rs1, " ", immFinal)
        elif func3 == 0x1:
            print("LH ", rd, " ", rs1, " ", immFinal)
        elif func3 == 0x2:
            print("LW ", rd, " ", rs1, " ", immFinal)

    elif inst_type == "S":
        if func3 == 0x0:
            print("SB ", rs1, " ", rs2, " ", immFinal)
        elif func3 == 0x1:
            print("SH ", rs1, " ", rs2, " ", immFinal)
        elif func3 == 0x2:
            print("SW ", rs1, " ", rs2, " ", immFinal)

    elif inst_type == "B":
        if func3 == 0x0:
            print("BEQ ", rs1, " ", rs2, " ", immFinal)
        elif func3 == 0x1:
            print("BNE ", rs1, " ", rs2, " ", immFinal)
        elif func3 == 0x4:
            print("BLT ", rs1, " ", rs2, " ", immFinal)
        elif func3 == 0x5:
            print("BGE ", rs1, " ", rs2, " ", immFinal)

    elif inst_type == "U" and opcode == 0b0110111:
        print("LUI ", rd, " ", immFinal)

    elif inst_type == "U" and opcode == 0b0010111:
        print("AUIPC ", rd, " ", immFinal)

    elif inst_type == "J":
        print("JAL ", rd, " ", immFinal)


def getALUReslt(ALUop, operand1, operand2):
    if ALUop == 1:
        ALUResult = operand1 + operand2
    elif ALUop == 2:
        ALUResult = operand1 - operand2
    elif ALUop == 3:
        ALUResult = operand1 & operand2
    elif ALUop == 4:
        ALUResult = operand1 | operand2
    elif ALUop == 5:
        ALUResult = operand1 << operand2
    elif ALUop == 6:
        ALUResult = operand1 >> operand2
    elif ALUop == 7:
        ALUResult = operand1 ^ operand2
    elif ALUop == 8:
        ALUResult = 1 if (operand1 < operand2) else 0
