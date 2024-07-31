#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <sourcecode_dir_path>"
    exit 1
fi

# print all commands to the terminal
set -x

# move into source code build dir
pushd $1

# configure and build sourcecode (this might need to be adjusted)
./configure AR=llvm-ar CC=clang CXX=clang++ LD=/usr/bin/ld CFLAGS="-flto -O0" CXXFLAGS="-flto -O0" LDFLAGS="-flto -Wl,-plugin-opt=save-temps"
make

popd