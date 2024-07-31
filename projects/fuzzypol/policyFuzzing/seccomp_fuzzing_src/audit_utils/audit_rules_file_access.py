import BitVector
import sys 
from io import StringIO
import audit_utils.audit_core_utils 

file_access_bitvector_str  = "001010100000000000000100000000000000000000000000000000001111100000000000000010000010011111101010000000000000000000000000000000000000110000000000000000000000000000000000000000000000000000001101101101100000000000000000000000000000000100010000000000000000000001011011111111000000000000000000000000000000000000000000000010000010000000000000000000000000000000000000" 

def generate_audit_filter(syscall_file_path: str): 
    global file_access_bitvector_str

    with open(syscall_file_path, 'r') as syscall_file: 
        syscall_bitmask_vector_str = syscall_file.read() 

    syscall_bitmask_vector = BitVector.BitVector(fp = StringIO(syscall_bitmask_vector_str))
    file_access_bitmask_vector = BitVector.BitVector(fp = StringIO(file_access_bitvector_str))

    relevant_syscalls = syscall_bitmask_vector & file_access_bitmask_vector

    relevant_syscalls[56] = True #clone
    relevant_syscalls[57] = True #fork 
    relevant_syscalls[58] = True #vfork

    print(relevant_syscalls)
    
    audit_utils.audit_core_utils.audit_filter_init(relevant_syscalls)
    

def destroy_audit_filter(syscall_file_path: str):
    global file_access_bitvector_str

    with open(syscall_file_path, 'r') as syscall_file: 
        syscall_bitmask_vector_str = syscall_file.read() 

    syscall_bitmask_vector = BitVector.BitVector(fp = StringIO(syscall_bitmask_vector_str))
    file_access_bitmask_vector = BitVector.BitVector(fp = StringIO(file_access_bitvector_str))

    relevant_syscalls = syscall_bitmask_vector & file_access_bitmask_vector

    relevant_syscalls[56] = True #clone 
    relevant_syscalls[57] = True #fork 
    relevant_syscalls[58] = True #vfork

    audit_utils.audit_core_utils.audit_filter_exit(relevant_syscalls)


def get_used_syscall_bitmask(syscall_file_path: str): 
    global file_access_bitvector_str

    with open(syscall_file_path, 'r') as syscall_file: 
        syscall_bitmask_vector_str = syscall_file.read() 

    syscall_bitmask_vector = BitVector.BitVector(fp = StringIO(syscall_bitmask_vector_str))
    file_access_bitmask_vector = BitVector.BitVector(fp = StringIO(file_access_bitvector_str))

    relevant_syscalls = syscall_bitmask_vector & file_access_bitmask_vector


    relevant_syscalls[57] = True #fork 
    relevant_syscalls[58] = True #vfork
    relevant_syscalls[59] = True #execve
    relevant_syscalls[322] = True #execveat

    return str(relevant_syscalls)

def main(syscall_file_path: str): 
    destroy_audit_filter(syscall_file_path)


if __name__ == "__main__": 
    pass