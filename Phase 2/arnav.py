import sys
import multiprocessing as mp
from multiprocessing import Manager

from helperFunctions import *

# cycle
cycle = 0

MEM = [0] * 4000


isStall = 0
decode_ready = 0
last_decode_done = 0


def fetch(fetch_input, fetch_output, write_output, register, ready_reg, codeExitFlag, fetch3_input):
    """
    Fetch Instruction
    """
    global isStall
    register[0] = 0  # X[0]=0

    # Input from Fetch
    pc = fetch_input["pc"]
    fetch_ready = fetch_input["fetch_ready"]
    MEM = fetch_input["MEM"]
    # decode_ready = fetch_input["decode_ready"]

    # Output from Write Back
    fetch_ready1 = write_output["fetch_ready1"]
    read_pc_from_write = write_output["read_pc_from_write"]
    pc1 = write_output["pc1"]

    # Check if pc is to be read from write back
    if read_pc_from_write == 1:
        print("Read PC FROM WRITEBACK")
        pc = pc1
        fetch3_input[pc] = pc1
        fetch_ready = 1
        fetch_output["decode_ready"] = 1
        write_output["read_pc_from_write"] = 0

    if fetch_ready:
        print()
        print("FETCH")
        print("PC: ", pc)

        # global instruction_word
        instruction_word = read_word(pc, MEM)
        print("Instruction Word", hex(instruction_word))

        # End of program
        if instruction_word == 0xFFFFFFFB:
            codeExitFlag[0] = 1
            print("HERE")
            # fetch_output["pc"] = 0
            # fetch_output["opcode"] = 0
            # fetch_output["rs1"] = 0
            # fetch_output["rs2"] = 0
            # fetch_output["rd"] = 0
            # fetch_output["func3"] = 0
            # fetch_output["func7"] = 0
            # fetch_output["immFinal"] = 0
            # fetch_output["instructionType"] = 0
            # fetch_output["decode_ready"] = 0
            fetch_output["decode_end"] = 1

            return

        # Split instructions from instruction word
        opcode, rs1, rs2, rd, func3, func7, imm, immS, immB, immU, immJ = splitInstruction(instruction_word)

        # Get Instruction Type
        inst_type = getInstructionType(opcode)

        # Get final Immediate
        immFinal = getFinalImmediate(inst_type, imm, immS, immB, immU, immJ)

        # Print Instruction
        printDetails(opcode, immFinal, rs1, rs2, rd, func3, func7, inst_type)

        # set decode_ready to 1, as the current instruction can go to decode
        # decode_ready=1
        global decode_ready
        decode_ready = 1

        # If instruction is not a branch or jump, increment pc --> Edit this for reducing 1 stall
        if (ready_reg[rs1] == 0 and inst_type != "J") or (
            inst_type != "J" and ready_reg[rs2] == 0 and (inst_type == "R" or inst_type == "S" or inst_type == "B")
        ):  # If rs1 or rs2 is not ready and instruction is R, S, or B and not J, stall
            print("INSIDE")
            fetch3_input["fetch_ready"] = 0
            # decode_ready=0
            fetch3_input["pc"] = pc + 1

        else:
            print("OUTSIDE")
            if inst_type != "J" and inst_type != "B" and opcode != 0b1100111:
                fetch3_input["pc"] = pc + 1
            else:
                fetch3_input["pc"] = pc + 1

            # if rd != 0 and inst_type != "S" and inst_type != "B":
            #     ready_reg[rd] = 0

        # # as soon as you meet a register which is non zero and has valid rd, set that rd to not ready
        # if rd != 0 and inst_type != "S" and inst_type != "B":
        #     ready_reg[rd] = 0

        # if both register are ready then do the following
        if (
            (inst_type == "B" or inst_type == "J" or opcode == 0b1100111)
            and (ready_reg[rs1] != 0)
            and ready_reg[rs2] != 0
        ):
            fetch3_input["fetch_ready"] = 0
            write_output["fetch_ready1"] = 0

        # Output to Decode
        fetch_output["pc"] = pc
        fetch_output["opcode"] = opcode
        fetch_output["rs1"] = rs1
        fetch_output["rs2"] = rs2
        fetch_output["rd"] = rd
        fetch_output["func3"] = func3
        fetch_output["func7"] = func7
        fetch_output["immFinal"] = immFinal
        fetch_output["instructionType"] = inst_type
        fetch_output["decode_ready"] = decode_ready
        fetch_output["decode_end"] = 0

        register[0] = 0

    else:
        # If fetch is not ready, output 0s
        print("\nNO FETCH READY")
        print("PC: ", pc)
        # fetch_output["pc"] = 0
        # fetch_output["opcode"] = 0
        # fetch_output["rs1"] = 0
        # fetch_output["rs2"] = 0
        # fetch_output["rd"] = 0
        # fetch_output["func3"] = 0
        # fetch_output["func7"] = 0
        # fetch_output["immFinal"] = 0
        # fetch_output["instructionType"] = 0
        # fetch_output["decode_ready"] = 0
        fetch_output["decode_end"] = 0

        register[0] = 0

    return


