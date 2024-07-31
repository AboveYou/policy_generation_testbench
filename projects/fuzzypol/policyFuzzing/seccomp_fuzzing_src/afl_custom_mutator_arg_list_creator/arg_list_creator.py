import os 
from sys import exit

def execute_arg_list_creator(arg_file: str, out_file: str, basename: str)-> None: 
    arg_vector = list() 

    if not os.path.exists(arg_file): 
        print("[!] Arg File does not exist")
        exit(-1)

    with open(arg_file, 'r') as arg_file_opened: 
        arg_vector = arg_file_opened.readlines() 

    arg_vector = [arg.strip() for arg in arg_vector]

    valid_arg_vector = list() 
    invalid_arg_vector = list() 

    for arg in arg_vector: 
        if not arg:
            continue
        if arg[0] != "-": 
            invalid_arg_vector.append(arg)
        else:
            valid_arg_vector.append(arg)

    for arg in valid_arg_vector.copy(): 
        if len(arg.split()) > 1: 
            valid_arg_vector.remove(arg)

    with open(out_file, 'w') as out_file_opened:
        for item in valid_arg_vector: 
            item += "\n"
            out_file_opened.write(item)


if __name__ == "__main__": 
    pass