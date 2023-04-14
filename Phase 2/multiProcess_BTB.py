import multiprocessing as mp
import time
from multiprocessing import Manager
import sys
import os

MEM = [0] * 4000

def reset_proc():
    pass

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


                                                            #FETCH
def fetch(pipe1, out1,extra_pipe,register, ready_reg, out_stall, codeExitFlag,TotalCycles,pipe2,btbTable1,btbTable2,ExitFlag):
    '''
        Fetch Instruction
    '''
    register[0]=0                   #X[0]=0
    # destructure variables
    pc, fetch_ready, MEM, decode_ready ,end_fetched= pipe1
    fetch_ready1,read_pc_from_write,pc1=extra_pipe


    if(read_pc_from_write==1):
        print("HERE")
        pc=pc1
        pipe1[0]=pc1
        fetch_ready=1
        extra_pipe[1]=0
    

    print("register values are: ", register[:])

    print("fetch_ready=",fetch_ready)
    if (fetch_ready and end_fetched==0):
        print("FETCH")
        print("PC: ", pc)

        if(pc>=0xfffffffb):
            # print("ENDDDDDDD  pc>0xfffffffb")
            for _ in range(10):
                out1.append(0)
            out1.append(1)                                  #pipe2 ka end_fetched=1
            return
    
        # global instruction_word
        instruction_word = read_word(pc, MEM)
        print("instruction_word in fetch after read_Word=",hex(instruction_word))
        print("instruction word in binary=",bin(instruction_word))

        if (instruction_word == 0xfffffffb):
            codeExitFlag[0] = 1
            ExitFlag[0]+=1
            # print("ENDDDDDDD  pc>0xfffffffb")
            for _ in range(10):
                out1.append(0)
            out1.append(1)#pipe2 ka end_fetched=1
            return 
        
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
        

        print("opcode here=",bin(opcode))
        inst_type = getInstructionType(opcode)
        print("Instruction type is: ",inst_type)

        immFinal = getFinalImmediate(inst_type, imm, immS ,immB, immU, immJ) 
        print("Final immediate in FETCH is: ",immFinal, " in hex: ", hex(immFinal))
        print("rd is = ", rd,"rs1 in FETCH is=",rs1,"and rs2 in FETCH is=",rs2)
        # decode_ready = 1

        # pipe1[0]=pc+1
        flag=0
        if ((ready_reg[rs1] == 0 and inst_type!='J')or ( inst_type!='J' and ready_reg[rs2] == 0 and (inst_type=='R' or inst_type=='S' or inst_type=='B'))):
            #Branch with dependency will also come inside this
            if(pipe2[-2]==1):    #if decode_ready==1
                print("Yupp")
                TotalCycles[0]=TotalCycles[0]-1

            decode_ready = 0
            print('"YES"')
            pipe1[1] = 1       #fetch_ready=1     
            pipe1[0] = pc      #pc to be fetched=pc
        
        else:
            decode_ready = 1
            if(inst_type!='J' and inst_type!='B' and opcode!=0b1100111): 
                pipe1[0] = pc + 1
            else:
                #branch without dependency
                pipe1[0]=pc

            if(rd!=0 and inst_type!='S' and inst_type!='B'):
                print("rd=0 done")
                if(ready_reg[rd]==1 and opcode==0b1100111):
                    print("CAME")
                    flag=1
                ready_reg[rd] = 0
        
        
        if(((inst_type=='B' or inst_type=='J' or opcode==0b1100111) and (ready_reg[rs1]!=0) and ready_reg[rs2]!=0)  or flag==1 ):
            #branch without dependency
            pipe1[1]=1                          #fetch_ready=0
            extra_pipe[0]=1                     #fetch_ready from write_back=0
            if pc in btbTable1:
                if(btbTable1[pc]==1):  #if branch taken
                    pipe1[0]=btbTable2[pc]
                else:
                    pipe1[0]=pc+1        #branch not taken
            else:
                print("YESDKDKD")
                # btbTable[pc]=[0,pc+1]
                btbTable1[pc]=0
                btbTable2[pc]=pc+1
                print("btbTable1[pc]=",btbTable1[pc],"btbTable2[pc]=",btbTable2[pc])
                pipe1[0]=pc+1
                   

        
        print("ready_reg ",ready_reg[:])

        out1.append(pc)
        out1.append(opcode)
        out1.append(rs1)
        out1.append(rs2)
        out1.append(rd)
        out1.append(func3)
        out1.append(func7)
        out1.append(immFinal)
        out1.append(inst_type)
        out1.append(decode_ready)
        out1.append(end_fetched)


        register[0]=0
        return 

    else:
        for _ in range(10):
            out1.append(0)
        out1.append(end_fetched)
        register[0]=0
        return
        



                                                        #DECODE