def decode(decode_input, decode_output, register, codeExitFlag, ready_reg, fetch_output):
    register[0] = 0

    # Read Inputs from decode
    pc = decode_input["pc"]
    opcode = decode_input["opcode"]
    rs1 = decode_input["rs1"]
    rs2 = decode_input["rs2"]
    rd = decode_input["rd"]
    func3 = decode_input["func3"]
    func7 = decode_input["func7"]
    immFinal = decode_input["immFinal"]
    instructionType = decode_input["instructionType"]
    decode_ready = decode_input["decode_ready"]
    decode_end = decode_input["decode_end"]

    inst_type = instructionType

    # global decode_ready, last_decode_done
    global last_decode_done

    # For Code Exit
    codeExitFlag[1] = decode_end

    print()
    # print("decode_ready: ", decode_ready)
    # Check if decode is ready
    # decode_ready=1
    # print("DECODE Contians: ", decode_input)

    # problem here, this condition is creating problem in case of beq
    #  and other branch instructions, looking at the cycles, the next
    #  PC after a branch instruction gets stuck in fetch for a while.
    #  Need to do something about it look into it,
    # I have tried to fix it as much as possible, still look into it
    # if you can
    if not (last_decode_done) and not (
        (ready_reg[rs1] == 0 and inst_type != "J")
        or (inst_type != "J" and ready_reg[rs2] == 0 and (inst_type == "R" or inst_type == "S" or inst_type == "B"))
    ):
        # print("CAME HEREE", decode_ready, last_decode_done)

        # added this to also check for decode_ready
        if decode_ready and not (last_decode_done):
            print("DECODE")
            print("Ready: rd: ", rd, " rs1 ", rs1, " pc ", pc, " instr: ", inst_type)
            print("lastdecodeone ", last_decode_done)
            print("1: ", (ready_reg[rs1] == 0 and inst_type != "J"))
            print(
                "2: ",
                (inst_type != "J" and ready_reg[rs2] == 0)
                and (inst_type == "R" or inst_type == "S" or inst_type == "B"),
            )
            print(
                "CONDITION: ",
                not (last_decode_done)
                and not (
                    (ready_reg[rs1] == 0 and inst_type != "J")
                    or (
                        inst_type != "J"
                        and ready_reg[rs2] == 0
                        and (inst_type == "R" or inst_type == "S" or inst_type == "B")
                    )
                ),
            )

            # as soon as you meet a register which is non zero and has valid rd, set that rd to not ready
            if rd != 0 and inst_type != "S" and inst_type != "B":
                print("DOING NOT READY")
                ready_reg[rd] = 0

            # Get ALUop, MemOp, RFWrite, ResultSelect, isBranch
            ALUop = getALUop(instructionType, func3, func7)
            operand1, operand2 = op2selectMUX(instructionType, rs1, rs2, immFinal, register)
            BranchTargetSelect = BranchTargetSelectMUX(instructionType, immFinal)
            MemOp = getMemOp(instructionType, opcode)
            RFWrite, ResultSelect = ResultSelectMUX(opcode, instructionType)
            isBranch = isBranchInstruction(opcode, instructionType, func3, operand1, operand2)

            if (
                (inst_type == "B" or inst_type == "J" or opcode == 0b1100111)
                and (ready_reg[rs1] != 0)
                and ready_reg[rs2] != 0
            ):
                fetch_output["decode_ready"] = 0

            if (ready_reg[rs1] == 0 and inst_type != "J") or (
                inst_type != "J" and ready_reg[rs2] == 0 and (inst_type == "R" or inst_type == "S" or inst_type == "B")
            ):  # If rs1 or rs2 is not ready and instruction is R, S, or B and not J, stall
                print("INSIDE")
                fetch_output["decode_ready"] = 0
                # decode_ready=0

            execute_ready = 1

            # Output to Execute
            decode_output["pc"] = pc
            decode_output["ALUop"] = ALUop
            decode_output["BranchTargetResult"] = BranchTargetSelect
            decode_output["ResultSelect"] = ResultSelect
            decode_output["immFinal"] = immFinal
            decode_output["operand1"] = operand1
            decode_output["operand2"] = operand2
            decode_output["rd"] = rd
            decode_output["MemOp"] = MemOp
            decode_output["isBranch"] = isBranch
            decode_output["RFWrite"] = RFWrite
            decode_output["execute_ready"] = execute_ready
            decode_output["rs2"] = rs2
            decode_output["instructionType"] = instructionType
            decode_output["opcode"] = opcode

            register[0] = 0

            if decode_end:
                last_decode_done = 1

        # if decode_ready is not 1, then, we have to check if the
        # instruction type is J, U or jalr, if it is, then we have
        # to set the execute_ready to 0 because once we run the decode
        #  for that jump instruction, in the next cycle, first that
        # jump instruction's execute will run, then decode will run
        # --> will find it's set to not ready, so will also set
        # execute_ready to not ready also.
        # Tried my best to explain what I did here
        else:
            # print("HERE")
            # print("INSTRUCTIONTYPE ", instructionType)

            if instructionType != "S" or instructionType != "R" or instructionType != "I" or instructionType != "U":
                # print("INSIDE")
                decode_output["execute_ready"] = 0
                if decode_end:
                    last_decode_done = 1
    else:
        # If decode is not ready, output 0s
        # set all these values to 0, because of the ready and not ready stuff
        print("\nNO DECODE READY")
        fetch_output["decode_ready"] = 0
        decode_output["pc"] = 0
        decode_output["ALUop"] = 0
        decode_output["BranchTargetResult"] = 0
        decode_output["ResultSelect"] = 0
        decode_output["immFinal"] = 0
        decode_output["operand1"] = 0
        decode_output["operand2"] = 0
        decode_output["rd"] = 0
        decode_output["MemOp"] = 0
        decode_output["isBranch"] = 0
        decode_output["RFWrite"] = 0
        decode_output["execute_ready"] = 0
        decode_output["rs2"] = 0
        decode_output["instructionType"] = "0"
        decode_output["opcode"] = 0

        register[0] = 0

    return


