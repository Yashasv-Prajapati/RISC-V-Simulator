import sys
from helperFunctions import *
import multiprocessing as mp
from multiprocessing import Manager

MEM = [0] * 4000



def fetch(fetch_input, fetch_output, write_output, register, ready_reg, codeExitFlag, TotalCycles, decode_input):
    """
    Fetch Instruction
    """
    register[0] = 0  # X[0]=0

    # Input from Fetch
    pc = fetch_input["pc"]
    fetch_ready = fetch_input["fetch_ready"]
    MEM = fetch_input["MEM"]
    decode_ready = fetch_input["decode_ready"]
    end_fetched = fetch_input["end_fetched"]

    # Output from Write Back
    fetch_ready1 = write_output["fetch_ready1"]
    read_pc_from_write = write_output["read_pc_from_write"]
    pc1 = write_output["pc1"]

    # Check if pc is to be read from write back
    if read_pc_from_write == 1:
        print("HERE")
        pc = pc1
        fetch_input[pc] = pc1
        fetch_ready = 1
        write_output["read_pc_from_write"] = 0

    # print("register values are: ", register[:])

    # print("fetch_ready=",fetch_ready)
    if fetch_ready and end_fetched == 0:
        print("FETCH")
        print("PC: ", pc)

        # global instruction_word
        instruction_word = read_word(pc, MEM)
        print("instruction_word in fetch after read_Word=", hex(instruction_word))

        if instruction_word == 0xFFFFFFFB:
            codeExitFlag[0] = 1
            # print("ENDDDDDDD  pc>0xfffffffb")
            fetch_output["pc"] = 0
            fetch_output["opcode"] = 0
            fetch_output["rs1"] = 0
            fetch_output["rs2"] = 0
            fetch_output["rd"] = 0
            fetch_output["func3"] = 0
            fetch_output["func7"] = 0
            fetch_output["immFinal"] = 0
            fetch_output["instructionType"] = 0
            fetch_output["decode_ready"] = 0
            fetch_output["end_fetched"] = 1

            return

        opcode, rs1, rs2, rd, func3, func7, imm, immS, immB, immU, immJ = splitInstruction(instruction_word)

        inst_type = getInstructionType(opcode)
        print("Instruction type is: ", inst_type)

        immFinal = getFinalImmediate(inst_type, imm, immS, immB, immU, immJ)
        print("Final immediate in FETCH is: ", immFinal, " in hex: ", hex(immFinal))
        print("rd is = ", rd, "rs1 in FETCH is=", rs1, "and rs2 in FETCH is=", rs2)
        decode_ready = 1

        if (ready_reg[rs1] == 0 and inst_type != "J") or (
            inst_type != "J" and ready_reg[rs2] == 0 and (inst_type == "R" or inst_type == "S" or inst_type == "B")
        ):
            if decode_input["decode_ready"] == 1:
                print("Yupp")
                TotalCycles[0] = TotalCycles[0] - 1

            decode_ready = 0
            print('"YES"')
            fetch_input["fetch_ready"] = 1
            fetch_input["pc"] = pc
        else:
            decode_ready = 1
            if inst_type != "J" and inst_type != "B" and opcode != 0b1100111:
                fetch_input["pc"] = pc + 1
            else:
                fetch_input["pc"] = pc
            if rd != 0 and inst_type != "S" and inst_type != "B":
                ready_reg[rd] = 0

        if (
            (inst_type == "B" or inst_type == "J" or opcode == 0b1100111)
            and (ready_reg[rs1] != 0)
            and ready_reg[rs2] != 0
        ):
            fetch_input["fetch_ready"] = 0
            # extra_pipe[0]=0
            write_output["fetch_ready1"] = 0

        print("ready_reg ", ready_reg[:])

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
        fetch_output["end_fetched"] = end_fetched

        register[0] = 0
        return

    else:
        fetch_output["pc"] = 0
        fetch_output["opcode"] = 0
        fetch_output["rs1"] = 0
        fetch_output["rs2"] = 0
        fetch_output["rd"] = 0
        fetch_output["func3"] = 0
        fetch_output["func7"] = 0
        fetch_output["immFinal"] = 0
        fetch_output["instructionType"] = 0
        fetch_output["decode_ready"] = 0
        fetch_output["end_fetched"] = end_fetched

        register[0] = 0
        return


