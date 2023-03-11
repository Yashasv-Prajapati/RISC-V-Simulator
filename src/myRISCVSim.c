
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

//#include "myRISCVSim.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

//Register file
static unsigned int X[32];
//X[0]=0;
//flags
//memory
static unsigned char MEM[4000];

static unsigned char DataMEM[10000];

//intermediate datapath and control path signals
static unsigned int instruction_word=1931476993;
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
char opCode[7];
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
void run_riscvsim() {
 while(1){
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
    printf("%x ", MEM[i]);
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
  // printf("instruction word is %x\n", instruction_word);
  pc = pc + 4;
}
//reads the instruction register, reads operand1, operand2 fromo register file, decides the operation to be performed in execute stage
void decode() {
    Dec_to_Hex();//+++++++++c
    printf("hex_instr=%s\n",hex_instr);
      HexToBin(hex_instr,bin_32_arr);
      printf("bin_32_arr=%s\n",bin_32_arr);
      //Working Fine
      opCode_gen(opCode,bin_32_arr);
      printf("OpCode=%s\n",opCode);
      rs1_gen(rs1,bin_32_arr);
      printf("rs1=%s\n",rs1);
      rs2_gen(rs2,bin_32_arr);
      printf("rs2=%s\n",rs2);
      rd_gen(rd,bin_32_arr);
      printf("rd=%s and rd_decimal=%d\n",rd,rd_decimal);
      funct3_gen(funct3,bin_32_arr);
      printf("funct3=%s\n",funct3);
      funct7_gen(funct7,bin_32_arr);
      printf("funct7=%s\n",funct7);
      imm_gen(imm,bin_32_arr);
      printf("imm=%s\n",imm);
      immS_gen(immS,bin_32_arr);
      printf("immS=%s\n",immS);
      immB_gen(immB,bin_32_arr);
      printf("immB=%s\n",immB);
      immU_gen(immU,bin_32_arr);
      printf("immU=%s\n",immU);
      immJ_gen(immJ,bin_32_arr);
      printf("immJ=%s\n",immJ);
      imm_final_gen(imm_final,bin_32_arr);
      printf("imm_final=%s and imm_final_decimal=%d \n",imm_final,imm_final_decimal);
      printf("instType=%c\n",instType);
      //Control Signals
      ALUop_gen();
      printf("ALUop=%d\n",ALUop);
      Op2Select_gen();
      printf("Op1=%d and op2_final=%d\n",Op1,Op2_final);
      printf("Op2Select=%d\n",Op2Select);
      BranchTargetSet_gen();

      printf("BranchTargetSet=%d and BranchTargetResult=%d\n",BranchTargetSet,BranchTargetResult);
      MemOp_gen();
      ResultSelect_gen();
      IsBranch_gen();
      printf("isBranch=%d\n",isBranch);
//      printf("ResultSet=%d and ResultSelect=")
      printf("operand1=%d and operand2=%d\n",operand1,operand2);

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
  //Second Address
  BranchTargetAddress=BranchTargetResult+pc;
  printf("BranchTargetAddress=%d",BranchTargetAddress);
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
  else if (MemOp == 1) // write
  {
    int *data_p;
    data_p = (int*)(DataMEM + ALUResult);
    *data_p = operand2;
    ReadData = operand2;
  }
  else if (MemOp == 2) // read
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
    3 - LoadData - essentially same as ReadData
    4 - ALUResult
  */

//  rd , ImmU_lui, Immu_auipc are to be decided, so creating temp variables in their name
  int rd, ImmU_lui, Immu_auipc;

  if(!RFWrite)
    switch(ResultSelect){
      case 0:{
        X[rd_decimal] = pc+4;
      }
      case 1:{
        X[rd_decimal] = imm_final_decimal << 12;
      }
      case 2:{
        X[rd_decimal] = pc + (imm_final_decimal << 12) ;
      }
      case 3:{
        static unsigned int *LoadData;
        LoadData = ReadData ;
        X[rd_decimal] = LoadData;
      }
      case 4:{
        X[rd_decimal] = ALUResult;
      }
    }
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
        pc+=4;
    }
}

int read_word(char *mem, unsigned int address) {
  int *data;
  data =  (int*) (mem + address);
  return *data;
}

void write_word(char *mem, unsigned int address, unsigned int data) {
  int *data_p;
  data_p = (int*) (mem + address);
  *data_p = data;
}

                                           ///////