def execute(execute_input, execute_output, register, codeExitFlag):
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

    register[0] = 0

    pc = execute_input["pc"]
    ALUop = execute_input["ALUop"]
    BranchTargetResult = execute_input["BranchTargetResult"]
    ResultSelect = execute_input["ResultSelect"]
    immFinal = execute_input["immFinal"]
    operand1 = execute_input["operand1"]
    operand2 = execute_input["operand2"]
    rd = execute_input["rd"]
    MemOp = execute_input["MemOp"]
    isBranch = execute_input["isBranch"]
    RFWrite = execute_input["RFWrite"]
    execute_ready = execute_input["execute_ready"]
    rs2 = execute_input["rs2"]
    inst_type = execute_input["instructionType"]
    opcode = execute_input["opcode"]

    codeExitFlag[2] = execute_ready

    # ready variable is used to check if the instruction is to be executed or not

    if execute_ready:
        print()
        print("EXECUTE")

        # get ALUResult
        ALUResult = getALUReslt(ALUop, operand1, operand2)

        # Get BranchTargetAddress
        BranchTargetAddress = BranchTargetResult + (pc * 4)
        print("ALUResult is: ", ALUResult)

        # Get memory_ready
        memory_ready = 1

        # Output to Memory
        execute_output["pc"] = pc
        execute_output["MemOp"] = MemOp
        execute_output["ALUResult"] = ALUResult
        execute_output["operand2"] = operand2
        execute_output["RFWrite"] = RFWrite
        execute_output["ResultSelect"] = ResultSelect
        execute_output["rd"] = rd
        execute_output["immFinal"] = immFinal
        execute_output["isBranch"] = isBranch
        execute_output["BranchTargetAddress"] = BranchTargetAddress
        execute_output["memory_ready"] = memory_ready
        execute_output["rs2"] = rs2
        execute_output["instructionType"] = inst_type
        execute_output["opcode"] = opcode

        register[0] = 0

    else:
        print("\nNO EXECUTE")
        # set all these values to 0, because of the ready and not ready stuff
        # If execute is not ready, output 0s
        execute_output["pc"] = 0
        execute_output["MemOp"] = 0
        execute_output["ALUResult"] = 0
        execute_output["operand2"] = 0
        execute_output["RFWrite"] = 0
        execute_output["ResultSelect"] = 0
        execute_output["rd"] = 0
        execute_output["immFinal"] = 0
        execute_output["isBranch"] = 0
        execute_output["BranchTargetAddress"] = 0
        execute_output["memory_ready"] = 0
        execute_output["rs2"] = 0
        execute_output["instructionType"] = "0"
        execute_output["opcode"] = 0

        register[0] = 0

    return


