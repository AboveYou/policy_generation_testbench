# Dockerized Chestnut
https://github.com/IAIK/Chestnut

## Build
Move into the directory with the according Dockerfile and run the following command.

```bash
docker build -t chestnut ./
```

Because the build time of the container is quite large you can also use the accompanied exported image. Refer to the [docker.md](../../docs/markdown/docker.md) for further information. 

## Run
The implementation supports operation in two modes: "manual" and "testsuit".

### Test Suit
There are two scripts for running the Source-/Binalyzer test suits separately. After running the commands as seen below the output files can be found in `results/ba/` or `results/sa/`. 

```bash
docker run --volume ./results/:/results/ chestnut ./binalyzer_run_suit.sh
# or
docker run --volume ./results/:/results/ chestnut ./sourcealyzer_run_suit.sh
```

### Manual
There are also two run scripts, one for each tool on self provided programs.

Binalyzer only requires the binary to be placed in `results/`, the resulting JSON file can be found in the same directory after running the according command.

Sourealyzer requires the source code of the binary to be available in `results/`. The script is designed to work on tools which can be build in a "configure" and "make" fashion. The GNU tools can be taken as an example.

The automation of the Sourcealyzer execution might fail, if dependencies needed in the build process are not installed or the provided directory got a custom structure. You can use the `-it` flag to spawn a shell in the container and resolve the issues from there.

```bash
docker run --volume ./results/:/results/ chestnut ./binalyzer_run.sh <bin_name>
# or
docker run --volume ./results/:/results/ chestnut ./sourcealyzer_run_suit.sh <dir_name> <bin_name>
```

Use the `-h` flag for the script to get more information.
