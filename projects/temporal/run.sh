#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <bytecode_path> <sourcecode_dir_path>"
    exit 1
fi

BC=$(basename $1 | cut -d "." -f 1)
DIR=$(dirname $1)
CALL_DIR="$DIR/callgraph"
REPO_ROOT="$2"

pushd $DIR

mkdir callgraph

# all commands are printed to the terminal
set -x

# create a dot call graph
wpa -print-fp -ander -dump-callgraph $1
python3 $REPO_ROOT/convertSvfCfgToHumanReadable.py callgraph_final.dot > $CALL_DIR/$BC.svf.type.cfg

spa -condition-cfg $1 2>&1 | tee $CALL_DIR/$BC.svf.conditional.direct.calls.cfg

spa -simple $1 2>&1 | tee $CALL_DIR/$BC.svf.function.pointer.allocations.wglobal.cfg

python3 $REPO_ROOT/python-utils/graphCleaner.py --fpanalysis --funcname main --output $CALL_DIR/$BC.svf.new.type.fp.wglobal.cfg --directgraphfile $CALL_DIR/$BC.svf.conditional.direct.calls.cfg --funcpointerfile $CALL_DIR/$BC.svf.function.pointer.allocations.wglobal.cfg -c $CALL_DIR/$BC.svf.type.cfg

mkdir outputs
mkdir stats
# Note: cause of the bin path the elf files need to be in the top layer of the path
python3 $REPO_ROOT/createSyscallStats.py -c $CALL_DIR/glibc.callgraph --apptopropertymap $REPO_ROOT/app.to.properties.json --binpath ./ --outputpath outputs/ --apptolibmap $REPO_ROOT/app.to.lib.map.json --sensitivesyscalls $REPO_ROOT/sensitive.syscalls --sensitivestatspath stats/sensitive.stats --syscallreductionpath stats/syscallreduction.stats --libdebloating --othercfgpath $REPO_ROOT/otherCfgs/ --cfgpath callgraph --singleappname $BC

python3 $REPO_ROOT/security-evaluation/getBlockedPayloads.py --blockedSyscallsTempSpl $REPO_ROOT/security-evaluation/removedViaTemporalSpecialization.txt --blockedSyscallsLibDeb $REPO_ROOT/security-evaluation/removedViaLibDebloating.txt 2>&1 | tee $BC.shellcode.payload.txt
python3 $REPO_ROOT/security-evaluation/getBlockedPayloadsROP.py --blockedSyscallsTempSpl $REPO_ROOT/security-evaluation/removedViaTemporalSpecialization.txt --blockedSyscallsLibDeb $REPO_ROOT/security-evaluation/removedViaLibDebloating.txt 2>&1 | tee $BC.rop.payload.txt

cp $BC.shellcode.payload.txt /results/
cp $BC.rop.payload.txt /results/

cp stats/sensitive.stats /results/$BC.sensitive.stats
cp outputs/syscall.count-TABLE2.out /results/$BC.syscall.count

popd