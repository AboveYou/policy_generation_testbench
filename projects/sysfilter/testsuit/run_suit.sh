#!/bin/bash

SUIT_DIR="/testsuit/tests/"
RES_DIR="/results/suit/"
# RES_DIR="/testsuit/results/"

# create output dir (exists)
# mkdir $RES_DIR

# execute diff
BIN="diff"
echo -e "\n[-] Running $BIN"
./sysfilter.elf -o $RES_DIR/$BIN.json $SUIT_DIR/$BIN

# execute tar
BIN="tar"
echo -e "\n[-] Running $BIN"
./sysfilter.elf -o $RES_DIR/$BIN.json $SUIT_DIR/$BIN

# execute find
BIN="find"
echo -e "\n[-] Running $BIN"
./sysfilter.elf -o $RES_DIR/$BIN.json $SUIT_DIR/$BIN

# execute stat
BIN="stat"
echo -e "\n[-] Running $BIN"
./sysfilter.elf -o $RES_DIR/$BIN.json $SUIT_DIR/$BIN

# execute ls
BIN="ls"
echo -e "\n[-] Running $BIN\n"
./sysfilter.elf -o $RES_DIR/$BIN.json $SUIT_DIR/$BIN