def decode(pipe2, out2, register, codeExitFlag):

    register[0] = 0

    # destructure arguments
    pc, opcode, rs1, rs2, rd, func3, func7, immFinal, instructionType, decode_ready,end_fetched = pipe2
    
    codeExitFlag[1] = decode_ready

    if (decode_ready):
        print("\nDECODE")
        ALUop = getALUop(instructionType, func3, func7)  
        operand1, operand2 = op2selectMUX(instructionType, rs1, rs2, immFinal, register)
        BranchTargetSelect = BranchTargetSelectMUX(instructionType, immFinal) 
        MemOp = getMemOp(instructionType, opcode)
        RFWrite, ResultSelect = ResultSelectMUX(opcode, instructionType)
        isBranch = isBranchInstruction(opcode, instructionType, func3, operand1, operand2)
        
        # printing operation details
        printOperationDetails(instructionType, immFinal, operand1, operand2, rd, ALUop) # this is not required
        
        execute_ready = 1

        out2.append(pc)
        out2.append(ALUop)
        out2.append(BranchTargetSelect)
        out2.append(ResultSelect)
        out2.append(immFinal)
        out2.append(operand1)
        out2.append(operand2)
        out2.append(rd)
        out2.append(MemOp)
        out2.append(isBranch)
        out2.append(RFWrite)
        out2.append(execute_ready)
        out2.append(rs2)
        out2.append(end_fetched)
        out2.append(instructionType)
        out2.append(opcode)
        print("YEA")
        register[0]=0

        return
    else:

        for i in range(13):
            out2.append(0)
        out2.append(end_fetched)
        out2.append('0')
        out2.append(0)

        register[0] = 0

        return

                                                                #EXECUTE    
