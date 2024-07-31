#!/bin/bash

# function to display the help message
help() {
    echo -e "Usage: $0 DIR_NAME BIN_NAME\n"
    echo -e "\tDIR_NAME: name of the source code directory (no archive) in resutls/"
    echo -e "\tBIN_NAME: name of the binary to build"
}

DIR=$1
BIN=$2

if [ $# -lt 2 ]; then
    help 
    exit 1
fi

# allow unsafe configuration
export FORCE_UNSAFE_CONFIGURE=1

# flags to select the chestnut 
export LLVM_COMPILER="clang"
export LLVM_CC_NAME="clang-10"
export CFLAGS="-fuse-ld=lld"
export CC="/chestnut/Sourcealyzer/llvm10/build/bin/clang"
export LD="/chestnut/Sourcealyzer/llvm10/build/bin/ld.lld"
export CPP="/chestnut/Sourcealyzer/llvm10/build/bin/clang++ -E"
export LLVM_COMPILER_PATH="/chestnut/Sourcealyzer/llvm10/build/bin"
export LLVM_CONFIG="/chestnut/Sourcealyzer/llvm10/build/bin/llvm-config"

pushd $SA
    cp -r $DIR ./
    cd $DIR/
    ./configure
    make -j $(nproc)
    cp src/$BIN /results/
popd
