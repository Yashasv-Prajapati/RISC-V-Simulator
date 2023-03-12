
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
#include <string.h>
#include <math.h>

//Register file
static unsigned int X[32];
// X[0]=0;
//flags
//memory
static unsigned char MEM[4000];

unsigned char *DataMEM;


//intermediate datapath and control path signals
static unsigned int instruction_word=0;
static unsigned int operand1;
static unsigned int operand2;
static unsigned int pc=0;

static unsigned int ALUop = 0;
static unsigned int ALUResult = 0;

static unsigned int MemOp = 0;
static unsigned int ReadData = 0;
static unsigned int LoadData=0;

static unsigned int ResultSelect = 0;
static unsigned int RFWrite = 0;

char instType;
static char opCode[7];
char rs1[5];
char rs2[5];
char rd[5];
char funct3[3];
char funct7[7];
char imm[12];
char immS[12];
char immB[13];
char immU[32];
char immJ[21];
char imm_final[32];
char bin_32_arr[32];
char hex_instr[8];//"019C5263";
//int instruction_word=908445968;
int Op2Select;
int Op1;
int Op2_final;
int rd_decimal;
//int ALUOp=0;
int BranchTargetSet;
int BranchTargetResult;
int imm_final_decimal;
int BranchTargetAddress;
int isBranch;
static int t=100;

void run_riscvsim() {
  
 while(1){
  //  printf("t in starting of loop=%d\n", t);
  //  printf("pc before fetch=%d\n", pc);
   fetch();
   if (pc > 4000)
   {
     break;
    }

    X[0]=0;
    // printf("pc after fetch=%d\n",pc);
    decode();

    X[0]=0;
    // printf("pc after decode=%d\n",pc);
    execute();

    X[0]=0;
    // printf("pc after execute=%d\n",pc);
    mem();

    X[0]=0;
    // printf("pc after mem=%d\n",pc);
    write_back();
    // printf("pc after write_back=%d\n",pc);
    // if(t<0){
    //   break;
    // }
    X[0]=0;
    t--;
    // printf("t in ending of loop=%d\n",t);
    // printf("X[2] at end of loop=%d\n",X[2]);
    printf("\n");
 }
  printf("SHOWING ALL THE REGISTERS\n");
  for(int i=0;i<32;i++){
    printf("X[%d] = %d\n", i, X[i]);
  }
}

// it is used to set the reset values
//reset all registers and memory content to 0
void reset_proc() {
  for(int i=0;i<32;i++){
    X[i]=0;
  }
  for(int i=0;i<4000;i++){
    MEM[i]=0;
  }
  // for(int i=0;i<10000;i++){
  //   DataMEM[i]=0;
  // }
  pc=0;
  instruction_word=0;
  operand1=0;
  operand2=0;
  ALUop=0;
  ALUResult=0;
  MemOp=0;
  ReadData=0;
  LoadData=0;
  ResultSelect=0;
  RFWrite=0;
  Op2Select=0;
  Op1=0;
  Op2_final=0;
  rd_decimal=0;
  BranchTargetSet=0;
  BranchTargetResult=0;
  imm_final_decimal=0;
  BranchTargetAddress=0;
  isBranch=0;
}

