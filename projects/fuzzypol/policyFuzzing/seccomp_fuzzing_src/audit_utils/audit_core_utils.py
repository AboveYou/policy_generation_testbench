import audit 
import BitVector
import sys 
from io import StringIO

def audit_filter_init(bitmask_vector):
    audit_kernel = audit.audit_open()

    for i in range(335): 
        if bitmask_vector[i]: 
            rule = audit.audit_rule_data() 
            audit.audit_rule_syscall_data(rule, i)
            audit.audit_add_rule_data(audit_kernel, rule, audit.AUDIT_FILTER_EXIT, audit.AUDIT_ALWAYS)
            

    audit.audit_close(audit_kernel)


def audit_filter_exit(bitmask_vector): 
    audit_kernel = audit.audit_open()

    for i in range(335): 
        if bitmask_vector[i]: 
            rule = audit.audit_rule_data() 
            audit.audit_rule_syscall_data(rule, i)
            audit.audit_delete_rule_data(audit_kernel, rule, audit.AUDIT_FILTER_EXIT, audit.AUDIT_ALWAYS)
    audit.audit_close(audit_kernel)

def main(mode): 
    bitmask_file_access = "001010100000000000000100000000000000000000000000000000001111100000000000000010000010011111101010000000000000000000000000000000000000110000000000000000000000000000000000000000000000000000001101101101100000000000000000000000000000000100010000000000000000000001011011111111000000000000000000000000000000000000000000000010000010000000000000000000000000000000000000" 
    syscall_new = "001010100000000000000100000000000000000000000000000000001111100000000000000010000010011111101010000000000000000000000000000000000000110000000000000000000000000000000000000000000000000000001101101101100000000000000000000000000000000100010000000000000000000001011011111111000000000000000000000000000000000000000000000010000010000000000000000000000000000000000000"
    bitmask_vector = BitVector.BitVector(fp = StringIO(syscall_new))
    if mode == "init": 
        audit_filter_init(bitmask_vector)
    else: 
        audit_filter_exit(bitmask_vector)


if __name__ == "__main__": 
    pass 