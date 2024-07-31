#!/usr/bin/env python3
import json 
import configparser
import argparse
import os
import time
import BitVector
import subprocess
from io import StringIO
from fuzzer_main import prepare_environment
from pyseccomp import ALLOW, KILL, KILL_PROCESS, KILL_THREAD, LOG, NOTIFY
import syscall_finder 

from syscall_finder import harvest_syscalls
from arg_finder.symbolic_execution_wrapper import SymbolicExecutionWrapper
from afl_custom_mutator_arg_list_creator import arg_list_creator
from afl_custom_mutator_config_creator import create_config
from afl_custom_mutator_config_creator import prep_environment
from adjust_config import adjust_config
import syscall_validity_checker

from toggling_audisp_plugins import toggle_audisp_plugins
from bitset_extraction import extract_bitvector
import fuzzer_main

try: 
    import seccomp
except ImportError: 
    import pyseccomp as seccomp


def parse_json(syscall_input: str) -> dict:
    print(f"Parsing input for syscall-file {syscall_input}")
    syscall_file = open(syscall_input)
    syscall_file = syscall_file.read()
    return json.loads(syscall_file)


def read_config(config_filepath:str) -> configparser.ConfigParser: 
    config = configparser.ConfigParser()
    config.read(config_filepath)
    return config


def toggle_audisp_Plugins_with_Restart(file_finder= False, syscall_finder= False, syscall_file_finder= False, fuzzing_plugin= False):
    toggle_audisp_plugins.toggle_file_finder_plugin(file_finder)
    toggle_audisp_plugins.toggle_syscall_finder_plugin(syscall_finder)
    toggle_audisp_plugins.toggle_syscall_file_finder_plugin(syscall_file_finder)
    toggle_audisp_plugins.toggle_fuzzing_plugin(fuzzing_plugin)
    toggle_audisp_plugins.restart_auditd() 


def extract_syscall_numbers(syscall_json: dict, bwrap_syscalls_x86:list =[], bwrap_syscalls_x86_64:list =[]) -> tuple:
    print(f"Extracting systemcall: ")
    syscalls_x86 = list() 
    syscall_names_x86 = list()
    syscalls_x64 = list() 
    syscall_names_x64 = list()

    for key, value in syscall_json.items():
        if value['x86'] == 'allowed' or key in bwrap_syscalls_x86: 
            syscalls_x86.append(int(value['number']))
            syscall_names_x86.append(key)

        if value['x86_64'] == 'allowed' or key in bwrap_syscalls_x86_64: 
            syscalls_x64.append(int(value['number']))
            syscall_names_x64.append(key)

    print("Extracted Systemcalls for x86:")
    if syscall_names_x86:
        for item in syscall_names_x86:
            print(f"\t- {item}")
    else: 
        print("\t[-] No systemcalls for x86_64 found!")
    print("Extracted Systemcalls for x86_64:")
    if syscall_names_x64:
        for item in syscall_names_x64:
            print(f"\t- {item}")
    else: 
        print("\t[-] No systemcalls for x86_64 found!")

    return (syscalls_x64, syscalls_x86)
        

def remove_delta(bitmask_delta_file):
    bitmask_delta =  "/tmp/syscall_bitmask_delta"
    bitmask_normal = bitmask_delta_file

    with open(bitmask_normal, 'r') as syscall_bitmask_fstream: 
        fstream_input = StringIO(syscall_bitmask_fstream.read())
        syscall_bitmask_vector = BitVector.BitVector(fp =fstream_input)


    with open(bitmask_delta, 'r') as syscall_bitmask_fstream: 
        fstream_input = StringIO(syscall_bitmask_fstream.read())
        syscall_bitmask_delta = BitVector.BitVector(fp =fstream_input)
        
    finalized_syscall_vector = syscall_bitmask_vector & (~syscall_bitmask_delta)

    return finalized_syscall_vector