//load_program_memory reads the input memory, and pupulates the instruction
// memory
void load_program_memory(char *file_name) {
  FILE *fp;
  unsigned int address;
  unsigned int instruction;
  fp = fopen(file_name, "r");
  if(fp == NULL) {
    printf("Error opening input mem file\n");
    exit(1);
  }

  while(fscanf(fp, "%X %x", &address, &instruction) != EOF) {
    write_word(MEM, address, instruction);
    // printf("Instruction word from file is %d and address=%d and &instruction=%d and &address=%d\n", instruction,address,&instruction,&address);
    // printf("Instruction word from file in hex is %X\n", instruction);
  }

  fclose(fp);
  // for(int i=0;i<4000;i++){
  //   printf("%x ", MEM[i]);
  // }

  // initialize the data memory
  DataMEM = (unsigned char*) calloc(100,sizeof(unsigned char));

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
    fprintf(fp, "%X %X\n", i, read_word(MEM, i));
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
  instruction_word = read_word(MEM, pc);
   printf("instruction_word Read from memory=%d\n", instruction_word);
}
//reads the instruction register, reads operand1, operand2 fromo register file, decides the operation to be performed in execute stage
void decode() {
    printf("instruction_word in Decode startin=%d\n",instruction_word);
    Dec_to_Hex();//+++++++++c
    // printf("hex_instr=%s\n",hex_instr);
      HexToBin(hex_instr,bin_32_arr);
      printf("bin_32_arr=%s\n",bin_32_arr);
      // Working Fine
      opCode_gen(opCode,bin_32_arr);
      printf("OpCode=%s\n",opCode);
      rs1_gen(rs1,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
       printf("rs1=%s\n",rs1);
      rs2_gen(rs2,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      printf("rs2=%s\n",rs2);
      rd_gen(rd,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      printf("rd=%s and rd_decimal=%d\n",rd,rd_decimal);
      // printf("OpCode=%s\n",opCode);
      funct3_gen(funct3,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      printf("funct3=%s\n",funct3);
      funct7_gen(funct7,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      printf("funct7=%s\n",funct7);
      imm_gen(imm,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      // printf("imm=%s\n",imm);
      immS_gen(immS,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      // printf("immS=%s\n",immS);
      immB_gen(immB,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      // printf("immB=%s\n",immB);
      immU_gen(immU,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      // printf("immU=%s\n",immU);
      immJ_gen(immJ,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      // printf("immJ=%s\n",immJ);
      imm_final_gen(imm_final,bin_32_arr);
      // printf("OpCode=%s\n",opCode);
      // printf("imm_final=%s and imm_final_decimal=%d \n",imm_final,imm_final_decimal);
      printf("instType=%c\n",instType);
      // printf("OpCode=%s\n",opCode);
      //Control Signals
      ALUop_gen();
      // printf("ALUop=%d\n",ALUop);
      Op2Select_gen();
      // printf("Op1=%d and op2_final=%d\n",Op1,Op2_final);
      // printf("Op2Select=%d\n",Op2Select);
      BranchTargetSet_gen();

      // printf("BranchTargetSet=%d and BranchTargetResult=%d\n",BranchTargetSet,BranchTargetResult);
      MemOp_gen();
      // printf("MemOp=%d\n",MemOp);
      ResultSelect_gen();
      IsBranch_gen();
      // printf("isBranch=%d\n",isBranch);
    //  printf("ResultSet=%d and ResultSelect=");
      // printf("operand1=%d and operand2=%d\n",operand1,operand2);

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
  printf("ALUop=%d\n",ALUop);
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
  //Second Address
  BranchTargetAddress=BranchTargetResult+pc;
}

//perform the memory operation
void mem() {
  /*
    MemOp operation
    0 - Do nothing (skip)
    1 - Write in memory --> Store
    2 - Read from memory --> Load
  */
  if (MemOp == 0)
  {
    ReadData = ALUResult;
  }
  else if (MemOp == 1) // Store
  {
    int *data_p;
    data_p = (int*)(DataMEM + ALUResult);
    int rs2Value = BintoDec(rs2,5);
    // printf("X[%d] = %d and Op2_final is = %d\n",Op2_final, X[Op2_final], Op2_final);

    *data_p = X[rs2Value];
    ReadData = X[rs2Value];
  }
  else if (MemOp == 2) // Load
  {
    int *data_p;
    data_p = (int*)(DataMEM + ALUResult);
    ReadData = *data_p;
    // printf("ReadData = %d\n", ReadData);
  }

  // reset the control signal 
  MemOp=0;
}

//writes the results back to register file
void write_back() {
  /*
    ResultSelect
    5 - None
    0 - PC+4
    1 - ImmU_lui
    2 - ImmU_auipc
    3 - LoadData - essentially same as ReadData
    4 - ALUResult
  */

//  rd , ImmU_lui, Immu_auipc are to be decided, so creating temp variables in their name
  int rd, ImmU_lui, Immu_auipc;
  printf("RFWrite in Write_back=%d and ResultSelect=%d\n",RFWrite,ResultSelect);
  if(RFWrite){
    // printf("rd_decimal = %d\n", rd_decimal);
    switch(ResultSelect){
      case 0:{
        X[rd_decimal] = pc+4;
        break;
      }
      case 1:{
        X[rd_decimal] = imm_final_decimal << 12;
        break;
      }
      case 2:{
        X[rd_decimal] = pc + (imm_final_decimal << 12) ;
        break;
      }
      case 3:{
        // printf("ReadData in other = %d\n", ReadData);
        static unsigned int LoadData;
        LoadData = ReadData ;
        X[rd_decimal] = ReadData;
        break;
      }
      case 4:{
        X[rd_decimal] = ALUResult;
        break;
      }
      // need to make another case for store instruction
    }
  }
    
    printf("ISbranch=%d and ALUResult=%d\n",isBranch,ALUResult);
    //IS BRANCH MUX
    /*
      IsBranch=0 => ALUResult
      =1         => BranchTargetAddress
      =2         => pc+4(default)
    */
    if(isBranch==0){
        pc=ALUResult;
    }
    else if(isBranch==1){
        pc=BranchTargetAddress;
    }
    else{
        pc=pc+4;
    }

}

unsigned int read_word(char *mem, unsigned int address) {
  unsigned int *data;
  // printf("here instruction_word=%d\n",instruction_word);
  printf("pc=%d\n",pc);
  // printf("mem=%d and address=%d",mem,address);
  data =  (unsigned int*) (mem + address);
  // printf("READ DATA from read_word function is %d and *data=%d\n", data,*data);
  return *data;
}

void write_word(char *mem, unsigned int address, unsigned int data) {
  unsigned int *data_p;
  data_p = (unsigned int*) (mem + address);
  *data_p = data;
}

// Decode functions start
int BintoDec(char* Bin,int size){
    int Dec=0;
    
    for(int i=size-1;i>=0;i--){
        if(Bin[i]=='1'){
          Dec += 1;
        }
        Dec *= 2;
    }
    return Dec/2;
}

void Dec_to_Hex(){
    unsigned int decimal_Number=instruction_word;
    printf("decimal number is %d\n", decimal_Number);
     char hexa_instr[8];
    int i=0;
    while (decimal_Number != 0) {
        int temp = decimal_Number % 16;

        // converting decimal number
        // in to a hexa decimal
        // number
        if (temp < 10)
            temp = temp + 48;
        else
            temp = temp + 55;
        hexa_instr[i] = temp;
        i++;
        decimal_Number = decimal_Number / 16;
    }
    while(i<8){
        hexa_instr[i]='0';
        i++;
    }
    hex_instr[8]='\0';
    // sprintf(hex_instr, "%08X", decimal_Number);
    // printf("hex_instr is %s and it's length is %lu\n", hex_instr, strlen(hex_instr));
    
   for(int i=0;i<=7;i++){
       hex_instr[i]=hexa_instr[7-i];
   }
  //  printf("instruction word is %d\n", instruction_word);
  //  printf("actual hex = %X\n", instruction_word);
    printf("HEX_INSTRUCTION STRING IS %s\n", hex_instr);
    printf("HEXA_INSTRUCTION STRING IS %s\n", hexa_instr);

}
//int char_to_int(char c){
//    int c_int=c;
//    if(c_int<=57){
//        return c_int-48;
//    }
//    else{
//        return c_int-55;
//    }
//}
//void decToBinary(int n)
//{
//    // array to store binary number
//    int binaryNum[4];
//
//    // counter for binary array
//    int i = 0;
//    while (n > 0) {
//        // storing remainder in binary array
//        binaryNum[i] = n % 2;
//        n = n / 2;
//        i++;
//    }
//    while(i<=4){
//
//    }
//    // printing binary array in reverse order
//    for (int j = i - 1; j >= 0; j--)
//        printf("%d", binaryNum[j]);
//}

void opCode_gen(char *opCode,char *bin_32_arr){
    for(int i=0;i<=6;i++){
        opCode[i]=bin_32_arr[i];
    }
    opCode[7]='\0';
}

void rs1_gen(char *rs1,char *bin_32_arr){
    for(int i=15;i<=19;i++){
        rs1[i-15]=bin_32_arr[i];
    }
    rs1[5]='\0';
}
void rs2_gen(char *rs2,char *bin_32_arr){
    for(int i=20;i<=24;i++){
        rs2[i-20]=bin_32_arr[i];
    }
    rs2[5]='\0';
}
void funct3_gen(char *funct3,char *bin_32_arr){
    for(int i=12;i<=14;i++){
        funct3[i-12]=bin_32_arr[i];
    }
    funct3[3]='\0';
}

void funct7_gen(char *rd,char *bin_32_arr){
    for(int i=25;i<=31;i++){
        funct7[i-25]=bin_32_arr[i];
    }
    funct7[8]='\0';
}
void rd_gen(char *rd,char *bin_32_arr){
    for(int i=7;i<=11;i++){
        rd[i-7]=bin_32_arr[i];
    }
    rd[6]='\0';
    rd_decimal=BintoDec(rd,5);
}

void imm_gen(char* imm,char * bin_32_arr){
    for(int i=20;i<=31;i++){
        imm[i-20]=bin_32_arr[i];
    }
}
void immS_gen(char* immS,char* bin_32_arr){
    for(int i=7;i<=11;i++){
        immS[i-7]=bin_32_arr[i];
    }
    for(int i=25;i<=31;i++){
        immS[i-20]=bin_32_arr[i];
    }
}
void immB_gen(char* immB,char* bin_32_arr){
    immB[0]='0';
    immB[11]=bin_32_arr[7];
    for(int i=8;i<=11;i++){
        immB[i-7]=bin_32_arr[i];
    }
    immB[12]=bin_32_arr[31];
    for(int i=25;i<=30;i++){
        immB[i-20]=bin_32_arr[i];
    }
}
void immU_gen(char* immU,char* bin_32_arr){
//    printf("IMMU BEFORE %s\n", immU);
    for(int i=0;i<=11;i++){
        immU[i]='0';
    }
//    printf("IMMU INTERMEDIATE %s\n", immU);
    for(int i=12;i<=31;i++){
        immU[i]=bin_32_arr[i];
//        printf("bin_32_arr[i] = %c\n", bin_32_arr[i]);
    }
    immU[32]='\0';
//    printf("IMMU AFTER %s\n", immU);
//    printf("IMMU SIZE %d\n", sizeof(immU)/sizeof(immU[0]));
}
void immJ_gen(char* immJ,char* bin_32_arr){
    for(int i=12;i<=19;i++){
        immJ[i]=bin_32_arr[i];
    }
    immJ[11]=bin_32_arr[20];
    immJ[0]='0';
    for(int i=21;i<=30;i++){
        immJ[i-20]=bin_32_arr[i];
    }
    immJ[20]=bin_32_arr[31];
}
void signExtender(char *array,int index){
    //index is the index for which extension will be done
    for(int i=index+1;i<=31;i++){
        array[i]=array[index];
    }
}

void imm_final_gen(char *imm_final,char* bin_32_arr){
  // printf("STRING COMPARE = %d and opCode is = %s\n", strcmp(opCode,"1100100"), opCode);
    
        // printf("YES HERE\n");
        // printf("opCode = %s\n", opCode);
    if(!strncmp(opCode,"1100110", 7)){
        //R-Type
        instType='R';
        // printf("YES HERE\n");
//        strncpy(imm_final,imm,12);
//        signExtender(imm_final,11);
    }
    else if(!strncmp(opCode,"1100100", 7) || !strncmp(opCode,"1100000", 7)){
        //I-type
        instType='I';
        strncpy(imm_final,imm,12);
        signExtender(imm_final,11);
    }
    else if(!strncmp(opCode,"1100010",7)){
        //S-Type
        instType='S';
        strncpy(imm_final,immS,12);
        signExtender(imm_final,11);
    }
    else if(!strncmp(opCode,"1100011",7)){
        //B-Type
        instType='B';
        strncpy(imm_final,immB,13);
        signExtender(imm_final,12);
    }
    else if(!strncmp(opCode,"1110110",7)){
        //U-Type
        instType='U';
        strncpy(imm_final,immU,32);
//        signExtender(imm_final)
    }
    else if(!strncmp(opCode,"1111011",7)){
        //J-Type
        instType='J';
        strncpy(imm_final,immJ,21);
        signExtender(imm_final,20);
    }else{ // incase none matches, then we simply put a dummy character
      instType = 'Z';
    }
    imm_final_decimal=BintoDec(imm_final,32);
}
void ALUop_gen(){
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
    if(strncmp(funct3,"000",3)==0&&instType=='R'){
        ALUop=1;
    }
    else if(strncmp(funct3,"111",3)==0&&instType=='I'){
        ALUop=3;
    }
    else if(strncmp(funct3,"011",3)==0){
            ALUop=4;
    }
    else if(strncmp(funct3,"100",3)==0&&instType=='R'){
        ALUop=5;
    }
    else if(strncmp(funct3,"010",3)==0&&instType=='R'){
        ALUop=8;
    }
    else if(strncmp(funct3,"101",3)==0&&instType=='R'){
        ALUop=6;
    }
    else if(strncmp(funct3,"001",3)==0&&instType=='R'){
        ALUop=7;
    }
    else if(instType=='B'){
        ALUop=2;
    }
    else if(strncmp(funct7,"0000010",7)==0&&strncmp(funct3,"000",3)==0&&instType=='R'){
        ALUop=2;
    }
    else{
        ALUop=1;
    }
}
void HexToBin(char* hexdec,char *bin_32_arr)
{

    long int i = 0;
//    char bin_32_arr[32];
    while (hexdec[i]) {
         if(hexdec[i]== '0'){
            char* c0="0000";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c0[j];
//                printf("%c",bin_32_arr[31-(4*i)-j]);
            }
          }
         else if(hexdec[i]== '1'){
            char* c1="0001";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c1[j];
            }
            }
         else if(hexdec[i]== '2'){
            char* c2="0010";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c2[j];
            }
            }
         else if(hexdec[i]== '3'){
            char* c3="0011";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c3[j];
                // bin_32_arr[31-(4*i)-3+j]=c3[j];
            }
            }
         else if(hexdec[i]== '4'){
            char* c4="0100";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c4[j];
            }
            }
         else if(hexdec[i]== '5'){
            char* c5="0101";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c5[j];
            }
            }
         else if(hexdec[i]== '6'){
            char* c6="0110";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c6[j];
            }
            }
         else if(hexdec[i]== '7'){
            char* c7="0111";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c7[j];
            }
            }
         else if(hexdec[i]== '8'){
            char* c8="1000";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c8[j];
            }
            }
         else if(hexdec[i]== '9'){
            char* c9="1001";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c9[j];
            }
            }
         else if(hexdec[i]== 'A'){
            char* c10="1010";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c10[j];
            }
            }
         else if(hexdec[i]== 'B'){
            char* c11="1011";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c11[j];
            }
            }
         else if(hexdec[i]== 'C'){
            char* c12="1100";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c12[j];
            }
            }
         else if(hexdec[i]== 'D'){
            char* c13="1101";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c13[j];
            }
            }
         else if(hexdec[i]== 'E'){
            char* c14="1110";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c14[j];
            }
            }
         else if(hexdec[i]== 'F'){
            char* c15="1111";
            for(int j=0;j<4;j++){
                bin_32_arr[31-(4*i)-j]=c15[j];
            }
            }
        i++;
    }