def execute(pipe3, out3,register, codeExitFlag,btbTable1,pipe1,out1,out2,pipe2,ready_reg,btbTable2):
    register[0] = 0
    # destructure arguments
    pc, ALUop, BranchTargetResult, ResultSelect, immFinal, operand1, operand2, rd, MemOp, isBranch, RFWrite, execute_ready,rs2,end_fetched,inst_type,opcode = pipe3

    codeExitFlag[2] = execute_ready

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
    # ready variable is used to check if the instruction is to be executed or not

    if (execute_ready):
        print()
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

        BranchTargetAddress=BranchTargetResult+(pc*4)
        print("ALUResult is: ", ALUResult)

        memory_ready = 1

        out3.append(pc)
        out3.append(MemOp)
        out3.append(ALUResult)
        out3.append(operand2)
        out3.append(RFWrite)
        out3.append(ResultSelect)
        out3.append(rd)
        out3.append(immFinal)
        out3.append(isBranch)
        out3.append(BranchTargetAddress)
        out3.append(memory_ready)
        out3.append(rs2)
        out3.append(end_fetched)
        out3.append(inst_type)
        out3.append(opcode)

        if (inst_type == 'B' or inst_type == 'J' or opcode == 0b1100111):
            print("HERE1")
            if (isBranch == 2):  # this means branch is not taken
                if (btbTable1[pc] == 1):  # but btb said to take branch
                    btbTable1[pc] = 0
                    btbTable2[pc] = pc+1
                    # btbTable[pc] = [0, pc+1]
                    pipe1[0] = pc+1
                    pipe1[1] = 1
                    ready_reg[out2[7]]=1
                    for i in range(13):
                        out2[i]=0
                    out2[13]=end_fetched
                    out2[14]='0'
                    out2[15]=0
                    ready_reg[out1[4]]=1
                    for i in range(10):
                        out1[i]=0
                    out1[10]=end_fetched


            else:  # Branch should be taken
                print("HERE2")
                if (btbTable1[pc] == 0 or btbTable2[pc]!=((int)(ALUResult/4))):  # but btb said not to branch
                    print("HERE3")
                    btbTable1[pc] = 1
                    if (opcode == 0b1100111):
                        btbTable2[pc] =((int) (ALUResult/4))
                        pipe1[0] = (int)(ALUResult/4)
                        pipe1[1] = 1
                    else:
                        print("HERE4")
                        btbTable2[pc] =((int) (BranchTargetAddress/4))
                        pipe1[0] = (int)(BranchTargetAddress/4)
                        pipe1[1] = 1
                    print("out2[7]=",out2[7])
                    ready_reg[out2[7]]=1
                    for i in range(13):
                        out2[i] = 0
                    out2[13]=end_fetched
                    out2[14]='0'
                    out2[15]=0
                    ready_reg[out1[4]]=1
                    for i in range(10):
                        out1[i]=0
                    out1[10]=end_fetched

        print("YO")
        register[0]=0

        return 
    else:

        for i in range(12):
            out3.append(0)
        out3.append(end_fetched)
        out3.append('0')
        out3.append(0)

        register[0] = 0

        return    



                                                            #MEMORY    
def Memory(pipe4, out4, data_mem,register, codeExitFlag):
    register[0] = 0
    # destructure arguments
    pc, MemOp, ALUResult, operand2, RFWrite, ResultSelect, rd, immFinal, isBranch, BranchTargetAddress, mem_ready,rs2,end_fetched,inst_type,opcode = pipe4
    
    codeExitFlag[3] = mem_ready

    '''
    MemOp operation
    0 - Do nothing (skip)
    1 - Write in memory --> Store
    2 - Read from memory --> Load
    '''

    if (mem_ready):

        ReadData = 0

        print("MEMORY")

        if (MemOp == 0):
            print("There is no Memory Operation")
            ReadData = ALUResult
        elif (MemOp == 1): 

            # Store
            print("data_mem[",ALUResult,"]=register[",rs2,"]=",register[rs2])
            data_mem[ALUResult] = register[rs2]
            ReadData = data_mem[ALUResult]

            print("There is a Store Operation to be done to memory and operand2=",operand2)

        elif (MemOp == 2):

            ReadData = data_mem[ALUResult]

            print("There is a Read Operation to be done from memory")
            print("ReadData=data_mem[",ALUResult,"]")


        MemOp = 0
        write_ready = 1

        out4.append(pc)
        out4.append(RFWrite)
        out4.append(ResultSelect)
        out4.append(rd)
        out4.append(immFinal)
        out4.append(ReadData)
        out4.append(ALUResult)
        out4.append(isBranch)
        out4.append(BranchTargetAddress)
        out4.append(write_ready)
        out4.append(end_fetched)
        out4.append(inst_type)
        out4.append(opcode)

        register[0] = 0

        return
    else:

        for i in range(10):
            out4.append(0)
        out4.append(end_fetched)
        out4.append('0')
        out4.append(0)

        register[0] = 0

        return
    
                                                        #WRITE    
