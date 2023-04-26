<<<<<<< HEAD
# from gopal import *
from new import *
=======
from multiProcess_BTB import *
>>>>>>> refs/remotes/origin/main
import argparse
import sys

def init():
    parser = argparse.ArgumentParser(
                    prog='RISC V Simulator',
                    description='This program Simulates the RISC V Architecture computer',
                    epilog='Text at the bottom of help')
    
    parser.add_argument('--file', help='filename')

    args = parser.parse_args()

    if args.file:
        # print(args.file)

        reset_proc()
        load_program_memory(args.file, MEM)
        run_riscvsim()


    else:
        print("Incorrect number of arguments. Please invoke the simulator \n\t./myRISCVSim <input mem file>")
        sys.exit(0)

if __name__ == '__main__':
    init()
