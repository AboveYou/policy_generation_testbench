# Policy Generation Testbench
This repository holds a small test suit evaluating four different proof-of-concept implementations researching the area of automated seccomp filter generation. 

The implementations can be found at:
- https://github.com/IAIK/Chestnut
- https://gitlab.com/iot-aalen/fuzz-seccomp-filter
- https://gitlab.com/Egalito/sysfilter
- https://github.com/shamedgh/temporal-specialization

A Docker environment is used to setup and prepare the test suit components. As a lot of compilation is done within the container the image creation can take a while but the runtime for the tests will be faster (differs for each project). Running automated tests with the programs defined in the testsuit or manual testing is supported. For manual testing the requirements for the tools have to be met.

Each tool in the `projects/` directory provides its own instructions on how to build and run it.  
See:
- [Fuzzypol](projects/fuzzypol/README.md)
- [Chestnut](projects/chestnut/README.md)
- [Sysfilter](projects/sysfilter/README.md)
- [Temporal](projects/temporal/README.md)

Since the project analyzed are all proof-of-concepts and have been released a few years ago I encountered various problems while setting them up. As a result some projects are not runnable or produce reliable outputs. A list of the current status can be found below, see the [status.md](docs/markdown/status.md) for more information.

Tool | Compilation | Runtime | Result
--- | --- | --- | ---
Chestnut | Yes | Yes | No 
Fuzzypol | Yes | No | No
Sysfilter | Yes | Yes | Yes
Temporal | Yes | No | No

The tools use different (custom) file formats and they are hard to compare to each other. For this reason a parser was written, see [parser.md](docs/markdown/parser.md) for further details on supported types and arguments.

The `docs/` directory provides a collection of code snippets and notes used/taken thought the tests. For example, some runtime tests could be found [here](docs/runtime_tests/) or a few code snippets used to test certain behavior encountered during the setup process [here](docs/lief/) and [here](docs/sysfilter/address_taken.c).