def Write(pipe5, out5, register,pipe1, ready_reg,pipe2,pipe3,pipe4, globalCounter, codeExitFlag):
    
    register[0] = 0
    # destructure arguments
    pc, RFWrite, ResultSelect, rd, immFinal, ReadData, ALUResult, isBranch, BranchTargetAddress, write_ready,end_fetched,inst_type,opcode = pipe5

    codeExitFlag[4] = write_ready

    '''
        ResultSelect
        5 - None
        0 - PC+4
        1 - ImmU_lui
        2 - ImmU_auipc
        3 - LoadData - essentially same as ReadData
        4 - ALUResult
    '''

    if (write_ready):

        print("WRITE BACK IS DONE, globalCounter = ",globalCounter[:], "#########################################" )
        
        globalCounter[0]+=1 

        out5.append(1)

        print("WRITEBACK ")
        print("RESULTSELECT=",ResultSelect)


        if (RFWrite):
            if (ResultSelect == 0):
                register[rd] = 4 * (pc + 1)
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
            
            ready_reg[rd] = 1
            print("Rd=1 Done")

            if(pipe2[8]!='J' and pipe2[8]!='B' and pipe3[14]!='J' and pipe3[14]!='B' and pipe4[13]!='J' and pipe4[13]!='B' and pipe5[11]!='J' and pipe5[11]!='B' and pipe2[1]==0b1100111 and pipe3[-1]!=0b1100111 and pipe4[-1]!=0b1100111 and pipe5[-1]!=0b1100111):
                pipe1[1]=1 #fetch_ready'
                #Non Branch Instruction

        else:
            print("There is no Write Back")

        '''
            IsBranch=0 => ALUResult
            =1         => BranchTargetAddress
            =2         => pc+4(default)
        '''

        print("Isbranch is =",isBranch)

        if (isBranch == 0):
            print("ALUResult=",ALUResult)
            pc = ALUResult
            pc//=4
            out5.append(0)
            pipe1[1]=1

        elif (isBranch == 1):
            print("BranchTargetAddress=",BranchTargetAddress)
            pc = BranchTargetAddress
            pc//=4
            out5.append(0)
            pipe1[1]=1

        else:
            pc += 1

            if(pipe1[1]==0 and end_fetched==0 and (inst_type=='J' or inst_type=='B')):# ie if fetch is waiting and it is not the end
                out5.append(0) # this is to tell that fetch should take pc from write_back
                pipe1[1]=1

            else:
                out5.append(0) 
        print("new PC is =", pc)
        out5.append(pc)
        
        register[0] = 0

        return
    
    else:
    
        if(end_fetched==1):
            for i in range(3):
                out5.append(0)

        else:
            out5.append(1)
            out5.append(0)
            out5.append(0)          # this is useless
        register[0] = 0

        return


def op2selectMUX(inst_type, rs1, rs2, imm_final, register):
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

    
    
