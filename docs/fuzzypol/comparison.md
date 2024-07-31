# Comparison
Fuzzypol vs. Sysfilter

## ls 
**fuzzypol**
read, write, close, lseek, mmap, mprotect, munmap, brk, rt_sigaction, rt sigprocmask, ioctl, pread64, access, socket, connect, uname, getcwd, readlink, capget, statfs, prctl, arch prctl, getxattr, lgetxattr, futex, getdents64,set tid address, exit group, openat, newfstatat, set robust list, prlimit64, statx
32 calls

**sysfilter**
ls:
0,1,3,7,8,9,10,11,12,13,14,15,16,17,19,20,25,28,39,41,42,44,45,47,52,54,60,63,72,79,89,96,99,102,104,107,108,115,143,144,145,146,147,186,201,202,204,217,228,231,234,257,262,269,302,307,318,332,439
59 calls

stat:
0,1,3,7,8,9,10,11,12,13,14,15,16,17,19,20,25,28,39,41,42,44,45,47,52,54,60,63,72,79,80,81,89,96,99,102,104,107,108,115,137,143,144,145,146,147,186,201,202,204,217,228,231,234,257,262,269,302,307,318,332,439
62 calls

**cmp**
ls: +84% (+27 calls) auf die eigentlich benötigten
stat: +94 (+30 calls)

## diff
**fuzzypol**
access, arch prctl, brk, clone, close, dup2, execve, exit group, fnctl, ioctl, lseek, mmap, mprotect, munmap, newfstatat, openat, pipe, pread64, read, rt_sigaction, sigaltstack, wait4, write, stat, lstat
25 calls

**sysfilter**
0,1,3,8,9,10,11,12,13,14,15,16,17,20,25,27,28,33,39,56,59,60,61,72,79,89,96,99,131,143,144,145,146,147,186,201,202,204,217,228,231,234,257,262,273,293,302,318
48 calls

check for the ones not found:
stat (sys number 4)
lstat (sys number 6)
> both were not found as well

**cmp**
diff: +92% (+23 calls) auf die eigentlich benötigten
