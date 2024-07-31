#!/bin/bash

# function to display the help message
help() {
    echo -e "Usage: $0 BIN\n"
    echo -e "\tBIN: path to the binary"
}

BIN=$1

if [ $# -lt 1 ]; then
    help 
    exit 1
fi

# execute the binary with arguments
./sysfilter.elf -o /results/$BIN.json /results/$BIN
