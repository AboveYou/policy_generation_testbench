#! /bin/bash

LLVM_COMPILER="clang"
LLVM_COMPILER_PATH="/lib/llvm-14/bin"
LLVM_CC_NAME="clang-14"

# function to display the help message
help() {
    echo -e "Usage: $0 PROJ_PATH BIN_NAME\n"
    echo -e "\tPROJ_PATH: path to extracte archive"
    echo -e "\tBIN_NAME: name of the binary to build"
}

PROJ=$1
BIN=$2

if [ $# -lt 2 ]; then
    help 
    exit 1
fi

mkdir klee_ins afl_ins
cd $PROJ/
mkdir afl klee

cd $PROJ_DIR/klee
CC=wllvm FORCE_UNSAFE_CONFIGURE=1 ../configure --disable-nls CFLAGS="-g -O1 -Xclang -disable-llvm-passes -D__NO_STRING_INLINES  -D_FORTIFY_SOURCE=0 -U__OPTIMIZE__"
make -j$(nproc)
cd src
extract-bc -l $LLVM_COMPILER_PATH/llvm-link ./$BIN
# cp $BIN $BIN.bc $ROOT/klee_ins/

cd $PROJ_DIR/afl
CC=afl-gcc FORCE_UNSAFE_CONFIGURE=1 CFLAGS="-L $GIT_REPO/customGLIBC/glibc/build/install/lib -I $GIT_REPO/customGLIBC/glibc/build/install/include/ -Wl,--rpath=$GIT_REPO/customGLIBC/glibc/build/install/lib"  ../configure
make -j$(nproc)
cd src
cp $BIN $ROOT/afl_ins/
