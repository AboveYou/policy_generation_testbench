# Overhead Measurements

libchestnut: 26288 Bytes, 26kB
libseccomp: 125360 Bytes, 123kB

combined: 151648 Bytes, 149kB
(would be 152kB)

libseccomp-2.5.5 was used

paper says (Sourcealyser, static):
- min +173kB
- max +219kB
difference are the list of syscalls + overhead from note section

average from the paper:
3448/18 = 192kB

for comparison (ls binary): 149480 Bytes, 149kB

paper says (Binalyzer, dynamic):
musl libc: +192kB 
libssl: +1048kB (1MB)
libcrypto: +1886000kB (18.9MB)

my tests on Sourcealyzer diff:
sa diff: 230512, 226kB
normal diff: 640984, 626kB
system diff: 137776, 135kB