def Memory(memory_input, memory_output, data_mem, register, codeExitFlag):
    """
    MemOp operation
    0 - Do nothing (skip)
    1 - Write in memory --> Store
    2 - Read from memory --> Load
    """

    register[0] = 0

    # Input to Memory
    pc = memory_input["pc"]
    MemOp = memory_input["MemOp"]
    ALUResult = memory_input["ALUResult"]
    operand2 = memory_input["operand2"]
    RFWrite = memory_input["RFWrite"]
    ResultSelect = memory_input["ResultSelect"]
    rd = memory_input["rd"]
    immFinal = memory_input["immFinal"]
    isBranch = memory_input["isBranch"]
    BranchTargetAddress = memory_input["BranchTargetAddress"]
    memory_ready = memory_input["memory_ready"]
    rs2 = memory_input["rs2"]
    inst_type = memory_input["instructionType"]
    opcode = memory_input["opcode"]

    # For exiting the code
    codeExitFlag[3] = memory_ready

    if memory_ready:
        ReadData = 0
        print()
        print("MEMORY")

        if MemOp == 0:
            print("There is no Memory Operation")
            ReadData = ALUResult
        elif MemOp == 1:
            # Store
            print("data_mem[", ALUResult, "]=register[", rs2, "]=", register[rs2])
            data_mem[ALUResult] = register[rs2]
            ReadData = data_mem[ALUResult]

            print("There is a Store Operation to be done to memory and operand2=", operand2)

        elif MemOp == 2:
            ReadData = data_mem.get(ALUResult, 0)

            print("There is a Read Operation to be done from memory")
            print("ReadData=data_mem[", ALUResult, "]")

        MemOp = 0
        write_ready = 1

        # Output to WriteBack
        memory_output["pc"] = pc
        memory_output["RFWrite"] = RFWrite
        memory_output["ResultSelect"] = ResultSelect
        memory_output["rd"] = rd
        memory_output["immFinal"] = immFinal
        memory_output["ReadData"] = ReadData
        memory_output["ALUResult"] = ALUResult
        memory_output["isBranch"] = isBranch
        memory_output["BranchTargetAddress"] = BranchTargetAddress
        memory_output["write_ready"] = write_ready
        memory_output["instructionType"] = inst_type
        memory_output["opcode"] = opcode

        register[0] = 0

    else:
        print("\nNO MEMORY READY")
        # If memory is not ready, output 0s
        # set all these values to 0, because of the ready and not ready stuff
        memory_output["pc"] = 0
        memory_output["RFWrite"] = 0
        memory_output["ResultSelect"] = 0
        memory_output["rd"] = 0
        memory_output["immFinal"] = 0
        memory_output["ReadData"] = 0
        memory_output["ALUResult"] = 0
        memory_output["isBranch"] = 0
        memory_output["BranchTargetAddress"] = 0
        memory_output["write_ready"] = 0
        memory_output["instructionType"] = "0"
        memory_output["opcode"] = 0

        register[0] = 0

    return


