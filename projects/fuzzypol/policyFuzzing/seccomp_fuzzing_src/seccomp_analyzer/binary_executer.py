import BitVector
import time
import sys
from io import StringIO
import os 
import subprocess 


def check_syscall_validity(syscall_bitvector: BitVector, checked_syscall: int, input: bytearray,binary_path: str): 
    tmp_syscall_bitvector = syscall_bitvector
    wrapper_path = "/home/vagrant/seccomp_fuzzing_src/seccomp_analyzer/fuzzer_wrapper"
    #tmp_syscall_bitvector_file = "/home/vagrant/seccomp_fuzzing_src/execute_without_wrapper/tmp_bitmask.bits"
    tmp_syscall_bitvector_file = "/home/vagrant/seccomp_fuzzing_src/seccomp_analyzer/tmp_bitmask.bits"

    tmp_syscall_bitvector[checked_syscall] = 0
    write_bitmask_to_file(tmp_syscall_bitvector_file, tmp_syscall_bitvector)
    tmp_syscall_bitvector[checked_syscall] = 1
    
    child_env = os.environ.copy() 
    child_env["PG_BITVECTOR_FILE"] = tmp_syscall_bitvector_file
    child_env["PG_BIN_NAME"] = binary_path



    wrapper_process_input = subprocess.Popen(["echo", input], stdout=subprocess.PIPE)
    wrapper_process_output = subprocess.Popen([wrapper_path], env = child_env, stdin=wrapper_process_input.stdout, stdout=subprocess.PIPE)
    #wrapper_process_output = subprocess.Popen([wrapper_path], env = child_env, stdin=wrapper_process_input.stdout)
    wrapper_process_output.communicate()
    ret_value = wrapper_process_output.returncode

    if ret_value == -31: 
        print(f"\t[i] Syscall {checked_syscall} seems to be important for the binary")
        return True 
    else: 
        print(f"\t[!] Syscall {checked_syscall} seems to be not important for the binary")#
        return False 


def write_bitmask_to_file(syscall_bitmask_file:str, bitvector: BitVector):
    with open(syscall_bitmask_file, 'w') as fstream: 
        fstream.write(str(bitvector)) 


if __name__ == "__main__": 
    with open("../ls_syscalls.bits", 'r') as syscall_bitmask_fstream: 
        fstream_input = StringIO(syscall_bitmask_fstream.read())
        syscall_bitmask = BitVector.BitVector(fp =fstream_input)
    binary_path = "/syscall_file_fuzzer/coretutils_for_policy_generation/normal_bin/ls"
    result_file = "./result_syscall_bitcheck"
    
    syscall_bitmask[50] = 1
    for i in range(336): 
        if syscall_bitmask[i]: 
            check_syscall_validity(syscall_bitmask, i, "-l", binary_path, result_file)

    #check_syscall_validity_2(syscall_bitmask, 50, "-l", binary_path, result_file)
    
