from myRISCVSim import *
# from pipeline import *
import argparse
import sys


'''
int main(int argc, char** argv) {
  char* prog_mem_file; 
  if(argc < 2) {
    printf("Incorrect number of arguments. Please invoke the simulator \n\t./myRISCVSim <input mem file> \n");
    exit(1);
  }

  //reset the processor
  reset_proc();
  //load the program memory
  load_program_memory(argv[1], jsonFile);
  //run the simulator
  run_riscvsim(jsonFile);

  fclose(jsonFile);

  return 1;
}
'''

def init():
    parser = argparse.ArgumentParser(
                    prog='RISC V Simulator',
                    description='This program Simulates the RISC V Architecture computer',
                    epilog='Text at the bottom of help')
    
    parser.add_argument('--file', help='filename')

    args = parser.parse_args()

    if args.file:
        print(args.file)

        reset_proc()
        load_program_memory(args.file)
        run_riscvsim()


    else:
        print("Incorrect number of arguments. Please invoke the simulator \n\t./myRISCVSim <input mem file>")
        sys.exit(0)

if __name__ == '__main__':
    init()