def decode(decode_input, decode_output, register, codeExitFlag):
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
    end_fetched = decode_input["end_fetched"]

    codeExitFlag[1] = decode_ready

    if decode_ready:
        print("\nDECODE")
        ALUop = getALUop(instructionType, func3, func7)
        operand1, operand2 = op2selectMUX(instructionType, rs1, rs2, immFinal, register)
        BranchTargetSelect = BranchTargetSelectMUX(instructionType, immFinal)
        MemOp = getMemOp(instructionType, opcode)
        RFWrite, ResultSelect = ResultSelectMUX(opcode, instructionType)
        isBranch = isBranchInstruction(opcode, instructionType, func3, operand1, operand2)

        # printing operation details
        printOperationDetails(instructionType, immFinal, operand1, operand2, rd, ALUop)  # this is not required

        execute_ready = 1

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
        decode_output["end_fetched"] = end_fetched
        decode_output["instructionType"] = instructionType
        decode_output["opcode"] = opcode

        register[0] = 0

        return
    else:
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
        decode_output["end_fetched"] = end_fetched
        decode_output["instructionType"] = "0"
        decode_output["opcode"] = 0

        register[0] = 0

        return

        # EXECUTE


def execute(execute_input, execute_output, register, codeExitFlag):
    register[0] = 0
    # destructure arguments

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
    end_fetched = execute_input["end_fetched"]
    inst_type = execute_input["instructionType"]
    opcode = execute_input["opcode"]

    codeExitFlag[2] = execute_ready

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
    # ready variable is used to check if the instruction is to be executed or not

    if execute_ready:
        print()
        print("EXECUTE")
        ALUResult = 0

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

        BranchTargetAddress = BranchTargetResult + (pc * 4)
        print("ALUResult is: ", ALUResult)

        memory_ready = 1

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
        execute_output["end_fetched"] = end_fetched
        execute_output["instructionType"] = inst_type
        execute_output["opcode"] = opcode

        register[0] = 0

        return
    else:
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
        execute_output["end_fetched"] = end_fetched
        execute_output["instructionType"] = "0"
        execute_output["opcode"] = 0

        register[0] = 0

        return

        # MEMORY


def Memory(memory_input, memory_output, data_mem, register, codeExitFlag):
    register[0] = 0

    # destructure arguments
    # pc, MemOp, ALUResult, operand2, RFWrite, ResultSelect, rd, immFinal, isBranch, BranchTargetAddress, mem_ready,rs2,end_fetched,inst_type,opcode = pipe4

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
    end_fetched = memory_input["end_fetched"]
    inst_type = memory_input["instructionType"]
    opcode = memory_input["opcode"]

    codeExitFlag[3] = memory_ready

    """
    MemOp operation
    0 - Do nothing (skip)
    1 - Write in memory --> Store
    2 - Read from memory --> Load
    """

    if memory_ready:
        ReadData = 0

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
            ReadData = data_mem[ALUResult]

            print("There is a Read Operation to be done from memory")
            print("ReadData=data_mem[", ALUResult, "]")

        MemOp = 0
        write_ready = 1

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
        memory_output["end_fetched"] = end_fetched
        memory_output["instructionType"] = inst_type
        memory_output["opcode"] = opcode

        register[0] = 0

        return
    else:
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
        memory_output["end_fetched"] = end_fetched
        memory_output["instructionType"] = "0"
        memory_output["opcode"] = 0

        register[0] = 0

        return

        # WRITE


