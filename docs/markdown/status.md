# Current State
Not all tools within this project are functional or produce sane results, see the sections below for further details.

## Chestnut
All tools within the container (Binalyzer, Sourcealyzer and Dynalyzer) compile successfully and are in a running state. However, when it comes to the analysis results it seems like some of the tools might be internally broken.

**Binalyzer**
The set of system calls dropped in the json file always contains all system calls available on the system. This behavior was observed for the analysis for all tools in the test suit. The results can be found [here](../runtime_tests/binalyzer/). 

**Sourcealyzer**
The compilation of all binaries terminate successfully. However there are no signs of modification on the binary. This indicates that the process of extracting and enforcing the systemcalls/the filter was not successful even though it does not fail in compiling. 

**Dynalyzer**
Due to the dynamic nature of the tool it does not make sense to include it in the automated analysis. It could be used in an interactive session using the `-it` command with Docker. Furthermore it was observed that the tool will fail to function correctly if the seccomp filter used by the program of analysis is empty (doesn't exist). Further information on this can be found in the paper. 

## Sysfilter  
Works completely! For instructions on how to run it have a look [here](../../projects/sysfilter/README.md) the runtime results can also be found [here](../runtime_tests/sysfilter/). A comparison with the required syscalls determined in the Fuzzypol paper can be found [here](../sysfilter/comparison.md).

## Fuzzypol  
I encountered instability with compilation of the `aurparse` dependence. On occasion the `auparse_metrics` is not found in the shared object.

Furthermore the symbolic execution fails to find any valid argument vectors. A log from the latest output can be found [here](../fuzzypol/klee.log).

For comparison I choose to use system call set manually determined in the paper, they are stored in the `.text` files [here](../runtime_tests/fuzzypol/).

## Temporal  
Because of the need for Bitcode to run the analysis, it has to be created first. While creation I reached a point of failure at the linker ecountering problems with various archives (e.g.`libver.a` and `libgnu.a`) for every program in the tool suit and was unable to resolve it. 