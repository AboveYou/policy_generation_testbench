import sys
sys.path.append('/usr/local/lib/python3.11/site-packages/')

import os
import auparse 

def normalize_seccomp_event(au):
    normalized_seccomp_event = dict() 

    au.first_field() 


    while True: 
        field_name = au.get_field_name()

        if field_name == "comm": 
            normalized_seccomp_event['comm'] = au.get_field_str().strip('"') 
        if field_name == "syscall": 
            normalized_seccomp_event['syscall'] = int(au.get_field_str())

        
        if not au.next_field(): break

    return normalized_seccomp_event


def analyze_seccomp_log(log_file, comm_name): 
    ret_list = list()
    if not os.path.exists(log_file): 
        print("[!] Module seccomp analyze: Log File does not exist.")
        return 
    
    au = auparse.AuParser(auparse.AUSOURCE_FILE, log_file)

    while au.parse_next_event(): 
        normalized_seccomp_event = normalize_seccomp_event(au) 
        if "fuzzer_wrapper" != normalized_seccomp_event['comm'] and normalized_seccomp_event['syscall'] == 59: 
            print("\t[+] Special case: Found Execve")
            ret_list.append(normalized_seccomp_event['syscall'])
        elif "fuzzer_wrapper" == normalized_seccomp_event['comm'] and normalized_seccomp_event['syscall'] == 59:
            continue
        else:
            ret_list.insert(0, normalized_seccomp_event['syscall'])

    
    return ret_list


def main(): 
    log_file = "/tmp/fuzzing_tmp_dir/seccomp_messages"
    comm_name = "ls"
    print(analyze_seccomp_log(log_file, comm_name))

if __name__ == "__main__": 
    main()