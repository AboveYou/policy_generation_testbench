import os 
import sys
import subprocess
import json 
import BitVector
import time 

parent_dir = os.path.abspath('.')
sys.path.insert(1, parent_dir)
import syscall_validity_checker
import policiesGenerator



class SyscallHarvester: 
    def __init__(self, bin_name: str, flag_file: str, uninstrumented_bin: str, debug: bool =False):
        self.flag_file = flag_file
        self.bin_name = bin_name
        self.flags = list()
        self.uninstrumented_bin = uninstrumented_bin
        self.syscall_bitvector = BitVector.BitVector(size=360) 

        for i in range(336):
            self.syscall_bitvector[i]= 0 

        if debug == True:  
            self.debug = subprocess.DEVNULL
        else:
            self.debug = subprocess.STDOUT
        
        
        if not os.path.isfile(self.flag_file):
            print('No valid argument file provided!')
            exit(1)
        
        self.flags = open(self.flag_file, 'r')
        

    def harvest_syscalls(self):
        print(f"\n\nStarting gathering syscalls for {self.bin_name}\n")
        i = 0; 
        syscall_list = dict()
        failed_flags = list() 

        open(f'./{os.path.basename(self.bin_name)}_syscalls.json', 'w')

        for line in self.flags.readlines(): 
            '''try: 
                flag = [item.strip('"') for item in line.split()][1]
            except IndexError: 
                print("IIIIII")
                continue'''
            flag = line

            flag = flag.strip() 
            if flag == '': 
                continue

            i += 1 
            if str.isprintable(flag): 
                print(f"[{i}] Execution of Syscall-Finder\tFlag = {flag}")
            else:
                print(f"[{i}] Execution of Syscall-Finder with non printable arg of order: {[ord(item) for item in flag]}")

            if subprocess.call(['sudo', 'python3', './syscall_finder/main.py', '-k', '-d', '50000', f"{self.bin_name}", flag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0: 
                subprocess.call(['sudo', 'systemctl', 'reset-failed', 'auditd'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if subprocess.call(['sudo', 'python3', './/syscall_finder/main.py', '-k', '-d', '50000', f"{self.bin_name}", flag],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0: 
                    failed_flags.append(flag)    

            while not os.path.exists(f'./{os.path.basename(self.bin_name)}_syscalls.json'): 
                time.sleep(1)

            with open(f'./{os.path.basename(self.bin_name)}_syscalls.json', 'r') as syscalls_json: 
                tmp_syscall_list = json.load(syscalls_json) 
                syscalls_json.close()

            if i==1: 
                syscall_list = tmp_syscall_list
                for syscall, attributes in tmp_syscall_list.items(): 
                    if (tmp_syscall_list[syscall][list(attributes.items())[1][0]] == 'allowed'):
                        print(f"\t[+] Adding syscall for architectur x86: {syscall}")
                    if (tmp_syscall_list[syscall][list(attributes.items())[2][0]] == 'allowed'):
                        print(f"\t[+] Adding syscall for architectur x86_64: {syscall}")
                        
                        syscall_number = int(syscall_list[syscall][list(attributes.items())[0][0]])
                        self.syscall_bitvector[syscall_number] = 1
                        self.analyse_syscall_log_without_wrapper(syscall_number, flag)
            else: 
                for syscall, attributes in tmp_syscall_list.items(): 
                    if (tmp_syscall_list[syscall][list(attributes.items())[1][0]] == 'allowed' and 
                            syscall_list[syscall][list(attributes.items())[1][0]] == 'blocked'):
                        print(f"\t[+] Adding syscall for architectur x86: {syscall}")
                        syscall_list[syscall][list(attributes.items())[1][0]] = 'allowed' 
                    if (tmp_syscall_list[syscall][list(attributes.items())[2][0]] == 'allowed' and 
                            syscall_list[syscall][list(attributes.items())[2][0]] == 'blocked'):
                        print(f"\t[+] Adding syscall for architectur x86_64: {syscall}")
                        syscall_list[syscall][list(attributes.items())[2][0]] = 'allowed'
                        
                        syscall_number = int(syscall_list[syscall][list(attributes.items())[0][0]])
                        self.syscall_bitvector[syscall_number] = 1
                        self.analyse_syscall_log_without_wrapper(syscall_number, flag)

        return syscall_list
    

    def analyse_syscall_log_without_wrapper(self, syscall_number: int, input: str): 
        syscall_validity_checker.check_validity(self.syscall_bitvector, syscall_number, input, self.uninstrumented_bin, "/tmp/syscall_bitmask_delta")
        policiesGenerator.toggle_audisp_Plugins_with_Restart(False, True)
        time.sleep(2)


if __name__ == "__main__":  
    pass