def Write(
    write_input,
    write_output,
    register,
    fetch3_input,
    ready_reg,
    decode_input,
    execute_input,
    memory_input,
    globalCounter,
    codeExitFlag,
    fetch_output,
):
    """
    ResultSelect
    5 - None
    0 - PC+4
    1 - ImmU_lui
    2 - ImmU_auipc
    3 - LoadData - essentially same as ReadData
    4 - ALUResult
    """

    register[0] = 0

    # Input to Write
    pc = write_input["pc"]
    RFWrite = write_input["RFWrite"]
    ResultSelect = write_input["ResultSelect"]
    rd = write_input["rd"]
    immFinal = write_input["immFinal"]
    ReadData = write_input["ReadData"]
    ALUResult = write_input["ALUResult"]
    isBranch = write_input["isBranch"]
    BranchTargetAddress = write_input["BranchTargetAddress"]
    write_ready = write_input["write_ready"]
    inst_type = write_input["instructionType"]
    opcode = write_input["opcode"]

    # For exiting the code
    codeExitFlag[4] = write_ready

    if write_ready:
        print("WRITE BACK IS DONE, globalCounter = ", globalCounter, "#########################################")

        globalCounter += 1

        write_output["fetch_ready1"] = 1

        print()
        print("WRITEBACK")

        if RFWrite:
            if ResultSelect == 0:
                register[rd] = 4 * (pc + 1)
                print("Write Back  ", 4 * (pc + 1), "to R", rd)
            elif ResultSelect == 1:
                register[rd] = immFinal
                print("Write Back to ", immFinal, "to R", rd)
            elif ResultSelect == 2:
                register[rd] = pc * 4 + immFinal
                print("Write Back to ", immFinal, "to R", rd)
            elif ResultSelect == 3:
                register[rd] = ReadData
                print("Write Back  ", ReadData, "to R", rd)
            elif ResultSelect == 4:
                register[rd] = ALUResult
                print("Write Back to ", ALUResult, "to R", rd)

            ready_reg[rd] = 1

            # check if the instruction is jalr, or branch, or jal, then don't set fetch_ready to 1, else set to 1
            #
            if (
                decode_input["instructionType"] != "J"
                and decode_input["instructionType"] != "B"
                and execute_input["instructionType"] != "J"
                and execute_input["instructionType"] != "B"
                and memory_input["instructionType"] != "J"
                and memory_input["instructionType"] != "B"
                and write_input["instructionType"] != "J"
                and write_input["instructionType"] != "B"
                and decode_input["opcode"] != 0b1100111
                and execute_input["opcode"] != 0b1100111
                and memory_input["opcode"] != 0b1100111
                and write_input["opcode"] != 0b1100111
            ):
                # now we want to make fetch_ready = 1 whenever
                # we know that a real register in `fetch_output` is not in use
                # we have feeded the data of fetch into the pipe/output of
                # fetch and stored it there, so that we can get rid of the
                # extra stall, this fetch_output == decode_input
                DecodeRS1 = decode_input["rs1"]
                DecodeRS2 = decode_input["rs2"]

                print("DecodeRS1 ", DecodeRS1, " DecodeRS2 ", DecodeRS2)
                if ready_reg[DecodeRS2] and ready_reg[DecodeRS1]:
                    # since dependency is resolved, we can start fetch
                    print("YASSSssss")
                    fetch3_input["fetch_ready"] = 1
                    fetch_output["decode_ready"] = 1

        else:
            print("There is no Write Back")

        """
            IsBranch=0 => ALUResult
            =1         => BranchTargetAddress
            =2         => pc+4(default)
        """

        print("Isbranch is =", isBranch)

        if isBranch == 0:
            print("ALUResult=", ALUResult)
            pc = ALUResult
            pc //= 4
            write_output["read_pc_from_write"] = 1
            fetch3_input["fetch_ready"] = 1
            fetch_output["decode_ready"] = 0

        elif isBranch == 1:
            print("BranchTargetAddress=", BranchTargetAddress)
            pc = BranchTargetAddress
            pc //= 4
            write_output["read_pc_from_write"] = 1
            fetch3_input["fetch_ready"] = 1
            fetch_output["decode_ready"] = 0
            fetch3_input["pc"] = pc

        else:
            pc += 1

            # print("Decode ready is ", fetch_output["decode_ready"])

            if fetch3_input["fetch_ready"] == 0 and (
                inst_type == "J" or inst_type == "B"
            ):  # ie if fetch is waiting and it is not the end
                # out5.append(1) # this is to tell that fetch should take pc from write_back
                write_output["read_pc_from_write"] = 1
                fetch3_input["fetch_ready"] = 1
                fetch_output["decode_ready"] = 0
                # print("HEY")

            elif inst_type == "I" and opcode == 0b0000011:
                # Load type instruction
                print("Load type instruction")
                fetch_output["decode_ready"] = 1
            else:
                write_output["read_pc_from_write"] = 0

            # added this here, because we have to give the most updated pc
            # to the next fetch instead of fetching the current instruction.
            # I hope you understand what I mean ~ yashasav
            # fetch3_input["pc"]=pc

        print("fetch ", fetch3_input["fetch_ready"])
        print("new PC is =", pc)
        write_output["pc1"] = pc
        register[0] = 0

    else:
        print("\nNO WRITE READY")
        write_output["fetch_ready1"] = 1
        # fetch_output["decode_ready"]=1
        write_output["read_pc_from_write"] = 0
        write_output["pc1"] = 0
        register[0] = 0

    print("Decode Ready ", fetch_output["decode_ready"])
    print("Fetch Ready ", fetch3_input["fetch_ready"])

    return


