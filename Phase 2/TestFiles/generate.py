i=0
output = open('output.mem', 'w')

with open('input.mem', 'r') as f:
    for line in f:
        text = hex(i)+' 0x'+line
        output.write(text)
        i += 4
    text = hex(i) + ' 0x000080b3\n'
    output.write(text)
    i+=4
    text=hex(i) + ' 0xfffffffb'
    output.write(text)
