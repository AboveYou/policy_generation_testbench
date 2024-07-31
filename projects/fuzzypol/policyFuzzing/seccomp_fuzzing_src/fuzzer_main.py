import sys
import os 
import subprocess
import BitVector
import time 
import re
import shutil 
import json 
import configparser
from io import StringIO
from toggling_audisp_plugins import toggle_audisp_plugins
from seccomp_analyzer import analyze_seccomp_log
from audit_utils import audit_rules_file_access
import syscall_validity_checker

fuzzer_wrapper = "/home/vagrant/seccomp_fuzzing_src/wrapper/fuzzer_wrapper"
seccomp_logs = "/tmp/fuzzing_tmp_dir/seccomp_messages"
input_dir = "/fuzzing/in"
output_dir = "/fuzzing/out"
duration = "60"
tmp_testcase_dir = "/tmp/fuzzing_testcases"
normal_bin_path = ""

def start_audisp_plugin(): 
    toggle_audisp_plugins.toggle_syscall_finder_plugin()
    toggle_audisp_plugins.toggle_file_finder_plugin()
    toggle_audisp_plugins.toggle_syscall_file_finder_plugin(True)
    toggle_audisp_plugins.toggle_fuzzing_plugin(True)
    toggle_audisp_plugins.restart_auditd()