def Write(
    write_input,
    write_output,
    register,
    fetch_input,
    ready_reg,
    decode_input,
    execute_input,
    memory_input,
    globalCounter,
    codeExitFlag,
):
    register[0] = 0
    # destructure arguments
    # pc, RFWrite, ResultSelect, rd, immFinal, ReadData, ALUResult, isBranch, BranchTargetAddress, write_ready,end_fetched,inst_type,opcode = pipe5

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
    end_fetched = write_input["end_fetched"]
    inst_type = write_input["instructionType"]
    opcode = write_input["opcode"]

    codeExitFlag[4] = write_ready

    """
        ResultSelect
        5 - None
        0 - PC+4
        1 - ImmU_lui
        2 - ImmU_auipc
        3 - LoadData - essentially same as ReadData
        4 - ALUResult
    """

    if write_ready:
        print("WRITE BACK IS DONE, globalCounter = ", globalCounter[:], "#########################################")

        globalCounter[0] += 1

        write_output["fetch_ready1"] = 1

        print("WRITEBACK ")
        print("RESULTSELECT=", ResultSelect)

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

            if (
                decode_input["instructionType"] != "J"
                and decode_input["instructionType"] != "B"
                and execute_input["instructionType"] != "J"
                and execute_input["instructionType"] != "B"
                and memory_input["instructionType"] != "J"
                and memory_input["instructionType"] != "B"
                and write_input["instructionType"] != "J"
                and write_input["instructionType"] != "B"
                and decode_input["opcode"] == 0b1100111
                and execute_input["opcode"] != 0b1100111
                and memory_input["opcode"] != 0b1100111
                and write_input["opcode"] != 0b1100111
            ):
                fetch_input["fetch_ready"] = 1

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
            # out5.append(1)
            write_output["read_pc_from_write"] = 1
            fetch_input["fetch_ready"] = 1

        elif isBranch == 1:
            print("BranchTargetAddress=", BranchTargetAddress)
            pc = BranchTargetAddress
            pc //= 4
            # out5.append(1)
            write_output["read_pc_from_write"] = 1
            fetch_input["fetch_ready"] = 1

        else:
            pc += 1

            if (
                fetch_input["fetch_ready"] == 0 and end_fetched == 0 and (inst_type == "J" or inst_type == "B")
            ):  # ie if fetch is waiting and it is not the end
                # out5.append(1) # this is to tell that fetch should take pc from write_back
                write_output["read_pc_from_write"] = 1
                fetch_input["fetch_ready"] = 1

            else:
                # out5.append(0)
                write_output["read_pc_from_write"] = 0

        print("new PC is =", pc)
        write_output["pc1"] = pc
        # out5.append(pc)
        register[0] = 0

        return

    else:
        if end_fetched == 1:
            # for i in range(3):
            #     out5.append(0)
            write_output["fetch_ready1"] = 0
            write_output["read_pc_from_write"] = 0
            write_output["pc1"] = 0

        else:
            write_output["fetch_ready1"] = 1
            write_output["read_pc_from_write"] = 0
            write_output["pc1"] = 0
            # out5.append(1)
            # out5.append(0)
            # out5.append(0)          # this is useless
        register[0] = 0

        return



