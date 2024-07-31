#!/bin/bash

# test must be executed in Binalyzer directory
pushd $BA/
# make sure there are no previous files
# rm -r cached_results/ modified_binaries/

SUIT_DIR="/testsuit/ba/tests/"
RES_DIR="/results/suit/ba"

# run diff
BIN="diff"
BIN_PATH=$SUIT_DIR$BIN
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
python3 filter.py $BIN_PATH
cp cached_results/syscalls_allowed*$BIN.json $RES_DIR/$BIN.json  
rm -r cached_results/ modified_binaries/

# run tar
BIN="tar"
BIN_PATH=$SUIT_DIR$BIN
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
python3 filter.py $BIN_PATH
# mkdir /results/tar/
cp cached_results/syscalls_allowed*$BIN.json $RES_DIR/$BIN.json
rm -r cached_results/ modified_binaries/

# run stat
BIN="stat"
BIN_PATH=$SUIT_DIR$BIN
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
python3 filter.py $BIN_PATH
# mkdir /results/stat/
cp cached_results/syscalls_allowed*$BIN.json $RES_DIR/$IN.json
rm -r cached_results/ modified_binaries/

# run ls
BIN="ls"
BIN_PATH=$SUIT_DIR$BIN
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
python3 filter.py $BIN_PATH
# mkdir /results/stat/
cp cached_results/syscalls_allowed*$BIN.json $RES_DIR/$BIN.json  
rm -r cached_results/ modified_binaries/

# run find
BIN="find"
BIN_PATH=$SUIT_DIR$BIN
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
python3 filter.py $BIN_PATH
# mkdir /results/find/
cp cached_results/syscalls_allowed*$BIN.json $RES_DIR/$BIN.json  
rm -r cached_results/ modified_binaries/

popd