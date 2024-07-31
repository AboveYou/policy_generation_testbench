#!/bin/bash

ROOT_DIR=$(pwd)

apt update
apt install -y wget build-essential xz-utils

# clone diff
wget https://ftp.gnu.org/gnu/diffutils/diffutils-3.9.tar.xz
tar xf diffutils-3.9.tar.xz
rm diffutils-3.9.tar.xz

# clone stat
wget https://ftp.gnu.org/gnu/coreutils/coreutils-9.5.tar.xz
tar xf coreutils-9.5.tar.xz
rm coreutils-9.5.tar.xz

# clone tar
wget https://ftp.gnu.org/gnu/tar/tar-1.35.tar.gz
tar xzf tar-1.35.tar.gz
rm tar-1.35.tar.gz

# clone find
wget https://ftp.gnu.org/gnu/findutils/findutils-4.8.0.tar.xz
tar xf findutils-4.8.0.tar.xz
rm findutils-4.8.0.tar.xz