def create_bpf_filter_from_syscall_vector(syscall_BitVector_file: str, bpf_filter_path: str) -> bool: 
    print("\nCreating the syscall filter from the provided BitVector")

    if not os.path.exists(bpf_filter_path): 
        os.mkdir(bpf_filter_path)
    
    bitcall_mask = remove_delta(syscall_BitVector_file)

    default_action = KILL_PROCESS
    print_default_action(default_action)
    bpf_x86_64 =  seccomp.SyscallFilter(default_action)


    if not bpf_x86_64.exist_arch(seccomp.Arch.X86_64):
        bpf_x86_64.add_arch(seccomp.Arch.X86_64)

    if bpf_x86_64.exist_arch(seccomp.Arch.X86): 
        bpf_x86_64.remove_arch(seccomp.Arch.X86)

    for i in range(336): 
        try:
            if bitcall_mask[i]: 
                bpf_x86_64.add_rule(ALLOW, seccomp.resolve_syscall(seccomp.Arch.X86_64, i).decode())
        except PermissionError: 
            return False
        except OSError: 
            return False
    
    bpf_x86_64.add_rule(ALLOW, seccomp.resolve_syscall(seccomp.Arch.X86_64, 59).decode())

    x86_64_filter_file = open(bpf_filter_path + "/x86_64.bpf", "w")
    bpf_x86_64.export_bpf(x86_64_filter_file)

    print("[+] Successfully created the bpf filters")

    return True


def extend_path(file_path): 
    if file_path[0:2] == "./":
        file_name = file_path[2:]
        cwd = os.getcwd()
        extended_path = cwd + "/" + file_name
        return extended_path
    elif file_path[0] == '/': 
        return file_path
    else:
        return None


def print_default_action(default_action): 
    if default_action == KILL or default_action == KILL_THREAD: 
        print("[!] The default action is set to KILL.")
    elif default_action == KILL_PROCESS: 
        print("[!] The default action is set to KILL_PROCESS.")
    elif default_action == LOG: 
        print("[!] The default action is set to LOG.")
    elif default_action == NOTIFY: 
        print("[!] The default action is set to NOTIFY.")


def get_syscalls(config: list, args): 
    syscall_finder_afl_bin = extend_path(config['SYSCALLFINDER']['syscallfinder_afl_bin'])
    syscall_finder_args = args
    syscall_finder_output = extend_path(f"./{os.path.basename(syscall_finder_afl_bin)}_syscalls.json")

    harvester = harvest_syscalls.SyscallHarvester(syscall_finder_afl_bin, syscall_finder_args, config['FILEFINDER']['filefinder_bin'])
    syscalls_dict = harvester.harvest_syscalls()
    output_file = open(syscall_finder_output, 'w')
    json.dump(syscalls_dict, output_file)
    output_file.close()


def execute_arg_finder(config, duration:str = "180"):
    cwd = os.getcwd() 
    os.chdir("./arg_finder/")

    symbolic_execution_script = config['SYMBOLICEXECUTION']['symbolicexecution_script']
    bitcode = config['SYMBOLICEXECUTION']['bitcode']
    aflplusplus_executable = config['SYMBOLICEXECUTION']['aflplusplus_executable']
    cov_dir = config['SYMBOLICEXECUTION']['cov_dir']


    symbol_execution = SymbolicExecutionWrapper(symbolic_execution_script, bitcode, aflplusplus_executable, "30", cov_dir, duration)
    symbol_execution.execute()
    symbol_execution.process_output()

    result_file = symbol_execution.get_result_file_name()
    os.chdir(cwd)

    return result_file
    

def prepare_bitvector_file(binary_path): 
    ''' Function to transform gathered syscalls into a BitVector object und print the results to the according file 

    Return: 
        Path to the resultfile.
    '''
    bitvector = extract_bitvector.BitVectorExtraction(f"./{os.path.basename(binary_path)}_syscalls.json", f"./{os.path.basename(binary_path)}_syscalls.bits")
    bitvector.read_json_file() 
    bitvector.create_bitvector() 
    bitvector.print_bitvector_to_file() 

    return f"./{os.path.basename(binary_path)}_syscalls.bits"


def prepare_custom_mutator(config): 
    arg_list_creator.execute_arg_list_creator(config['SYMBOLICEXECUTION']['combined_flags'], "./afl_custom_mutator_arg_list_creator/transformed_input.txt", os.path.basename(config['FILEFINDER']['filefinder_bin']))
    create_config.create_config(config['AFL_CUSTOM_MUTATOR']['save_path'], config['AFL_CUSTOM_MUTATOR']['locations_file_path'], config['AFL_CUSTOM_MUTATOR']['existing_flags_paths']) 
    prep_environment.init_custom_mutator(config['AFL_CUSTOM_MUTATOR']['path_custom_mutator_dir'], config['AFL_CUSTOM_MUTATOR']['package_name'])


