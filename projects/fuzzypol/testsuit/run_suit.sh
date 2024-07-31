#!/bin/bash

DURATION=3

BIN="diff"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $BIN
    ../run.sh $PWD/klee_ins/$BIN $PWD/afl_ins/$BIN $PWD/klee_ins/$BIN.bc $DURATION
popd

BIN="find"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $BIN
    ../run.sh $PWD/klee_ins/$BIN $PWD/afl_ins/$BIN $PWD/klee_ins/$BIN.bc $DURATION
popd

BIN="tar"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $BIN
    ../run.sh $PWD/klee_ins/$BIN $PWD/afl_ins/$BIN $PWD/klee_ins/$BIN.bc $DURATION
popd

BIN="ls"
echo -e "\nRunning $BIN"
echo -e "---------------------\n"
pushd $BIN
    ../run.sh $PWD/klee_ins/$BIN $PWD/afl_ins/$BIN $PWD/klee_ins/$BIN.bc $DURATION
popd
