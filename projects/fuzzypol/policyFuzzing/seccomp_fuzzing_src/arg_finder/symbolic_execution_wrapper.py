import os 
import subprocess
import glob
import shutil 

class SymbolicExecutionWrapper: 
    def __init__(self, main_script: str, bitcode: str, afl_instructed_bin: str, symargs: str, cov_dir: str, duration: str = "60"):

        if os.getuid() != 0: 
            print("[!] Script requires root prvileges")
            exit(-1)

        self.main_script = main_script
        self.bitcode = bitcode
        self.afl_instructed_bin = afl_instructed_bin
        self.symargs = symargs
        self.cov_dir = cov_dir
        self.duration = duration
        self.check_file_existance()

        print("[+] Successfully initialized the Symbolic Execution Wrapper:\n")


    def check_file_existance(self):
        if not os.path.exists(self.main_script):
            print("[!] SymbolicExecutionWrapper: Main Script path does not exist.")
            exit(-1)
        if not os.path.exists(self.bitcode):
            print("[!] SymbolicExecutionWrapper: Bitcode path does not exist.") 
            exit(-1)
        if not os.path.exists(self.afl_instructed_bin): 
            print("[!] SymbolicExecutionWrapper: AFL instructed bin path does not exist.") 
            exit(-1)


    def execute(self, debug:bool = True):
        print("[+] Starting KLEE with AFL")
        if debug: 
            subprocess.call(["sudo", "python3" , self.main_script, self.bitcode, self.afl_instructed_bin, self.symargs, "KS", self.cov_dir, self.duration])
        else:
            subprocess.call(["sudo", "python3" , self.main_script, self.bitcode, self.afl_instructed_bin, self.symargs, "KS", self.cov_dir, self.duration], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    def clear(self): 
        dir = os.path.abspath(os.path.join(self.main_script, os.pardir))
        del_dirs = glob.glob(f"{dir}/klee-out-*", recursive=True)
        
        if del_dirs: 
            del_dirs.append(f"{dir}/fuzzin.txt")
            del_dirs.append(f"{dir}/fuzzin_string.txt")
            del_dirs.append(f"{dir}/KLEEArgs1.txt")
            del_dirs.append(f"{dir}/{os.path.basename(self.afl_instructed_bin)}replay.txt")

        for item in del_dirs: 
            if os.path.isdir(item):
                try: 
                    print(os.chmod(item, 0o755))
                    print(item)
                except FileNotFoundError: 
                    continue 
            else: 
                print(item)



    def process_output(self): 
        basename = os.path.basename(self.afl_instructed_bin)

        base_dir = os.path.abspath(os.path.join(self.main_script, os.pardir))
        found_args = open(f"{base_dir}/fuzzin.txt", 'r')
        result_file = open(f"{basename}_flags.txt", 'w')

        for line in found_args: 
            result_file.write(f'"./ls" "{line.strip()}"\n')

        found_args.close()
        result_file.close()


    def get_result_file_name(self): 
        basename = os.path.basename(self.afl_instructed_bin)
        return os.path.join(os.getcwd(), f"{basename}_flags.txt")


if __name__ == "__main__": 
    pass