def run_riscvsim():
    with Manager() as manager:
        process_list = []

        fetch_ready = 1
        decode_ready = 0
        execute_ready = 0
        memory_ready = 0
        write_ready = 0
        end_fetched = 0  # 1 -> end has been fetched
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

        globalCounter = mp.Array("i", 1, lock=False)

        TotalCycles = mp.Array("i", 1, lock=False)  # Count of Total No. of Cycles
        TotalCycles[0] = 0  # Initially Total Cycles=0

        codeExitFlag = mp.Array("i", 5, lock=False)  # For Exiting Program
        for i in range(5):
            codeExitFlag[i] = 1
        codeExitFlag[0] = 0

        register = mp.Array("i", 32, lock=False)  # All 32 Registers
        data_mem = mp.Array("i", 1000000000, lock=False)  # Data Memory as Array

        """
                Ready Bit
                1 -> Ready
                0 -> Not Ready
         """
        ready_reg = mp.Array("i", 32, lock=False)  # Showing if rd Ready to be Read

        for i in range(32):
            ready_reg[i] = 1

        fetch_input = manager.dict(
            {"pc": pc, "fetch_ready": fetch_ready, "MEM": MEM, "decode_ready": decode_ready, "end_fetched": end_fetched}
        )
        decode_input = manager.dict(
            {
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
                "end_fetched": end_fetched,
            }
        )
        execute_input = manager.dict(
            {
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
                "end_fetched": end_fetched,
                "instructionType": instructionType,
                "opcode": opcode,
            }
        )
        memory_input = manager.dict(
            {
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
                "end_fetched": end_fetched,
                "instructionType": instructionType,
                "opcode": opcode,
            }
        )
        write_input = manager.dict(
            {
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
                "end_fetched": end_fetched,
                "instructionType": instructionType,
                "opcode": opcode,
            }
        )

        fetch_output = manager.dict(
            {
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
                "end_fetched": end_fetched,
            }
        )
        decode_output = manager.dict(
            {
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
                "end_fetched": end_fetched,
                "instructionType": instructionType,
                "opcode": opcode,
            }
        )
        execute_output = manager.dict(
            {
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
                "end_fetched": end_fetched,
                "instructionType": instructionType,
                "opcode": opcode,
            }
        )
        memory_output = manager.dict(
            {
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
                "end_fetched": end_fetched,
                "instructionType": instructionType,
                "opcode": opcode,
            }
        )
        write_output = manager.dict(
            {"fetch_ready1": fetch_ready1, "read_pc_from_write": read_pc_from_write, "pc1": pc1}
        )

        fetch2_input = manager.dict(
            {"pc": pc, "fetch_ready": fetch_ready, "MEM": MEM, "decode_ready": decode_ready, "end_fetched": end_fetched}
        )

        # out5 = manager.list()

        for i in range(100000000):
            print("Cycle No.", i + 1)
            p1 = mp.Process(
                target=fetch,
                args=(
                    fetch_input,
                    fetch_output,
                    fetch2_input,
                    register,
                    ready_reg,
                    codeExitFlag,
                    TotalCycles,
                    decode_input,
                ),
            )
            p2 = mp.Process(target=decode, args=(decode_input, decode_output, register, codeExitFlag))
            p3 = mp.Process(target=execute, args=(execute_input, execute_output, register, codeExitFlag))
            p4 = mp.Process(target=Memory, args=(memory_input, memory_output, data_mem, register, codeExitFlag))
            p5 = mp.Process(
                target=Write,
                args=(
                    write_input,
                    write_output,
                    register,
                    fetch_input,
                    ready_reg,
                    decode_input,
                    execute_input,
                    memory_input,
                    globalCounter,
                    codeExitFlag,
                ),
            )

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

            # print()
            # print("Fetch out: ", fetch_output)
            # print("Decode 2: ", decode_output)
            # print("Execute 3: ", execute_output)
            # print("Out 4: ", memory_output)
            # print("Out 5: ", write_output)

            if (
                codeExitFlag[0] == 1
                and codeExitFlag[1] == 0
                and codeExitFlag[2] == 0
                and codeExitFlag[3] == 0
                and codeExitFlag[4] == 0
            ):
                print("<<<<<<<<<<<<<<---------------EXITING--------------------->>>>>>>>>>>>>>>>")
                break

            TotalCycles[0] += 1  # Incrementing Total Cycles

            print("-------------------------------------------------------")

            decode_input = manager.dict()
            execute_input = manager.dict()
            memory_input = manager.dict()
            write_input = manager.dict()
            fetch2_input = manager.dict()

            makeDictEqual(fetch_output, decode_input)
            makeDictEqual(decode_output, execute_input)
            makeDictEqual(execute_output, memory_input)
            makeDictEqual(memory_output, write_input)
            makeDictEqual(write_output, fetch2_input)
            # extra_pipe=out5

            fetch_output = manager.dict()
            decode_output = manager.dict()
            execute_output = manager.dict()
            memory_output = manager.dict()
            write_output = manager.dict()
            # out5 = manager.list()

        print("Register: ", register[:])

        # Print data memory
        print_data_mem(data_mem)
        

