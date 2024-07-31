#!/bin/bash

# function to display the help message
help() {
    echo -e "Usage: $0 BIN_NAME\n"
    echo -e "\tBIN_NAME: name of the binary to build"
}

BIN=$1

if [ $# -lt 1 ]; then
    help 
    exit 1
fi

# run Binalyzer
pushd $BA
    # delete last output
    rm -r cached_results/ modified_binaries/
    # copy the binary
    cp /results/$BIN ./
    # run the analysis
    python3 filter.py $BIN
    # copy the results
    cp cached_results/syscalls_allowed*$BIN.json /results/
popd