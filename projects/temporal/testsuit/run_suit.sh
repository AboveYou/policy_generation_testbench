#!/bin/bash

SA_BASE="/testsuit"

# allow unsafe configuration
export FORCE_UNSAFE_CONFIGURE=1

BIN="diff"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $SA_BASE/diffutils-3.9/
    ./configure AR=llvm-ar CC=clang CXX=clang++ LD=/usr/bin/ld CFLAGS="-flto -O0" CXXFLAGS="-flto -O0" LDFLAGS="-flto -Wl,-plugin-opt=save-temps"
    make
popd

BIN="ls"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $SA_BASE/coreutils-9.5/
    ./configure AR=llvm-ar CC=clang CXX=clang++ LD=/usr/bin/ld CFLAGS="-flto -O0" CXXFLAGS="-flto -O0" LDFLAGS="-flto -Wl,-plugin-opt=save-temps"
    make
popd

BIN="tar"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $SA_BASE/tar-1.35/
    ./configure AR=llvm-ar CC=clang CXX=clang++ LD=/usr/bin/ld CFLAGS="-flto -O0" CXXFLAGS="-flto -O0" LDFLAGS="-flto -Wl,-plugin-opt=save-temps"
    make
popd

BIN="find"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $SA_BASE/findutils-4.8.0/
    ./configure AR=llvm-ar CC=clang CXX=clang++ LD=/usr/bin/ld CFLAGS="-flto -O0" CXXFLAGS="-flto -O0" LDFLAGS="-flto -Wl,-plugin-opt=save-temps"
    make
popd
