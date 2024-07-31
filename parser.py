import csv
import json
import toml
from datetime import datetime
import argparse

FILENAME = __file__[:-3]
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def stats_to_list(filepath):
    global FILENAME
    res_list = list()

    if "stats" not in filepath:
        filepath += ".stats"

    FILENAME = f"{filepath}"

    try:
        with open(filepath, "r") as read_file:
            reader = csv.reader(read_file, delimiter=';')

            res_list = list()
            for row in reader:
                if "piecewise-master" in row:
                    res_list.append(row)

            return res_list
    except:
        print("error: input file does not exist")
        exit(1)


def stats_to_dict(filepath, syscall_dict):
    stat_data = stats_to_list(filepath)

    # invert the dict for this use case
    inv_syscall_dict = {v: k for k, v in syscall_dict.items()}

    tmp_dict = dict()
    for item in stat_data:
        # syscall not needed
        if item[3] == '0':
            continue
        syscall_name = item[0]
        tmp_dict[int(inv_syscall_dict[syscall_name])] = syscall_name
    
    # sort syscalls by number
    tmp_dict = dict(sorted(tmp_dict.items()))
    
    res_dict = dict()
    # convert items back to str
    for k,v in tmp_dict.items():
        res_dict[str(k)] = v

    return res_dict


def json_to_list(filepath):
    global FILENAME

    if "json" not in filepath:
        filepath += ".json"

    FILENAME = f"{filepath}"

    try:
        with open(filepath, "r") as read_file:
            return json.load(read_file)
    except:
        print("error: input file does not exist")
        exit(1)


def text_to_list(filepath):
    global FILENAME

    FILENAME = f"{filepath}"

    with open(filepath, "r") as read_file:
        content = read_file.read()

    items = content.split(',')
    items = [item.strip() for item in items]

    return items


def text_to_dict(filepath, syscall_dict):
    text_data = text_to_list(filepath)

    res_dict = dict()

    rev_dict = {v: k for k, v in syscall_dict.items()}

    for item in text_data:
        syscall_number = rev_dict[item]
        res_dict[syscall_number] = item

    sorted_keys = sorted(res_dict.keys(), key=int)

    sorted_dict = {key: res_dict[key] for key in sorted_keys}

    return sorted_dict


def json_to_dict(filepath, syscall_dict):
    json_data = json_to_list(filepath)

    res_dict = dict()
    for item in json_data:
        item = str(item)
        res_dict[item] = syscall_dict[item]

    return res_dict


def csv_to_list(filepath):
    global FILENAME
    res_list = list()

    if "csv" not in filepath:
        filepath += ".csv"

    FILENAME = f"{filepath}"

    try:
        with open(filepath, "r") as read_file:
            reader = csv.reader(read_file)

            return next(reader, None)
    except:
        print("error: input file does not exist")
        exit(1)


def csv_to_dict(filepath, syscall_dict):
    csv_data = csv_to_list(filepath)

    res_dict = dict()
    for index in range(len(csv_data)):
        if csv_data[index] == '0':
            continue
        index = str(index)
        res_dict[index] = syscall_dict[index]

    return res_dict


def header_to_dict(filepath):
    syscall_dict = dict()

    try:
        with open(filepath, 'r') as f:
            header_data = f.readlines()
    except:
        print("error: header file does not exist")
        exit(1)

    for line in header_data:
        if line.startswith('#define __NR_'):
            parts = line.split()
            syscall_dict[parts[2]] = parts[1][len('__NR_'):].lower()
    
    if not syscall_dict:
        print("error: failed to parse header file")
        exit(1)
    
    return syscall_dict


def drop_dict_to_toml(filepath, timestamp, res_dict):
    global FILENAME
    global TIMESTAMP

    try:
        if filepath:
            FILENAME = filepath
        
        if timestamp:
            FILENAME += f"_{TIMESTAMP}"

        if "toml" not in FILENAME:
            FILENAME += ".toml"

        with open(FILENAME, 'w') as file:
            toml.dump(res_dict, file)
    except:
        print("error: not able to create file")
        exit(1)


def main():
    # create ArgumentParser object
    parser = argparse.ArgumentParser(description=f"parse the resulting files from the projects (csv, stats, text, json) into a toml format")

    # add arguments
    parser.add_argument('filepath', type=str, help='filepath to the input file')
    parser.add_argument('-o', '--output', type=str, help='name of output file')
    parser.add_argument('-e', '--header', type=str, default='/usr/include/asm/unistd_64.h', help='filepath of the header')
    parser.add_argument('-t', '--timestamp', action='store_true', help='add timestamp to the output')

    # parse the arguments
    args = parser.parse_args()

    # parse the syscalls file
    syscall_dict = header_to_dict(args.header)
    
    # fetch the file ending
    file_ending = args.filepath.split(".")[-1]

    res_dict = dict()
    match file_ending:
        case "json":
            res_dict = json_to_dict(args.filepath, syscall_dict)
        case "csv":
            res_dict = csv_to_dict(args.filepath, syscall_dict)
        case "stats":
            res_dict = stats_to_dict(args.filepath, syscall_dict)
        case "text":
            res_dict = text_to_dict(args.filepath, syscall_dict)
        case _:
            print("Error: no valid file-type to parse.")
            exit(1)

    drop_dict_to_toml(args.output, args.timestamp, res_dict)


if __name__ == "__main__":
    main()
    exit(0)
