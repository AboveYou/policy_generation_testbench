import configparser 
import os
import sys 
from shutil import copyfile, copy


def prepare_symbol_execution(bc_file_path, afl_instrumented_bin):
    if not os.path.exists(bc_file_path): 
        print("[!]  Specified Bitcode Path for the Symbolic Execution does not exist.")
        sys.exit(-1)
    
    if not os.path.exists(afl_instrumented_bin): 
        print("[!]  Specified AFL instrumented Binary Path for the Symbolic Execution does not exist.")
        sys.exit(-1)
    
    copy(bc_file_path, "./arg_finder/")
    copy(afl_instrumented_bin, "./arg_finder/")


def adjust_config(current_config_path, normal_bin, bc_file_path, afl_instrumented_bin ): 
    config = configparser.ConfigParser()
    config.read(current_config_path)

    bin_basename = os.path.basename(normal_bin) 
    
    config['DEFAULT']['syscallfilepath'] = f"./{bin_basename}_syscalls.json"

    prepare_symbol_execution(bc_file_path, afl_instrumented_bin)
    config['SYMBOLICEXECUTION']['bitcode'] = os.path.basename(bc_file_path)
    config['SYMBOLICEXECUTION']['aflplusplus_executable'] = os.path.basename(afl_instrumented_bin)

    config['SYSCALLFINDER']['syscallfinder_afl_bin'] = afl_instrumented_bin


    config['FILEFINDER']['filefinder_bin'] = normal_bin
    config['FILEFINDER']['filefinder_bwrap_mount_string_file'] = f"./file_finder/{bin_basename}_file_access.txt"


    with open("pG_config.ini", 'w') as configfile: 
        config.write(configfile)


if __name__ == "__main__": 
    pass