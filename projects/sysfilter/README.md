# Dockerized Sysfilter
https://gitlab.com/Egalito/sysfilter

## Build
Move into the directory with the according Dockerfile and run the following command.

```bash
docker build -t sysfilter ./
```

Because the build time of the container is quite large you can also use the accompanied exported image. Refer to the [docker.md](../../docs/markdown/docker.md) for further information. 

## Run
The implementation supports operation in two modes: "manual" and "testsuit".

### Test Suit
The binaries for the tools in the test suit are pre-build within the container. Executing the script will run Sysfilter for every binary in the suit. The results of the analysis can be found in `results/suit/` after executing the command below.

```bash
docker run --volume ./results/:/results/ sysfilter ./run_suit.sh
```

### Manual
In order for the tool to work it requires binaries to be compiled as **PIC** and with **stack unwinding information**, binaries given to the container must fulfill with requirement.

Most modern compilers fulfill the requirement without providing additional flags. Use `readelf` or `objdump` to check the requirement.
```bash
readelf -h <binary>
objdump -h <binary> | grep .eh_frame
```

The binary is expected to be present in `results/` after executing the script there will be a <bin_name>.json file in the same directory containing the results.

```bash
docker run --volume ./results/:/results/ sysfilter ./run.sh <bin_name>
```

Use the `-h` flag for the script to get more information.
