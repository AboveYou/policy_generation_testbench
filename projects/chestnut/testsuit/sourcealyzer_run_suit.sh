#!/bin/bash

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

SA_BASE="/testsuit/sa"

BIN="diff"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $SA_BASE/diffutils-3.9/
    ./configure
    make -j $(nproc)
    cp src/$BIN /results/suit/sa/
popd

BIN="ls"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $SA_BASE/coreutils-9.5/
    ./configure
    make -j $(nproc)
    cp src/$BIN /results/suit/sa/
popd

BIN="tar"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $SA_BASE/tar-1.35/
    ./configure
    make -j $(nproc)
    cp src/$BIN /results/suit/sa/
popd

BIN="find"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $SA_BASE/findutils-4.8.0/
    ./configure
    make -j $(nproc)
    cp find/$BIN /results/suit/sa/
popd
