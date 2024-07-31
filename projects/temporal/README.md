# Dockerized Temporal
https://github.com/shamedgh/temporal-specialization

## Build
Move into the directory with the according Dockerfile and run the following command.

```bash
docker build -t temporal ./
```

Because the build time of the container is quite large you can also use the accompanied exported image. Refer to the [docker.md](../../docs/markdown/docker.md) for further information. 

## Run
The implementation supports operation in two modes: "manual" and "testsuit".

### Test Suit
For Temporal the LLVM bitcode need to be created first to perform the analysis on. As described in [status.md](../../docs/markdown/status.md) the execution does not surpass this point, the error log for the commands in the current state can be observed when executing the command below.

```bash
docker run --volume ./results/:/results/ temporal ./run_suit.sh
```

### Manual
There are two scripts to execute here, the first one is intended to create the bicodes, the files created will be used for the next command. This one performs the final analysis to export the calls the bitcodes and the source code directory is used for this step.

```bash
docker run --volume ./results/:/results/ temporal ./create_bitecode.sh <sourcecode_dir_path>
docker run --volume ./results/:/results/ temporal ./run.sh <bitecode_path> <sourcecode_dir_path>
```

Use the `-h` flag for the script to get more information.




















## Description
This container contains a prebuilt Clang+LLVM and the modified SVF for artifact evaluation of Temporal Specialization.

Build the container like this:
```bash
docker build -t temporal ./
```

Because temporal needs the sourcecode of the application to run on you need to compile it from source. Due to different dependencies and flags in the building process there can not be a universal way of building the required bytecode. However there are template scripts which might work but will most likely need to be adjusted.

It's best to run the container in an interactive manner and execute the following commands. It is assumed that the source code to the application lies in the `results/` directory in the same file as the Dockerfile but it would also be possible to download and uncompress the code within the container. 
```bash
# run container ans mount results dir
docker run -it -name temporal --volume ./results:/results temporal

# create bytecode (the script might be adjusted e.g. different build flags, installing dependencies)
./create_bytecodes.sh <sourcecode_path>

# extract the syscalls
./extract_syscalls.sh <bytecode_path> <project_root_path>
```
