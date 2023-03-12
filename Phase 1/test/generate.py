i=0
output = open('output2.mem', 'w')

with open('bubble_sort.mem', 'r') as f:
    for line in f:
        text = hex(i)+' 0x'+line
        output.write(text)
        i += 4
