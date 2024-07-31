from BitVector import BitVector
import sys 
import os
import json 

class BitVectorExtraction: 
    def __init__(self, syscall_json_file, save_file): 
        self.syscall_json_file = syscall_json_file
        self.save_file = save_file 
        self.syscall_data = dict() 
        self.bitvector = BitVector(size= 360)

    def read_json_file(self): 
        if not os.path.exists(self.syscall_json_file): 
            print("[!] Provided Syscall-JSON does not exist")
            sys.exit(-1)
        
        with open(self.syscall_json_file) as syscall_file:
            self.syscall_data = json.load(syscall_file)
    

    def create_bitvector(self): 
        syscall_number_counter = 0
        for syscall_name, value_field in self.syscall_data.items(): 
            for key, value in value_field.items(): 
                if (key ==  "x86_64" and value == "allowed"): 
                    self.bitvector[syscall_number_counter] = 1 
            syscall_number_counter += 1

    def print_bitvector_to_file(self): 
        with open(self.save_file, 'w') as bitvector_save_file: 
            bitvector_save_file.write(str(self.bitvector))


def main(): 
    bitvector = BitVectorExtraction("./ls_syscalls.json", "./ls_bitvector.bits")
    bitvector.read_json_file() 
    bitvector.create_bitvector() 
    bitvector.print_bitvector_to_file() 

if __name__ == "__main__": 
    main()