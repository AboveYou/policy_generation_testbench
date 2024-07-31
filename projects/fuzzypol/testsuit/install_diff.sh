#! /bin/bash

export LLVM_COMPILER="clang"
export LLVM_COMPILER_PATH="/lib/llvm-14/bin"
export LLVM_CC_NAME="clang-14"

ARCHIVE="diffutils-3.9.tar.xz"
LINK="https://ftp.gnu.org/gnu/diffutils/diffutils-3.9.tar.xz"
PROJ="diffutils-3.9"
BIN="diff"

ROOT=$(pwd)
PROJ_DIR=$ROOT/$PROJ/

apt install -y wget xz-utils tar

wget $LINK
tar xf $ARCHIVE && rm $ARCHIVE 
mkdir klee_ins afl_ins
cd $PROJ/
mkdir klee afl

cd $PROJ_DIR/klee
CC=wllvm FORCE_UNSAFE_CONFIGURE=1 ../configure --disable-nls CFLAGS="-g -O1 -Xclang -disable-llvm-passes -D__NO_STRING_INLINES  -D_FORTIFY_SOURCE=0 -U__OPTIMIZE__"
make -j$(nproc)
cd src
extract-bc -l $LLVM_COMPILER_PATH/llvm-link ./$BIN
cp $BIN $BIN.bc $ROOT/klee_ins/

cd $PROJ_DIR/afl
CC=afl-gcc FORCE_UNSAFE_CONFIGURE=1 CFLAGS="-L $GIT_REPO/customGLIBC/glibc/build/install/lib -I $GIT_REPO/customGLIBC/glibc/build/install/include/ -Wl,--rpath=$GIT_REPO/customGLIBC/glibc/build/install/lib"  ../configure
make -j$(nproc)
cd src
cp $BIN $ROOT/afl_ins/