def run_riscvsim():
    
    with Manager() as manager:

        process_list = []


        fetch_ready = 1
        decode_ready = 0
        execute_ready = 0
        mem_ready = 0
        write_ready = 0
        end_fetched=0                                           # 1 -> end has been fetched
        read_pc_from_write=0                                    # 1-> read pc from write

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

        # BTB dictionary
        btbTable1 = manager.dict()    #Contains taken or not taken value
        btbTable2= manager.dict()     #Contains predicted pc value
        #   0-> NT    1->T


        globalCounter = mp.Array('i', 1, lock=False)
        
        TotalCycles=mp.Array('i',1,lock=False)               #Count of Total No. of Cycles
        TotalCycles[0]=0                                     #Initially Total Cycles=0

        codeExitFlag = mp.Array('i', 5, lock=False)          #For Exiting Program
        ExitFlag=mp.Array('i',1,lock=False)
        ExitFlag[0]=0
        for i in range(5):                         
            codeExitFlag[i] = 1
        codeExitFlag[0] = 0

        register = mp.Array('i', 32, lock=False)             #All 32 Registers
        data_mem = mp.Array('i', 10000000, lock=False)     #Data Memory as Array

        '''
                Ready Bit
                1 -> Ready
                0 -> Not Ready
         '''
        ready_reg = mp.Array('i', 32, lock=False)                    #Showing if rd Ready to be Read

        for i in range(32):
            ready_reg[i] = 1

        pipe1 = manager.list([pc, fetch_ready, MEM, decode_ready,end_fetched])
        pipe2 = manager.list([pc, opcode, rs1, rs2, rd, func3, func7, immFinal, instructionType, decode_ready,end_fetched])
        pipe3 = manager.list([pc, ALUop, BranchTargetResult, ResultSelect, immFinal, operand1, operand2, rd, MemOp, isBranch, RFWrite, execute_ready,rs2,end_fetched,instructionType, opcode])
        pipe4 = manager.list([pc, MemOp, ALUResult, operand2, RFWrite, ResultSelect, rd, immFinal, isBranch, BranchTargetAddress, mem_ready,rs2,end_fetched,instructionType, opcode])
        pipe5 = manager.list([pc, RFWrite, ResultSelect, rd, immFinal, ReadData, ALUResult, isBranch, BranchTargetAddress, write_ready,end_fetched,instructionType, opcode])
        extra_pipe=manager.list([fetch_ready,read_pc_from_write,pc])

        out1 = manager.list()
        out2 = manager.list()
        out3 = manager.list()
        out4 = manager.list()
        out5 = manager.list()
        out_stall = manager.list()



        for i in range(1500):
        
            print("Cycle No.",i+1)
            p1 =  mp.Process(target= fetch, args=(pipe1, out1,extra_pipe,register, ready_reg, out_stall, codeExitFlag,TotalCycles,pipe2,btbTable1,btbTable2,ExitFlag))
            p2 =  mp.Process(target= decode, args=(pipe2, out2, register, codeExitFlag))
            p3 =  mp.Process(target= execute, args=(pipe3, out3,register, codeExitFlag,btbTable1,pipe1,out1,out2,pipe2,ready_reg,btbTable2))
            p4 =  mp.Process(target= Memory, args=(pipe4, out4, data_mem, register, codeExitFlag))
            p5 =  mp.Process(target= Write, args=(pipe5, out5, register,pipe1, ready_reg,pipe2,pipe3,pipe4, globalCounter, codeExitFlag))
            
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
            print()
            print("Out 1: ", out1)
            print("Out 2: ", out2)
            print("Out 3: ", out3)
            print("Out 4: ", out4)
            print("Out 5: ", out5)

            # if(codeExitFlag[0] == 1 and codeExitFlag[1] == 0 and codeExitFlag[2] == 0 and codeExitFlag[3] == 0 and codeExitFlag[4] == 0):
            #     print("<<<<<<<<<<<<<<---------------EXITING--------------------->>>>>>>>>>>>>>>>")
            #     print("Total no. of cycles=",TotalCycles[0])
            #     break
            print("Total no. of cycles=", TotalCycles[0])
            TotalCycles[0]+=1         #Incrementing Total Cycles

            print("-------------------------------------------------------")

            pipe2 = manager.list()
            pipe3 = manager.list()
            pipe4 = manager.list()
            pipe5 = manager.list()
            extra_pipe=manager.list()


            pipe2 = out1
            pipe3 = out2
            pipe4 = out3
            pipe5 = out4
            extra_pipe=out5

            out1 = manager.list()
            out2 = manager.list()
            out3 = manager.list()
            out4 = manager.list()
            out5 = manager.list()
            out_stall = manager.list()


        print("Register: ", register[:])
        #Print data memory
        # for i in range(0,1000000000):
        #     if(data_mem[i]!=0):
        #         print("data_mem[",i,"]=",data_mem[i])



# Fetch helper functions

def write_word(address, instruction, MEM):
    '''
        Write Word
    '''
    index = address/4
    MEM[int(index)] = instruction

def read_word(address, MEM):
    '''
        Read Word
    '''
        
    return MEM[(address)]


# Decode helper functions

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
        ResultSelect = 5
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
    print("operand1=",operand1,"and operand2=",operand2)
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
    print("inst_type in DECODE=",inst_type)
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
        print("Operand1 is: ", operand1)
        print("Immediate is: ", immFinal)
        print("Write Register(rd) is: ", rd)
    elif (inst_type=='S'):
        print("Decode has Store instruction!")
        print("immFinal in DECODE=",immFinal,"and operand1 in DECODE=",operand1,"and operand2 in DECODE=",operand2)