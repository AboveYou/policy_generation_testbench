#define _DEFAULT_SOURCE 
#include <seccomp.h> 
#include <cstdlib> 
#include <iostream>
#include <string> 
#include <bitset> 
#include <streambuf> 
#include <algorithm> 
#include <fstream>
#include <sys/prctl.h> 
#include <unistd.h>
#include "argv-fuzz-inl-byte-restricted.h"

int main (int argc, char* argv[]){
    std::string input; 
    int syscall_counter; 
    scmp_filter_ctx ctx86_64= nullptr; 

    /* AFL is not intended to fuzz argument vectors. Instead argv has to be replaced after initial argv assignment. 

      The argv-fuzz-inl Header is the suggested solution from AFL. Altough its experimental and could lead to some crashes during fuzzing. 
    */
    AFL_INIT_SET0("fuzzer_wrapper"); 

    const char* bin_name = std::getenv("PG_BIN_NAME"); 
    const char* bitvector_file_path = std::getenv("PG_BITVECTOR_FILE"); 

    if (bin_name == NULL) {
	    return -1; 
    }

    if (bitvector_file_path == NULL) {
	    return -1; 
    }

    std::ifstream bitset_syscall_mask_file(bitvector_file_path);
    if (!bitset_syscall_mask_file.is_open()) {
        std::cerr << "[!] Could not open syscall bitset file\nFile: "<< bitvector_file_path << std::endl; 
    }
    bitset_syscall_mask_file >> input; 
    std::reverse(input.begin(), input.end());

    std::bitset<360> syscall_mask{input};

    std::cout << syscall_mask[0] << std::endl; 

    prctl(PR_SET_NO_NEW_PRIVS, 1); 

    ctx86_64 = seccomp_init(SCMP_ACT_KILL_PROCESS);

    seccomp_arch_remove(ctx86_64, SCMP_ARCH_NATIVE); 
    seccomp_arch_add(ctx86_64, SCMP_ARCH_X86_64);

    
    seccomp_rule_add(ctx86_64, SCMP_ACT_LOG, 59, 0);

    for (syscall_counter = 0; syscall_counter <= 335; syscall_counter++) {
        if (syscall_mask[syscall_counter] == 1){
            seccomp_rule_add(ctx86_64, SCMP_ACT_ALLOW, syscall_counter, 0);
        }
    }

    if (seccomp_load(ctx86_64) != 0) {
        std::cerr << "[!] Error initializing the seccomp filter." << std::endl; 
    }

    execv(bin_name, &argv[0]);

    seccomp_release(ctx86_64); 

    return 0; 
}
