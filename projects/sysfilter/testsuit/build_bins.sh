#!/bin/bash
export FORCE_UNSAFE_CONFIGURE=1
ROOT_DIR=$(pwd)
TEST_DIR=$ROOT_DIR/tests/
mkdir $TEST_DIR

apt update
apt install -y wget build-essential xz-utils

# clone and build diff
wget https://ftp.gnu.org/gnu/diffutils/diffutils-3.9.tar.xz
tar xf diffutils-3.9.tar.xz
pushd diffutils-3.9
./configure CFLAGS="-g"
make -j $(nproc)
cp src/diff $TEST_DIR
popd

# clone and build stat
wget https://ftp.gnu.org/gnu/coreutils/coreutils-9.5.tar.xz
tar xf coreutils-9.5.tar.xz
pushd coreutils-9.5
./configure CFLAGS="-g"
make -j $(nproc)
cp src/stat $TEST_DIR
cp src/ls $TEST_DIR
popd

# clone and build tar
wget https://ftp.gnu.org/gnu/tar/tar-1.35.tar.gz
tar xzf tar-1.35.tar.gz
pushd tar-1.35
./configure CFLAGS="-g"
make -j $(nproc)
cp src/tar $TEST_DIR
popd

# clone and build find
wget https://ftp.gnu.org/gnu/findutils/findutils-4.8.0.tar.xz
tar xf findutils-4.8.0.tar.xz
pushd findutils-4.8.0
./configure CFLAGS="-g"
make -j $(nproc)
cp find/find $TEST_DIR
popd
