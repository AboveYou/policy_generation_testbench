# Overhead Measurements

the library is created and directly linked to the binary

testing with ls:
- before: 151344 Bytes, 151kB
- after: 153920 Bytes 154kB

difference: 3kB
there is only one syscall in the policy

the library adds:
- libsysfilter-ls: 15536 Bytes, 16kB

when enforcing 10 syscalls:
- binary: 153920 Bytes (the same)
- library: 15536 Bytes

-> library seems to have constant size (all flagged syscalls have to be included)