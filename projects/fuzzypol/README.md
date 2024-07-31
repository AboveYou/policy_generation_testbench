# Dockerized Fuzzypol
https://gitlab.com/iot-aalen/fuzz-seccomp-filter

## Build
Move into the directory with the according Dockerfile and run the following command.

```bash
docker build -t fuzzypol ./
```

Because the build time of the container is quite large you can also use the accompanied exported image. Refer to the [docker.md](../../docs/markdown/docker.md) for further information. 

## Run
The implementation supports operation in two modes: "manual" and "testsuit". Both modes can be run from outside the container but "manual" requires more preparation.

### Test Suit
The binaries/bitcodes for the tools in the test suit are pre-build within the container. Executing the script will run the fuzzer for every binary in the suit. The default duration is set to 3 minutes.

> Note that 3 minutes is the time needed to pass without a new crash detected by the fuzzer to stop the execution. Absolute  runtime will be much longer.

```bash
docker run --volume ./results/:/results/ fuzzypol ./run_suit.sh
```

### Manual
Running the fuzzer manually requires a bit more preparation. The directory (not an archive) needed to build the tool need to be placed in `results/`. 

The first command shown will build the AFL instrumented binary and create the bitcode needed for the symbolic execution. The script is intended to work in a "configure" and "make" fashion, as seen in e.g. the GNU projects. After successful execution the files will be stored in `alf_ins/` and `klee_ins/`, these directories have been created in the process.   

The second command will run the fuzzer. The script is intended to be used with the previously created files and the paths need to be provides accordingly.

```bash
docker run --volume ./results/:/results/  fuzzypol ./build.sh <bin_build_dir> <bin_name>
docker run --volume ./results/:/results/ fuzzypol ./run.sh <path_to_bin> <path_to_afl_bin > <path_to_klee_bc> <duration>
```

Use the `-h` flag for the scripts to get more information.
