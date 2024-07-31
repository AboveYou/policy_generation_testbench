#!/bin/bash

# function to display the help message
help() {
    echo -e "Usage: $0 BIN_PATH AFL_PATH KLEE_PATH DURATION\n"
    echo -e "\t BIN_PATH: path to normal binary"
    echo -e "\t AFL_PATH: path to afl instrumentation"
    echo -e "\t KLEE_PATH: path to klee bitcode"
    echo -e "\t DURATION: minutes to stop fuzzing (no new inputs found for DURATION min)"
}

BIN_PATH=$1
ALF_PATH=$2
KLEE_PATH=$3
DURATION=$3

if [ $# -lt 4 ]; then
    help 
    exit 1
fi

cd /fuzzypol/seccomp_fuzzing_src/

python3 ./policiesGenerator.py --bin_path $BIN_PATH --duration $DURATION -n $BIN_PATH -bc $KLEE_PATH -afl $AFL_PATH