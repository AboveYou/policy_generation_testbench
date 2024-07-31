#!/bin/bash

echo -e "[+] (1 of 7 Executing KLEE on $1 with -sym-arg $3)"

timeout $4 time klee --simplify-sym-indices --write-cov --output-module --max-memory=16000 --disable-inlining --optimize --use-forked-solver --use-cex-cache --libc=uclibc --posix-runtime --libcxx --readable-posix-inputs --external-calls=all --only-output-states-covering-new --env-file=test.env --run-in-dir=/tmp/sandbox --max-sym-array-size=16384 --max-time=40min --watchdog --max-memory-inhibit=false --max-static-fork-pct=5 --max-static-solve-pct=5 --max-static-cpfork-pct=5 --switch-type=llvm --search=random-path --search=nurs:rp --use-batching-search --batch-time=45s --silent-klee-assume --write-test-info --zero-seed-extension --named-seed-matching --allow-seed-extension --pgso --solver-optimize-divides --speculate-one-expensive-inst --store-to-load-forwarding-conflict-detection --optimize-array=all --switch-to-lookup --trap-unreachable --max-solver-time=45s --unroll-runtime --use-cfl-aa=both --x86-speculative-load-hardening --use-iterative-deepening-time-search --use-newer-candidate --mul-constant-optimization --ffast-math --mergefunc-use-aliases --loop-vectorize-with-block-frequency --expensive-combines --enable-unswitch-cost-multiplier --allow-unroll-and-jam --asan-recover --threads=$(nproc) $1 --sym-arg $3
#changes batch-time from 25 to 45

#time klee --simplify-sym-indices --write-cov --output-module --max-memory=16000 --disable-inlining --optimize --use-forked-solver --use-cex-cache --libc=uclibc --posix-runtime --libcxx --readable-posix-inputs --external-calls=all --only-output-states-covering-new --env-file=test.env --run-in-dir=/tmp/sandbox --max-sym-array-size=4096 --max-time=30min --watchdog --max-memory-inhibit=false --max-static-fork-pct=1 --max-static-solve-pct=1 --max-static-cpfork-pct=1 --switch-type=internal --search=random-path --search=nurs:rp --use-batching-search --batch-time=15s --silent-klee-assume --write-test-info --zero-seed-extension --named-seed-matching --allow-seed-extension --pgso --use-fast-cex-solver --solver-optimize-divides --speculate-one-expensive-inst --store-to-load-forwarding-conflict-detection --optimize-array=all --switch-to-lookup --trap-unreachable --max-solver-time=45s --unroll-runtime --use-cfl-aa=both --x86-speculative-load-hardening --use-iterative-deepening-time-search --use-newer-candidate --mul-constant-optimization --ffast-math --mergefunc-use-aliases --loop-vectorize-with-block-frequency --expensive-combines --enable-unswitch-cost-multiplier --allow-unroll-and-jam --asan-recover --threads=$(nproc) $1 --sym-arg $3
# von 10000 auf 16000 MB memory
echo -e "[+] (Experimental KLEE with 60 min 16GB RAM max-fork-pct=8 max-solve-pct -max-static-cpt-fork-pct=8)"

#klee --simplify-sym-indices --write-cov --output-module --max-memory=16000 --disable-inlining --optimize --use-forked-solver --use-cex-cache --libc=uclibc --posix-runtime --libcxx --readable-posix-inputs --external-calls=all --only-output-states-covering-new --env-file=test.env --run-in-dir=/tmp/sandbox --max-sym-array-size=4096 --max-time=10min --watchdog --max-memory-inhibit=false --max-static-fork-pct=8 --max-static-solve-pct=8 --max-static-cpfork-pct=8 --switch-type=internal --search=random-path --search=nurs:rp --use-batching-search --batch-time=15s --silent-klee-assume --write-test-info --zero-seed-extension --named-seed-matching --allow-seed-extension --pgso --use-fast-cex-solver --solver-optimize-divides --speculate-one-expensive-inst --store-to-load-forwarding-conflict-detection --optimize-array=all --switch-to-lookup --trap-unreachable --max-solver-time=45s --unroll-runtime --use-cfl-aa=both --x86-speculative-load-hardening --use-iterative-deepening-time-search --use-newer-candidate --mul-constant-optimization --ffast-math --mergefunc-use-aliases --loop-vectorize-with-block-frequency --expensive-combines --enable-unswitch-cost-multiplier --allow-unroll-and-jam --asan-recover --threads=$(nproc) $1 --sym-arg $3


# --use-incomplete-merge, changed Runtime from 30 to 60 

#sleep 5s

# Test Variant with Klree Replay
export KLEE_REPLAY_TIMEOUT=5

echo -e "[+] (2 count ktest files in klee-last directory )"
VAR_NR_of_Kktest_f=$(ls -1q klee-last/*.ktest | wc -l)
echo -e "[+] ($VAR_NR_of_Kktest_f)"
VAR_KLEE_LAST_Path=klee-last/*.ktest
COUNTER_LOOP=0

for f in $VAR_KLEE_LAST_Path
do
	COUNTER=$[$COUNTER +1]
	(klee-replay ./$2 $f) 2>&1 | tee -a $2replay.txt
	echo -e "$COUNTER LOOP ITERATION "
	sleep 1s
	if [ $COUNTER = $VAR_NR_of_Kktest_f ]; then
		break
	fi
done

echo -e "[+] (2 of 7 Executing Klee-replay on $2 )"
sleep 1s

echo -e "[+] (3 of 7 Overwrite Args.txt with grep - Arguments out of replay.txt and write to Args.txt)"
grep "\"-" $2replay.txt > Args.txt
sleep 1s
echo -e "[+] (4 of 7 grep '- Arguments out of replay.txt and write to Args.txt)"
grep "'-" $2replay.txt >> Args.txt
sleep 1s
echo -e "[+] (5 of 7 grep '-- Arguments out of replay.txt and write to Args.txt)"
grep "'--" $2replay.txt >> Args.txt
sleep 1s
echo -e "[+] (6 of 7 grep hopefuly only KLEE Arguments out of replay.txt and write to KLEEArgs.txt)"
#grep "KLEE-REPLAY: NOTE: Arguments: \"./$2\"" $2replay.txt >> KLEEArgs.txt
grep -oP '(?<=KLEE-REPLAY: NOTE: Arguments: ).*' $2replay.txt > KLEEArgs1.txt
# Whitespace with special Charakter would otherwise disrupt AFL
#(cat KLEEArgs1.txt | tr -d ' @')  | tee KLEEArgs1.txt
sleep 1s
echo -e "[+] (7 of 7 End of Script)"
echo -e "[+] Have a nice day! "0