def find_valid_flag(config): 
    print("\n[+] Searching for a valid flag...")

    arg_file_path = config['SYMBOLICEXECUTION']['combined_flags']
    normal_bin = config['FILEFINDER']['filefinder_bin']

    with open(arg_file_path) as arg_file:
        args = arg_file.readlines() 

    result_list = list() 
    for item in args: 
        item = item.strip()
        result_list.append(item)


    for flag in result_list: 
        print(f"\t- Executing with flag {flag}")
        try: 
            subprocess.check_output([normal_bin, flag], stderr=subprocess.DEVNULL)
            break; 
        except subprocess.CalledProcessError: 
            print(f"\t\t ->Flag invalid")

    print(f"\n\t==>Found valid flag: {flag}\n")

    return flag


def generate_output(syscall_BitVector_file): 
    syscall_BitVector_file = f"{os.path.basename(syscall_BitVector_file)}_syscalls.bits"

    while not os.path.exists(syscall_BitVector_file): 
        time.sleep(1)

    with open(syscall_BitVector_file, 'r') as bitcall_mask_fstream: 
            fstream_input = StringIO(bitcall_mask_fstream.read())
            bitcall_mask = BitVector.BitVector(fp =fstream_input)
    
    print("\n=> Overview about found systemcalls:")

    for i in range(334):
        if bitcall_mask[i]: 
            print(seccomp.resolve_syscall(seccomp.Arch.X86_64, i).decode())


def main() -> None: 
    parser = argparse.ArgumentParser(description="Automatic Generation of Linux Sandbox Policies based on Bubblewrap")
    parser.add_argument("--bin_path", "-P", nargs=1, dest="bin_path", type=str, required=True, help="Path to Binary")
    parser.add_argument("--duration", "-d", dest="duration", type=str, required=False, help="Duration for the symbolic execution")
    parser.add_argument("--normal_bin_path", "-n", dest="normal_bin_path", required=False, help="Adjust the config, by setting the path to the new binary")
    parser.add_argument("--bitcode_file_path", "-bc", dest="bc_file_path", required=False, help="Path to the Bitcode of the analysed binary")
    parser.add_argument("--afl_instrumented_bin", "-afl", dest="afl_instrumented_bin", required=False, help="Path to the AFL instrumented binary")
    args = parser.parse_args()
    if args.normal_bin_path and (args.bc_file_path is None or args.afl_instrumented_bin is None): 
        parser.error("If normal bin path is set, -bc and -afl have to be set")
    
    if (not args.normal_bin_path is None) and (not args.bc_file_path is None) and (not args.afl_instrumented_bin is None): 
        adjust_config.adjust_config("pG_config.ini", args.normal_bin_path, args.bc_file_path, args.afl_instrumented_bin)
    
    
    config = read_config("pG_config.ini")

    syscall_validity_checker.create_tmp_diff_file("/tmp/syscall_bitmask_delta")    

    toggle_audisp_Plugins_with_Restart()
    execute_arg_finder(config, args.duration)


    toggle_audisp_Plugins_with_Restart(False, True)
    get_syscalls(config, config['SYMBOLICEXECUTION']['combined_flags'])

    parsed_json = parse_json(config['DEFAULT']['syscallfilepath'])

    
    extract_syscall_numbers(parsed_json, bwrap_syscalls_x86_64=["execve", "fcntl", "prctl", "wait4", "exit_group"])
    
    valid_flag = find_valid_flag(config)
    syscall_bitvector_file = prepare_bitvector_file(config['FILEFINDER']['filefinder_bin'])
    prepare_custom_mutator(config) 

    fuzzer_main.main(syscall_bitvector_file, "placeholder", config['SYSCALLFINDER']['syscallfinder_afl_bin'], valid_flag, config, args.duration)

    create_bpf_filter_from_syscall_vector(syscall_bitvector_file, config['DEFAULT']['bpfFilterPath'])
    generate_output(config['FILEFINDER']['filefinder_bin'])
    


if __name__ == "__main__": 
    # python3 ./policiesGenerator.py --bin_path /home/vagrant/examples/normal_bin/ls --duration 60 -n /home/vagrant/examples/normal_bin/ls -bc /home/vagrant/examples/klee_instructed/ls.bc -afl /home/vagrant/examples/afl_instructed/ls
    # python3 ./policiesGenerator.py --bin_path /home/vagrant/examples/normal_bin/file --duration 60 -n /home/vagrant/examples/normal_bin/file -bc /home/vagrant/examples/klee_instructed/file.bc -afl /home/vagrant/examples/afl_instructed/file
    # python3 ./policiesGenerator.py --bin_path /home/vagrant/examples/normal_bin/diff --duration 60 -n /home/vagrant/examples/normal_bin/diff -bc /home/vagrant/examples/klee_instructed/diff.bc -afl /home/vagrant/examples/afl_instructed/diff
    main()