//    printf("TS");
//    printf("%c is the [33] of %s",bin_32_arr[33],bin_32_arr);
    bin_32_arr[32]='\0';

//    char *b=bin_32_arr;
//    return b;
//    return  bin_32_arr;
}
void Op2Select_gen(){
    /*Op2Select=1 =>rs2
    Op2Select=2 =>imm
    Op2Select=3 =>immS
    */
    Op1=BintoDec(rs1,5);
    operand1=X[Op1];
    if(instType=='S'){
        Op2Select=3;
        Op2_final=BintoDec(imm_final,32);
        operand2=Op2_final;
    }
    else if(instType=='I'){
        Op2Select=2;
        Op2_final=BintoDec(imm_final,32);
        operand2=Op2_final;
    }
    else{
        Op2Select=1;
        Op2_final=BintoDec(rs2,5);
        operand2=X[Op2_final];
    }
}
void BranchTargetSet_gen(){
/*if BranchTargetSet=1 =>IMMB otherwise immJ
*/
    if(instType=='B'){
        BranchTargetSet=1;
        BranchTargetResult=BintoDec(imm_final,32);
    }
    else{
        BranchTargetSet=2;
        BranchTargetResult=BintoDec(imm_final,32);
    }
}

void MemOp_gen(){
    if(instType=='S'){
        MemOp=1;
      // printf("YES HERE 1 \n");
    }
    else if(!strncmp(opCode,"1100000",7)){
        MemOp=2;
      // printf("YES HERE \n");
    }
    else {
        MemOp=0;
    }
}

