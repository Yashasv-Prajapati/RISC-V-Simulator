# RISC-V-Simulator

This is the repository for the RISC-V simulator code.
This is the final project for the course CS-204 - Computer Architecture.

<br>
The team members are:
<br>

1. <p style="color:#EA8FEA;"> Arnav Kharbanda </p>
2. <p style="color:#FFAACF;"> Shobhit Juglan </p>
3. <p style="color:#B9F3E4;"> Gopal Bansal </p>
4. <p style="color:#FFF4D2;"> Yashasav Prajapati </p>

<br>

The simulator is written in `C`, the GUI is written in `ReactJs` and `NodeJs`.

<br>

## Testing the simulator using command line
To test the simulator, add a `.mem` file containing addresses of each instruction followed by the machine code of each instruction in the `test` directory and run the program as described below. Example below

```
0X0 0X00A00093
0X4 0X00900113
0X8 0X002081B3
0XC 0X004000EF
0X10 0X00000263
0X14 0X0202423
0X18 0X00802283
```

## Testing the simulator using GUI
To test the simulator using the GUI, go to the `gui` directory and follow the commands in the README.md file in the `gui` directory.


## Running the simulator
Nothing major here. Just clone the repository and run the following command in the `src` directory of the project. (Also make sure you have some C compiler installed.) 
```
make
```

This will create the executable file `myRISCVSim` in the `bin` directory.
Move to the `bin` directory and run the following command to run the simulator.
```
./myRISCVSim  <path_to_input_file>[../test/simple_add.mem]
```
This will run the simulator on the input file and generate the output file `output.mem` in the `bin` directory.

<p style="color:red;"> To delete the executable file, run the following command in the `src` directory </p>

```
make clean
```


## Key Features
1. The simulator supports all the instructions mentioned in the project description.
2. The GUI is fully functional and supports all the features, which include Run, Step, Reset, Previous, Register. [Memory to be added soon]
