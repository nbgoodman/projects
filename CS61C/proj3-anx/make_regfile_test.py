import sys
import numpy as np

def switch(x):
    return {
        'sll':0,
        'srl':1,
        'sra':2,
        'mult':3,
        'divu':4,
        'add':5,
        'addu':6,
        'sub':7,
        'subu':8,
        'and':9,
        'or':10,
        'xor':11,
        'nor':12,
        'slt':13,
        'sltu':14,
    }.get(x, 15)

registers = np.zeros(32)

user_input = raw_input("Test name: ")
name = user_input
f_D = open("tests/"+name+".D", 'w')
f_R = open("tests/"+name+".R", 'w')
f_out = open("tests/"+name+".out", 'w')
f_D.write("v2.0 raw\n")
f_R.write("v2.0 raw\n")
print("Created files "+name+".D, .R  and .out in your tests folder")
success = 0
#CYCLES
while success==0:
    user_input = raw_input("Number of cycles: ")
    try:
        cycles = int(user_input)
        print(user_input+" cycles")
        success = 1
    except ValueError:
        print("Please enter a valid base-10 number.")
for t in range(cycles):
    success = 0
    #Write Data
    while success==0:
        user_input = raw_input("Time "+str(t)+"\tWrite Data: ")
        try:
            if user_input[0:2] == "0x":
                val = int(user_input[2:], 16)
            elif user_input[0:2] == "0b":
                val = int(user_input[2:], 2)
            else:
                val = int(user_input)
            s = format(val, '08x')
            f_D.write(s+"\n")
            success = 1
        except ValueError:
            print("Please enter a valid number.")
    success = 0
    #RS
    regval = 0
    while success==0:
        user_input = raw_input("Time "+str(t)+"\tRead Register 1: ")
        try:
            if user_input[0:2] == "0x":
                val = int(user_input[2:], 16)
            elif user_input[0:2] == "0b":
                val = int(user_input[2:], 2)
            else:
                regval = int(user_input)
            success = 1
        except ValueError:
            print("Please enter a valid number.")
    success = 0
    #RT
    while success==0:
        user_input = raw_input("Time "+str(t)+"\tRead Register 2: ")
        try:
            if user_input[0:2] == "0x":
                val = int(user_input[2:], 16)
            elif user_input[0:2] == "0b":
                val = int(user_input[2:], 2)
            else:
                regval = regval | (int(user_input) << 5)
            success = 1
        except ValueError:
            print("Please enter a valid number.")
    success = 0
    #RD
    while success==0:
        user_input = raw_input("Time "+str(t)+"\tWrite Register: ")
        try:
            if user_input[0:2] == "0x":
                val = int(user_input[2:], 16)
            elif user_input[0:2] == "0b":
                val = int(user_input[2:], 2)
            else:
                regval = regval | (int(user_input) << 10)
            success = 1
        except ValueError:
            print("Please enter a valid number.")
    success = 0
    #WE
    while success==0:
        user_input = raw_input("Time "+str(t)+"\tWrite Enable: ")
        try:
            regval = regval | (int(user_input, 2) << 15)
            f_R.write(regval+"\n") #Do I need to alternate between spaces and new lines?
            success = 1
        except ValueError:
            print("Please enter a valid number.")
    success = 0
    #S
    while success==0:
        user_input = raw_input("Time "+str(t)+"\tFunction: ")
        if user_input == 'mult' or user_input == 'divu':
            result2 = 1
        else:
            result2 = 0
        val = switch(user_input)
        if val != 15:
            s = format(val, '01x')
            f_S.write(s+"\n")
            success = 1
        else:
            print("Please enter valid instruction name. Ex: 'add'")    
    success = 0
    #TIME
    s = format(t, '08b')
    s = " ".join(s[i:i+4] for i in range(0, len(s), 4))
    f_out.write(s+"\t") 
    #OVERFLOW
    while success == 0:
        user_input = raw_input("Expected Signed Overflow: ")
        try:
            val = int(user_input, 2)
            s = format(val, '01b')
            f_out.write(s+"\t") 
            success = 1
        except ValueError:
            print("Please enter a '1' or a '0'") 
    success = 0
    #EQUAL
    while success == 0:
        user_input = raw_input("Expected Equal: ")
        try:
            val = int(user_input, 2)
            s = format(val, '01b')
            f_out.write(s+"\t")
            success = 1
        except ValueError:
            print("Please enter a '1' or a '0'") 
    success = 0
    #RESULT
    while success == 0:
        user_input = raw_input("Expected Result: ")
        try:
            if user_input[0:2] == "0x":
                val = int(user_input[2:], 16)
            elif user_input[0:2] == "0b":
                val = int(user_input[2:], 2)
            else:
                val = int(user_input)
            s = format(val, '032b')
            s = " ".join(s[i:i+4] for i in range(0, len(s), 4))
            f_out.write(s+"\t")
            success = 1
        except ValueError:
            print("Please enter a valid number.")
    #RESULT2
    if result2:
        success = 0
        while success == 0:
            user_input = raw_input("Expected Result2: ")
            try:
                if user_input[0:2] == "0x":
                    val = int(user_input[2:], 16)
                elif user_input[0:2] == "0b":
                    val = int(user_input[2:], 2)
                else:
                    val = int(user_input)
                s = format(val, '032b')
                s = " ".join(s[i:i+4] for i in range(0, len(s), 4))
                f_out.write(s+"\n")
                success = 1
            except ValueError:
                print("Please enter a valid number.")
    else:
        f_out.write(".... .... .... .... .... .... .... ....\n")

print("Tests created. Load your "+name+".X, .Y and .S files into a copy of your alu harness, which you should call '"+name+".circ'.")
print("Move your '"+name+".circ' file into your 'tests' folder.")
print("Add the following line to the list called 'tests' at the end of 'tests/sanity_test.py'")
print("(\""+name+" test\",TestCase(os.path.join(file_locations,'"+name+".circ'), os.path.join(file_locations,'"+name+".out'))),") 
f_X.close()
f_Y.close()
f_S.close()
f_out.close() 
