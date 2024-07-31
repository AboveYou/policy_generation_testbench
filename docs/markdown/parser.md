# Parser
Each project uses a different file format to store the extracted system calls, for better analysis they need to be unified into a consistent format.

A universal parser was written for this purpose, it can detect the extension of a given file and parses it into the easy to read [TOML](https://toml.io/en/) syntax.

The resulting file is structured as `number_of_syscall = syscall_name`.
For example:

```toml
1 = "write"
2 = "open"
3 = "close"
5 = "fstat"
...
```

Supported file types are
- `.json` (Chestnut & Sysfilter)
- `.csv` (Fuzzypol)
- `.stats` (Temporal)
- `.text` (to parse system call lists from papers)

Note that the different file formats have to be interpreted accordingly. For example Fuzzypol uses a Bitvetor while Chestnut uses the system call numbers, tampering with the extension will therefore not work.

## Run
The requirements have to be installed according to `requirements.txt`!

The easiest way to run the parser is like this:
```bash
python3 parser.py ./results/test.<ending>
```

Without using any additional flag, the resulting file will be placed in the same directory as the input. This behavior could be changed using the `-o` flag.

The filename will be the same as the original file with an additional `.toml` ending. The `-t` flag could be used to insert an additional timestamp in the filename, this is especial useful when testing binaries multiple times as the output will otherwise be overwritten.

The parser works by creating a dictionary from the `unistd_64.h` header file, which is normally use to define constants to the system call numbers. This file is assumed to be present at `/usr/include/asm/unistd_64.h`, if this differs on your system the `-e` flag can be used to change the path.

Have a look at the help page of the script to see more options (`-h`).
