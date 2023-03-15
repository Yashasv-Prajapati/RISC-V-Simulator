/* 

The project is developed as part of Computer Architecture class
Project Name: Functional Simulator for subset of ARM Processor

Developer's Name:
Developer's Email id:
Date: 

*/
#include<stdio.h>

/* myRISCVSim.h
   Purpose of this file: header file for myARMSim
*/

void run_riscvsim();
void reset_proc();
void load_program_memory(char* file_name, FILE *jsonFile);
void write_data_memory();
void swi_exit();



//reads from the instruction memory and updates the instruction register
void fetch();
//reads the instruction register, reads operand1, operand2 fromo register file, decides the operation to be performed in execute stage
void decode();
//executes the ALU operation based on ALUop
void execute();
//perform the memory operation
void mem();
//writes the results back to register file
void write_back();


unsigned int read_word(char *mem, unsigned int address);
void write_word(char *mem, unsigned int address, unsigned int data);

int BintoDec(char* Bin,int size);
void Dec_to_Hex();
void opCode_gen(char *opCode,char *bin_32_arr);
void rs1_gen(char *rs1,char *bin_32_arr);
void rs2_gen(char *rs2,char *bin_32_arr);
void funct3_gen(char *funct3,char *bin_32_arr);
void funct7_gen(char *rd,char *bin_32_arr);
void rd_gen(char *rd,char *bin_32_arr);
void imm_gen(char* imm,char * bin_32_arr);
void immS_gen(char* immS,char* bin_32_arr);
void immB_gen(char* immB,char* bin_32_arr);
void immU_gen(char* immU,char* bin_32_arr);
void immJ_gen(char* immJ,char* bin_32_arr);
void signExtender(char *array,int index);
void imm_final_gen(char *imm_final,char* bin_32_arr);
void ALUop_gen();
// void HexToBin(char* hexdec,char *bin_32_arr);
void HexToBin();
void Op2Select_gen();
void BranchTargetSet_gen();
void MemOp_gen();
void ResultSelect_gen();
void IsBranch_gen();
void operation_gen();