import os
from tabnanny import check 
import time
from io import StringIO
import BitVector
from seccomp_analyzer import analyze_seccomp_log, binary_executer
import fuzzer_main
from toggling_audisp_plugins import toggle_audisp_plugins


def check_validity(syscall_bitvector: BitVector, checked_syscall: int, input: bytearray,binary_path: str, result_file: str): 
    time.sleep(2)
    with open(result_file, 'r') as syscall_bitmask_fstream: 
        fstream_input = StringIO(syscall_bitmask_fstream.read())
        delta_syscall_bitvector = BitVector.BitVector(fp =fstream_input)

    syscall_bitvector = (syscall_bitvector | delta_syscall_bitvector) ^ delta_syscall_bitvector
    tmp_delta_syscalls_indices = list() 
    for x in range(336): 
        if delta_syscall_bitvector[x]: 
            tmp_delta_syscalls_indices.append(x) 

    
    seccomp_logs = seccomp_logs = "/tmp/fuzzing_tmp_dir/seccomp_messages"
    fuzzer_main.start_audisp_plugin() 
    if binary_executer.check_syscall_validity(syscall_bitvector, checked_syscall, input, binary_path):
        time.sleep(2)
        toggle_audisp_plugins.restart_auditd()
        new_syscalls = analyze_seccomp_log.analyze_seccomp_log(seccomp_logs, os.path.basename(binary_path))
        #print(new_syscalls)
        if new_syscalls[0] == checked_syscall: 
            return True 
        elif new_syscalls[0] in tmp_delta_syscalls_indices:
            print(f"[Syscall {new_syscalls[0]} erroneously found in delta in delta syscalls: Removing it from list...")
            with open(result_file, 'r') as syscall_bitmask_fstream: 
                fstream_input = StringIO(syscall_bitmask_fstream.read())
                existing_validity_syscall_bitvector = BitVector.BitVector(fp =fstream_input)
            
            existing_validity_syscall_bitvector[new_syscalls[0]] = 0

            with open(result_file, 'w') as result_file_stream: 
                result_file_stream.write(str(existing_validity_syscall_bitvector))
            return False            
        else: 
            return False 
    else: 
        with open(result_file, 'r') as syscall_bitmask_fstream: 
            fstream_input = StringIO(syscall_bitmask_fstream.read())
            existing_validity_syscall_bitvector = BitVector.BitVector(fp =fstream_input)
        
        existing_validity_syscall_bitvector[checked_syscall] = 1

        with open(result_file, 'w') as result_file_stream: 
            result_file_stream.write(str(existing_validity_syscall_bitvector))
        return False


def create_tmp_diff_file(result_file: str):
    if not os.path.exists(result_file): 
        syscall_bitvector_copy = BitVector.BitVector(size=360) 
        for i in range(336):
            syscall_bitvector_copy[i] = 0 

        syscall_bitvector_copy[30] = 1
        syscall_bitvector_copy[31] = 1

        with open(result_file, 'w') as result_file_stream: 
            result_file_stream.write(str(syscall_bitvector_copy))


if __name__ == "__main__": 
    pass 