def explore_missing_syscall_bits(instrumented_binary: str, bitcall_mask_file: str, valid_input: str): 
    global seccomp_logs
    global normal_bin_path
    ret_code = True
    already_explored_syscalls = list() 
    tmp_syscall_storage = -1

    with open("/tmp/file_input_new_syscalls.txt", 'a') as tmp_input_new_syscall:
        tmp_input_new_syscall.write(valid_input + "\n")

    print("[+] Exploring missing syscalls")

    with open(bitcall_mask_file, 'r') as syscall_bitmask_fstream: 
        fstream_input = StringIO(syscall_bitmask_fstream.read())
        syscall_bitmask = BitVector.BitVector(fp =fstream_input)

    fuzzer_env = os.environ.copy()
    while ret_code: 
        print(f"[i] A valid input is: {valid_input}")

        wrapper_process_input = subprocess.Popen(["echo", valid_input], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        wrapper_process_output = subprocess.Popen([fuzzer_wrapper], env = fuzzer_env,  stdin=wrapper_process_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        wrapper_process_output.communicate()
        ret_value = wrapper_process_output.returncode

        toggle_audisp_plugins.restart_auditd()

        if ret_value != 159 and ret_value != -31:
            print(f"\n\nEntering leavin with ret_value {ret_value}\n\n") 
            ret_code = False 
        
        new_syscalls = analyze_seccomp_log.analyze_seccomp_log(seccomp_logs, os.path.basename(instrumented_binary))
        if new_syscalls:
            for item in new_syscalls: 
                if item in already_explored_syscalls: 
                    continue
                print(f"\tFound Syscall with number {item}")
                syscall_bitmask[item] = True 
                syscall_validity_checker.check_validity(syscall_bitmask, item, valid_input, normal_bin_path, "/tmp/syscall_bitmask_delta")
                already_explored_syscalls.append(item)
                write_bitmask_to_file(bitcall_mask_file, syscall_bitmask)
        else:
            break
        if tmp_syscall_storage == item: 
            break 

        tmp_syscall_storage = item 
        time.sleep(2)
        
        
def write_bitmask_to_file(syscall_bitmask_file:str, bitvector: BitVector):
    print(f"\t[i]Writing Bitsmask to file with path: {syscall_bitmask_file} ")
    with open(syscall_bitmask_file, 'w') as fstream: 
        fstream.write(str(bitvector))  


def execute_binary_with_wrapper(instrumented_binary: str, bitcall_mask_file: str, valid_input: str): 
    global fuzzer_wrapper
    global seccomp_logs

    fuzzer_env = os.environ.copy()

    wrapper_process_input = subprocess.Popen(["echo", valid_input], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    wrapper_process_output = subprocess.Popen([fuzzer_wrapper], env = fuzzer_env, stdin=wrapper_process_input.stdout, stdout=subprocess.PIPE,  stderr=subprocess.DEVNULL)
    wrapper_process_output.communicate()

    ret_value = wrapper_process_output.returncode

    if ret_value == 0: 
        print("[+] The input seems to work with the chosen seccomp filter.")
        return 

    print("[!] The input does not work with the provided seccomp filter:\n")

    explore_missing_syscall_bits(instrumented_binary, bitcall_mask_file, valid_input)
    

def execute_fuzzing_process(instrumented_binary: str,  bitcall_mask_file: str, valid_input: str): 
    global duration
    global input_dir
    global output_dir
    global fuzzer_wrapper
    
    execute_binary_with_wrapper(instrumented_binary, bitcall_mask_file, valid_input)

    print(f"[+] AFL Fuzz will be executed with the following parameters:\n\tDuration={duration}\n\tInput dir={input_dir}\n\tOutput dir={output_dir}")
    time.sleep(2)

    audit_rules_file_access.generate_audit_filter(bitcall_mask_file)
    
    print(f"\n\nInputs:\nInput_dir = {input_dir}\nOutput_dir = {output_dir}\nFuzzer_wrapper = {fuzzer_wrapper}\nBitcall_mask_file = {bitcall_mask_file}\nInstrumented Binary = {instrumented_binary}")

    fuzzer_env = os.environ.copy()
    subprocess.run(["timeout", duration, "afl-fuzz", "-i", input_dir, "-o", output_dir, fuzzer_wrapper], env = fuzzer_env)

    audit_rules_file_access.destroy_audit_filter(bitcall_mask_file)

    toggle_audisp_plugins.restart_auditd() 

def check_for_crashes(): 
    global output_dir 

    print("[+] Checking output dir for crashes during fuzzing")

    output_list = os.listdir(os.path.join(output_dir, "default/crashes"))

    if not output_list or len(output_list) == 1: 
        print("\t=> No crashes detect")
        time.sleep(1)
        return False
    else: 
        print(f"\t=> Detected {len(output_list) -1} unique crashes")
        time.sleep(1)
        return True

def minimizing_test_cases(syscall_bitmask_file, instrumented_binary): 
    global fuzzer_wrapper
    global tmp_testcase_dir
    global output_dir 

    minimized_testcase_name = "minimized_testcase_"
    testcase_counter = 0 

    print("[+] Minimzing testcases: ")

    if not os.path.exists(tmp_testcase_dir): 
        os.mkdir(tmp_testcase_dir)

    crashing_test_cases = os.listdir(os.path.join(output_dir, "default/crashes"))

    for item in crashing_test_cases: 
        if item == "README.txt": 
            continue


        output_file = os.path.join(tmp_testcase_dir, f"{minimized_testcase_name}{str(testcase_counter)}")
        input_file = os.path.join(output_dir, "default/crashes")
        input_file = os.path.join(input_file, item)
        fuzzer_env = os.environ.copy()
        subprocess.run(["afl-tmin", "-i", input_file, "-o", output_file, "--", fuzzer_wrapper], env = fuzzer_env)

        testcase_counter += 1 

    purge_tmp_files(os.getcwd(), "\.afl-tmin-temp-*")


# Source: https://stackoverflow.com/questions/1548704/delete-multiple-files-matching-a-pattern
def purge_tmp_files(dir, pattern): 
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))


def execute_test_cases(bitcall_mask_file, instrumented_binary): 
    global tmp_testcase_dir

    print("[+] Executing the crashing test cases.")

    testcases = os.listdir(tmp_testcase_dir)


    for item in testcases: 
        with open(os.path.join(tmp_testcase_dir, item), 'r') as testcase_file: 
            testcase_data =testcase_file.read()

        print(f"\tExecuting test case {item} with test case data: {testcase_data}")
        explore_missing_syscall_bits(instrumented_binary,bitcall_mask_file, testcase_data)


def clean_tmp(): 
    log_dir =  "/tmp/syscall_file_fuzzer"

    log_files = os.listdir(log_dir) 
    
    for log_file in log_files: 
        os.remove(os.path.join(log_dir, log_file))


def prepare_environment(bitcall_mask_file, instrumented_binary): 
    global output_dir

    print("[+] Setting the necessary environment variables and deleting old files")
    os.environ["AFL_AUTORESUME"] = "1"
    os.environ["AFL_BENCH_UNTIL_CRASH"] = "1"
    os.environ["PG_BITVECTOR_FILE"] = bitcall_mask_file
    os.environ["PG_BIN_NAME"] = instrumented_binary
    if os.path.exists(os.path.join(output_dir, "default")): 
        shutil.rmtree(os.path.join(output_dir, "default"))


def adjust_inputfile(valid_input): 
    global input_dir 

    with open(os.path.join(input_dir, "input.txt"), 'w') as testcase_file: 
        testcase_file.write(valid_input)


def main(bitcall_mask_file: str, file_access_file: str, instrumented_binary: str, valid_input: str, config,  fuzzing_duration:str ="60"):
    global duration 
    global seccomp_logs 
    global input_dir 
    global output_dir 
    global tmp_testcase_dir
    global normal_bin_path

    seccomp_logs = config['FUZZING']['seccomp_logs']
    input_dir = config['FUZZING']['input_dir']
    output_dir  = config['FUZZING']['output_dir']
    tmp_testcase_dir = config['FUZZING']['tmp_testcase_dir']
    normal_bin_path = config['FILEFINDER']['filefinder_bin']

    duration = fuzzing_duration

    adjust_inputfile(valid_input)

    if not os.path.exists(bitcall_mask_file): 
        print("[1] Bitcall mask file path does not exist")
        sys.exit(-1)

    #if not os.path.exists(file_access_file): 
    #    print("[1] File access file path does not exist")
    #    sys.exit(-1)

    if not os.path.exists(instrumented_binary): 
        print("[1] Instrumented binary path does not exist")
        sys.exit(-1)

    with open(bitcall_mask_file, 'r') as bitcall_mask_fstream: 
        fstream_input = StringIO(bitcall_mask_fstream.read())
        bitcall_mask = BitVector.BitVector(fp =fstream_input)

    prepare_environment(bitcall_mask_file, instrumented_binary) 

    event_loop(bitcall_mask_file, file_access_file, instrumented_binary, valid_input)


def event_loop(bitcall_mask_file: str, file_access_file: str, instrumented_binary, valid_input: str):
    while True: 
        toggle_audisp_plugins.stop_auditd()
        time.sleep(2)
        clean_tmp() 
        start_audisp_plugin() 
        execute_fuzzing_process(instrumented_binary, bitcall_mask_file, valid_input) 
        if check_for_crashes(): 
            minimizing_test_cases(bitcall_mask_file, instrumented_binary)
            execute_test_cases(bitcall_mask_file, instrumented_binary)
        else: 
            break 
        
    toggle_audisp_plugins.stop_auditd()



if __name__ == "__main__": 
    pass 