int BintoDec(char* Bin,int size){
    int Dec=0;
    for (int i=0;i<size;i++){
        if(Bin[i]=='1'){
            Dec+=pow(2,i);
        }
    }
    return Dec;
}
void Dec_to_Hex(){
    int decimal_Number=instruction_word;
//    char hex_instr[8];
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
        hex_instr[i] = temp;
        i++;
        decimal_Number = decimal_Number / 16;
    }
    while(i<8){
        hex_instr[i]='0';
        i++;
    }
    hex_instr[8]='\0';
//    for(int i=0;i<=7;i++){
//        hex_instr[i]=hexa_instr[7-i];
//    }

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
}

void rs1_gen(char *rs1,char *bin_32_arr){
    for(int i=15;i<=19;i++){
        rs1[i-15]=bin_32_arr[i];
    }
}
void rs2_gen(char *rs2,char *bin_32_arr){
    for(int i=20;i<=24;i++){
        rs2[i-20]=bin_32_arr[i];
    }
}
void funct3_gen(char *funct3,char *bin_32_arr){
    for(int i=12;i<=14;i++){
        funct3[i-12]=bin_32_arr[i];
    }
}

void funct7_gen(char *rd,char *bin_32_arr){
    for(int i=25;i<=31;i++){
        funct7[i-25]=bin_32_arr[i];
    }
}
void rd_gen(char *rd,char *bin_32_arr){
    for(int i=7;i<=11;i++){
        rd[i-7]=bin_32_arr[i];
    }
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
    if(!strcmp(opCode,"1100110")){
        //R-Type
        instType='R';
//        strncpy(imm_final,imm,12);
//        signExtender(imm_final,11);
    }
    else if(!strcmp(opCode,"1100100")){
        //I-type
        instType='I';
        strncpy(imm_final,imm,12);
        signExtender(imm_final,11);
    }
    else if(!strcmp(opCode,"1100010")){
        //S-Type
        instType='S';
        strncpy(imm_final,immS,12);
        signExtender(imm_final,11);
    }
    else if(!strcmp(opCode,"1100011")){
        //B-Type
        instType='B';
        strncpy(imm_final,immB,13);
        signExtender(imm_final,12);
    }
    else if(!strcmp(opCode,"1110110")){
        //U-Type
        instType='U';
        strncpy(imm_final,immU,32);
//        signExtender(imm_final)
    }
    else if(!strcmp(opCode,"1111011")){
        //J-Type
        instType='J';
        strncpy(imm_final,immJ,21);
        signExtender(imm_final,20);
    }
    imm_final_decimal=BintoDec(imm_final,32);
}
void ALUop_gen(){
    if(strcmp(funct3,"000")==0&&instType=='R'){
        ALUop=3;
    }
    else if(strcmp(funct3,"111")==0&&instType=='I'){
        ALUop=3;
    }
    else if(strcmp(funct3,"011")==0){
            ALUop=4;
    }
    else if(strcmp(funct3,"100")==0&&instType=='R'){
        ALUop=5;
    }
    else if(strcmp(funct3,"010")==0&&instType=='R'){
        ALUop=5;
    }
    else if(strcmp(funct3,"101")==0&&instType=='R'){
        ALUop=6;
    }
    else if(strcmp(funct3,"001")==0&&instType=='R'){
        ALUop=7;
    }
    else if(instType=='B'){
        ALUop=2;
    }
    else if(strcmp(funct7,"0000010")==0&&strcmp(funct3,"000")==0&&instType=='R'){
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
        Op2_final=BintoDec(immS,32);
        operand2=Op2_final;
    }
    else if(instType=='I'){
        Op2Select=2;
        Op2_final=BintoDec(imm,32);
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
    }
    else if(opCode=='1100000'){
        MemOp=2;
    }
    else {
        MemOp=0;
    }
}

void ResultSelect_gen(){
    if(opCode=="111011"){
        ResultSelect=1;
    }
    else if(opCode=="1110100"){
        ResultSelect=2;
    }
    else if(opCode=="1111011"||opCode=="1110011"){
        ResultSelect=0;
    }
    else if(opCode=="1100000"){
        ResultSelect=3;
    }
    else{
        ResultSelect=4;
    }
}
void IsBranch_gen(){
    if(opCode=="1110011"){
        isBranch=0;
    }
    else if(instType=='B'||instType=='J'){
        isBranch=1;
    }
    else{
        isBranch=2;
    }
}
int main(void){
//    printf("\ninstruction_word BEFORE fetch=%d\n",instruction_word);
//    fetch();
//    printf("\ninstruction_word AFTER fetch=%d\n",instruction_word);
    decode();
    return 0;
}