def run_riscvsim():
    global cycle

    fetch_ready = 1
    decode_ready = 0
    execute_ready = 0
    memory_ready = 0
    write_ready = 0
    read_pc_from_write = 0  # 1-> read pc from write

    pc = 0
    opcode = 0
    rs1 = 0
    rs2 = 0
    rd = 0
    func3 = 0
    func7 = 0
    immFinal = 0
    instructionType = 0
    ALUop = 0
    BranchTargetResult = 0
    ResultSelect = 0
    operand1 = 0
    operand2 = 0
    MemOp = 0
    isBranch = 0
    RFWrite = 0
    ALUResult = 0
    BranchTargetAddress = 0
    ReadData = 0
    fetch_ready1 = 0
    pc1 = 0
    decode_end = 0

    globalCounter = 0

    codeExitFlag = [0, 1, 1, 1, 1]

    # register = mp.Array("i", 32, lock=False)  # All 32 Registers
    # data_mem = mp.Array("i", 1000000000, lock=False)  # Data Memory as Array

    register = [0] * 32
    # data_mem = [0] * 1000000000
    data_mem = {}

    """
        Ready Bit
        1 -> Ready
        0 -> Not Ready
    """
    # ready_reg = mp.Array("i", 32, lock=False)  # Showing if rd Ready to be Read
    ready_reg = []

    for i in range(32):
        ready_reg.append(1)

    fetch_input = {"pc": pc, "fetch_ready": fetch_ready, "MEM": MEM, "decode_ready": decode_ready}
    decode_input = {  # if (
        #     codeExitFlag[0] == 1
        #     and codeExitFlag[1] == 0
        #     and codeExitFlag[2] == 0
        #     and codeExitFlag[3] == 0
        #     and codeExitFlag[4] == 0
        # ):
        #     print("<<<<<<<<<<<<<<---------------EXITING--------------------->>>>>>>>>>>>>>>>")
        #     break
        "pc": pc,
        "opcode": opcode,
        "rs1": rs1,
        "rs2": rs2,
        "rd": rd,
        "func3": func3,
        "func7": func7,
        "immFinal": immFinal,
        "instructionType": instructionType,
        "decode_ready": decode_ready,
        "decode_end": decode_end,
    }

    execute_input = {
        "pc": pc,
        "ALUop": ALUop,
        "BranchTargetResult": BranchTargetResult,
        "ResultSelect": ResultSelect,
        "immFinal": immFinal,
        "operand1": operand1,
        "operand2": operand2,
        "rd": rd,
        "MemOp": MemOp,
        "isBranch": isBranch,
        "RFWrite": RFWrite,
        "execute_ready": execute_ready,
        "rs2": rs2,
        "instructionType": instructionType,
        "opcode": opcode,
    }

    memory_input = {
        "pc": pc,
        "MemOp": MemOp,
        "ALUResult": ALUResult,
        "operand2": operand2,
        "RFWrite": RFWrite,
        "ResultSelect": ResultSelect,
        "rd": rd,
        "immFinal": immFinal,
        "ReadData": ReadData,
        "isBranch": isBranch,
        "BranchTargetAddress": BranchTargetAddress,
        "memory_ready": memory_ready,
        "rs2": rs2,
        "instructionType": instructionType,
        "opcode": opcode,
    }

    write_input = {
        "pc": pc,
        "RFWrite": RFWrite,
        "ResultSelect": ResultSelect,
        "rd": rd,
        "immFinal": immFinal,
        "ReadData": ReadData,
        "ALUResult": ALUResult,
        "isBranch": isBranch,
        "BranchTargetAddress": BranchTargetAddress,
        "write_ready": write_ready,
        "rs2": rs2,
        "instructionType": instructionType,
        "opcode": opcode,
    }

    fetch_output = {
        "pc": pc,
        "opcode": opcode,
        "rs1": rs1,
        "rs2": rs2,
        "rd": rd,
        "func3": func3,
        "func7": func7,
        "immFinal": immFinal,
        "instructionType": instructionType,
        "decode_ready": decode_ready,
        "decode_end": decode_end,
    }

    decode_output = {
        "pc": pc,
        "ALUop": ALUop,
        "BranchTargetResult": BranchTargetResult,
        "ResultSelect": ResultSelect,
        "immFinal": immFinal,
        "operand1": operand1,
        "operand2": operand2,
        "rd": rd,
        "MemOp": MemOp,
        "isBranch": isBranch,
        "RFWrite": RFWrite,
        "execute_ready": execute_ready,
        "rs2": rs2,
        "instructionType": instructionType,
        "opcode": opcode,
    }

    execute_output = {
        "pc": pc,
        "MemOp": MemOp,
        "ALUResult": ALUResult,
        "operand2": operand2,
        "RFWrite": RFWrite,
        "ResultSelect": ResultSelect,
        "rd": rd,
        "immFinal": immFinal,
        "ReadData": ReadData,
        "isBranch": isBranch,
        "BranchTargetAddress": BranchTargetAddress,
        "memory_ready": memory_ready,
        "rs2": rs2,
        "instructionType": instructionType,
        "opcode": opcode,
    }

    memory_output = {
        "pc": pc,
        "RFWrite": RFWrite,
        "ResultSelect": ResultSelect,
        "rd": rd,
        "immFinal": immFinal,
        "ReadData": ReadData,
        "ALUResult": ALUResult,
        "isBranch": isBranch,
        "BranchTargetAddress": BranchTargetAddress,
        "write_ready": write_ready,
        "rs2": rs2,
        "instructionType": instructionType,
        "opcode": opcode,
    }

    write_output = {"fetch_ready1": fetch_ready1, "read_pc_from_write": read_pc_from_write, "pc1": pc1}

    fetch2_input = {"fetch_ready1": fetch_ready1, "read_pc_from_write": read_pc_from_write, "pc1": pc1}
    fetch3_input = {"pc": pc, "fetch_ready": fetch_ready, "MEM": MEM, "decode_ready": decode_ready}

    while cycle < 198:
        print("CYCLE: ", cycle)

        # call for every cycle
        if cycle == 0:  # if cycle is 0, start from beginning
            fetch(fetch_input, fetch_output, fetch2_input, register, ready_reg, codeExitFlag, fetch3_input)
            cycle += 1
        elif cycle == 1:  # 1 instruction
            decode(decode_input, decode_output, register, codeExitFlag, ready_reg, fetch_output)
            fetch(fetch_input, fetch_output, fetch2_input, register, ready_reg, codeExitFlag, fetch3_input)
            cycle += 1
        elif cycle == 2:  # 2 instruction
            execute(execute_input, execute_output, register, codeExitFlag)
            decode(decode_input, decode_output, register, codeExitFlag, ready_reg, fetch_output)
            fetch(fetch_input, fetch_output, fetch2_input, register, ready_reg, codeExitFlag, fetch3_input)
            cycle += 1
        elif cycle == 3:  # 3 instruction
            Memory(memory_input, memory_output, data_mem, register, codeExitFlag)
            execute(execute_input, execute_output, register, codeExitFlag)
            decode(decode_input, decode_output, register, codeExitFlag, ready_reg, fetch_output)
            fetch(fetch_input, fetch_output, fetch2_input, register, ready_reg, codeExitFlag, fetch3_input)
            cycle += 1
        elif cycle >= 4:  # 4 or more than 4 instructions, then keep looping in this fashion
            Write(
                write_input,
                write_output,
                register,
                fetch3_input,
                ready_reg,
                decode_input,
                execute_input,
                memory_input,
                globalCounter,
                codeExitFlag,
                fetch_output,
            )
            Memory(memory_input, memory_output, data_mem, register, codeExitFlag)
            execute(execute_input, execute_output, register, codeExitFlag)
            decode(decode_input, decode_output, register, codeExitFlag, ready_reg, fetch_output)
            fetch(fetch_input, fetch_output, fetch2_input, register, ready_reg, codeExitFlag, fetch3_input)
            cycle += 1

        print("register: ", register)
        print("ready: ", ready_reg)

        print("Code Exit Flag: ", codeExitFlag)
        print("Last Decode Done: ", last_decode_done)

        if (
            codeExitFlag[0] == 1
            and codeExitFlag[1] == 1
            and codeExitFlag[2] == 0
            and codeExitFlag[3] == 0
            and codeExitFlag[4] == 0
            and last_decode_done == 1
        ):
            print("<<<<<<<<<<<<<<---------------EXITING--------------------->>>>>>>>>>>>>>>>")
            break

        print("-------------------------------------------------------")

        makeDictEqual(fetch_output, decode_input)
        makeDictEqual(decode_output, execute_input)
        makeDictEqual(execute_output, memory_input)
        makeDictEqual(memory_output, write_input)
        makeDictEqual(write_output, fetch2_input)
        makeDictEqual(fetch3_input, fetch_input)

    # for i in range(100):
    #     print("Cycle No.", i + 1)

    #     fetch(fetch_input, fetch_output, fetch2_input, register, ready_reg, codeExitFlag)
    #     decode(decode_input, decode_output, register, codeExitFlag, ready_reg)
    #     execute(execute_input, execute_output, register, codeExitFlag)
    #     Memory(memory_input, memory_output, data_mem, register, codeExitFlag)
    #     Write(write_input, write_output, register, fetch_input, ready_reg, decode_input, execute_input, memory_input, globalCounter, codeExitFlag, fetch_output)

    # print("register: ", register)
    # print("ready: ", ready_reg)

    # print()
    # print("Fetch out: ", fetch_output)
    # print("Decode 2: ", decode_output)
    # print("Execute 3: ", execute_output)
    # print("Out 4: ", memory_output)
    # print("Out 5: ", write_output)

    # print("CodeExit: ", codeExitFlag, last_decode_done)

    # if (
    #     codeExitFlag[0] == 1
    #     and codeExitFlag[1] == 1
    #     and codeExitFlag[2] == 0
    #     and codeExitFlag[3] == 0
    #     and codeExitFlag[4] == 1
    #     and last_decode_done == 1
    # ):
    #     print("<<<<<<<<<<<<<<---------------EXITING--------------------->>>>>>>>>>>>>>>>")
    #     break

    # print("-------------------------------------------------------")

    # makeDictEqual(fetch_output, decode_input)
    # makeDictEqual(decode_output, execute_input)
    # makeDictEqual(execute_output, memory_input)
    # makeDictEqual(memory_output, write_input)
    # makeDictEqual(write_output, fetch2_input)

    print("Register: ", register[:])

    # Print data memory
    # print("Data Memory: ", data_mem)
    print_data_mem(data_mem)
