# #hola this is testing code

# i=0
# output = open('output.mem', 'w')

# # with open('input_files.txt.', 'r') as f:
# #     for line in f:
# #         open(line,'r') as testcase
# with open('input.mem', 'r') as f:
#     for line in f:
        
import os

# define the file names to run
file1 = "helo.py"
file2 = "helo1.py"

# define the command to run the files and capture their output
command = "python {}"

output1 = os.system("python helo.py")

# output1 = os.popen(command.format(file1), mode='r', buffering=-1).read()
output2 = os.popen(command.format(file2)).read()

# compare the outputs
print("Output1 is "+ output1)
print("Output2 is "+ output2)

if (output1 == output2):
    print("The outputs of {} and {} are the same!".format(file1, file2))
else:
    print("The outputs of {} and {} are different.".format(file1, file2))