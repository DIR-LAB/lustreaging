#!/usr/local/bin/python3

import os
import subprocess

darshan_log_dir = "/Users/ddai/Documents/test-data-sets/intrepid/2013"
file_size_map_file = "/Users/ddai/Documents/test-data-sets/processed.txt"
parsed_file_path = "/tmp/1.txt"

g = os.walk(darshan_log_dir)

file_size_map = {}
helper_map = {}

for path, _, files in g:
    for file in files:
        if (not file.endswith("bz2")):
            continue
        file_path = os.path.join(path, file)
        print (file_path)
        parsed_file_output = open(parsed_file_path, "w")
        command = "./darshan-parser " + file_path
        p = subprocess.Popen(command, shell=True, stdout=parsed_file_output).wait()
        parsed_file_output.close()

        input_log = open(parsed_file_path, "r")
        for line in input_log:
            if line.startswith("#"):
                continue
            str = line.split()
            if (len(str) == 0):
                continue
            
            file_name_id = int(str[1])

            # if this file has not been visisted before, initialize its size as 0
            if not file_name_id in file_size_map.keys():
                file_size_map[file_name_id] = 0
                helper_map[file_name_id] = 0
            # CP_SIZE_AT_OPEN may be smaller than the recorded size!
            
            if (str[2] == "CP_BYTES_WRITTEN"): # index: 48
                helper_map[file_name_id] = int(str[3])

            if (str[2] == "CP_SIZE_AT_OPEN"): # index: 139
                size_at_open = int(str[3])
                new_file_size = size_at_open + helper_map[file_name_id]
                file_size_map[file_name_id] = max(file_size_map[file_name_id], new_file_size)
        
        input_log.close()

with open(file_size_map_file, 'w') as f:
    print(file_size_map, file=f)            