void ResultSelect_gen(){
  /*
    ResultSelect
    5 - None
    0 - PC+4
    1 - ImmU_lui
    2 - ImmU_auipc
    3 - LoadData - essentially same as ReadData
    4 - ALUResult
  */
    RFWrite = 0;
    if(!strncmp(opCode, "1110110",7)){
        ResultSelect=1;
        RFWrite = 1;
        // printf("ResultSelect=1");
        // printf("ResultSelect=1");
    }
    else if(!strncmp(opCode, "1110100",7)){
        ResultSelect=2;
        RFWrite = 1;
        // printf("ResultSelect=2");
    }
    else if(!strncmp(opCode, "1111011",7)||!strncmp(opCode, "1110011",7)){
        ResultSelect=0;
        RFWrite = 1;
        // printf("ResultSelect=3");
    }
    else if(!strncmp(opCode, "1100000",7)){
        ResultSelect=3;
        RFWrite = 1;
        // printf("ResultSelect=4");
    }else if(!strncmp(opCode, "1100010",7)){ // store instruction - no write to RF added
        RFWrite = 0;
    }
    else if(instType=='B'){
        RFWrite=0;
    }
    else{
        ResultSelect=4;
        
        // printf("ResultSelect=5");
        RFWrite = 1;
    }
}
void IsBranch_gen(){
    // IS BRANCH MUX
    /*
      IsBranch=0 => ALUResult
      =1         => BranchTargetAddress
      =2         => pc+4(default)
    */
   printf("operand1=%d operand2=%d", operand1, operand2);
    if(opCode=="1110011"){
        isBranch=0;
    }
    else if(instType=='B'){
      isBranch=2;

      // we already have funct3 for Branch so using that funct3
      printf("strncmp= %d", strncmp(funct3, "000", 3));

      if(!strncmp(funct3, "000", 3)){
        // beq 
        if(operand1==operand2){
            isBranch=1;
        }
      }

      if(!strncmp(funct3, "100", 3)){
        // bne
        if(operand1!=operand2){
            isBranch=1;
        }
      }

      if(!strncmp(funct3, "001", 3)){
        // blt
        if(operand1<operand2){
            isBranch=1;
        }
      }

      if(!strncmp(funct3, "101", 3)){
        // bge
        if(operand1>=operand2){
            isBranch=1;
        }
      }

    }
    else if(instType=='J'){
        isBranch = 1;
    }
    else{
        isBranch=2;
    }
}

// Decode functions ends here
