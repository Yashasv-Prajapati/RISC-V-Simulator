
/* 

The project is developed as part of Computer Architecture class
Project Name: Functional Simulator for subset of RISCV Processor

Developer's Name:
Developer's Email id:
Date: 

*/


/* myRISCVSim.cpp
   Purpose of this file: implementation file for myRISCVSim
*/

#include "myRISCVSim.h"
#include <stdlib.h>
#include <stdio.h>


//Register file
static unsigned int X[32];
//flags
//memory
static unsigned char MEM[4000];

static unsigned char DataMEM[1000];

//intermediate datapath and control path signals
static unsigned int instruction_word;
static unsigned int operand1;
static unsigned int operand2;
static unsigned int pc=0;

static unsigned int ALUop = 0;
static unsigned int ALUResult = 0;

static unsigned int MemOp = 0;
static unsigned int ReadData = 0;

static unsigned int ResultSelect = 0;
static unsigned int RFWrite = 0;

void run_riscvsim() {
  while(1) {
    fetch();
    decode();
    execute();
    mem();
    write_back();
  }
}

// it is used to set the reset values
//reset all registers and memory content to 0
void reset_proc() {

}

//load_program_memory reads the input memory, and pupulates the instruction 
// memory
void load_program_memory(char *file_name) {
  FILE *fp;
  unsigned int address, instruction;
  fp = fopen(file_name, "r");
  if(fp == NULL) {
    printf("Error opening input mem file\n");
    exit(1);
  }
  while(fscanf(fp, "%x %x", &address, &instruction) != EOF) {
    write_word(MEM, address, instruction);
  }
  fclose(fp);
  for(int i=0;i<4000;i++){
    printf("%d ", MEM[i]);
  }
}

//writes the data memory in "data_out.mem" file
void write_data_memory() {
  FILE *fp;
  unsigned int i;
  fp = fopen("data_out.mem", "w");
  if(fp == NULL) {
    printf("Error opening dataout.mem file for writing\n");
    return;
  }
  
  for(i=0; i < 4000; i = i+4){
    fprintf(fp, "%x %x\n", i, read_word(MEM, i));
  }
  fclose(fp);
}

//should be called when instruction is swi_exit
void swi_exit() {
  write_data_memory();
  exit(0);
}


//reads from the instruction memory and updates the instruction register
void fetch(){
  if(pc>4000){
    exit(0);
  }
  instruction_word = read_word(MEM, pc);
  printf("instruction word is %x\n", instruction_word);
  pc = pc + 4;
}
//reads the instruction register, reads operand1, operand2 fromo register file, decides the operation to be performed in execute stage
void decode() {
}
//executes the ALU operation based on ALUop
void execute() {
  /*
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
  */

  if (ALUop == 1)
  {
    ALUResult = operand1 + operand2;
  }
  else if (ALUop == 2)
  {
    ALUResult = operand1 - operand2;
  }
  else if (ALUop == 3)
  {
    ALUResult = operand1 & operand2;
  }
  else if (ALUop == 4)
  {
    ALUResult = operand1 | operand2;
  }
  else if (ALUop == 5)
  {
    ALUResult = operand1 << operand2;
  }
  else if (ALUop == 6)
  {
    ALUResult = operand1 >> operand2;
  }
  else if (ALUop == 7)
  {
    ALUResult = operand1 ^ operand2;
  }
  else if (ALUop == 8)
  {
    ALUResult = (operand1 < operand2)?1:0;
  }
}
//perform the memory operation
void mem() {
  /*
    MemOp operation
    0 - Do nothing (skip)
    1 - Write 
    2 - Read
  */
  if (MemOp == 0)
  { 
    ReadData = ALUResult;
  }
  else if (MemOp == 1)
  {
    int *data_p;
    data_p = (int*)(DataMEM + ALUResult);
    *data_p = operand2;
    ReadData = operand2;
  }
  else if (MemOp == 2)
  {
    int *data_p;
    data_p = (int*)(DataMEM + ALUResult);
    ReadData = *data_p;
  }
}


//writes the results back to register file
void write_back() {
  /*
    ResultSelect
    0 - PC+4
    1 - ImmU_lui
    2 - ImmU_auipc
    3 - LoadData
    4 - ALUResult
  */
  if(!RFWrite)
    switch(ResultSelect){
      case 0:{
        rd = pc+4;
      }
      case 1:{
        rd = ImmU_lui << 12;
      }
      case 2:{
        rd = pc + (Immu_auipc << 12) ;
      }
      case 3:{
        static unsigned int *LoadData;
        LoadData = ReadData ;
        rd = LoadData;
      }
      case 4:{
        rd = ALUResult;
      }
    }


}


int read_word(char *mem, unsigned int address) {
  int *data;
  data =  (int*) (mem + address);
  return *data;
}

void write_word(char *mem, unsigned int address, unsigned int data) {
  int *data_p;
  printf(" address is %d\n", address);
  data_p = (int*) (mem + address);
  *data_p = data;
}


void parseBytes(char *mem, unsigned int address){
  int *data_p;
  data_p = (int*) (mem + address);
  unsigned int data = MEM[address];

}