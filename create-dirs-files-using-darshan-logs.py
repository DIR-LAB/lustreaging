#!/usr/local/bin/python3

import os
import random
import math

lustre_mount_point = "/lustre"
file_size_map_file = "/Users/ddai/Documents/test-data-sets/processed-v1.txt"

target_inodes = 1000

MAX_DIR_DEPTH = 10
MAX_FILES_IN_DIR = 100
MAX_DIRS_IN_DIR = 100
STRIPE_SIZE = 1048576
SMALL_FILE_SIZE = 1024

list_of_files = []
list_of_files_sizes = []
with open(file_size_map_file, 'r') as f:
    for line in f.readlines():        
        file_name = line.split('\t')[0]
        file_size = int(line.split('\t')[1])
        list_of_files.append(file_name)
        list_of_files_sizes.append(file_size)

print ("load log file OK")

total_files_and_dirs = 0
total_files_size = 0

curr_idx = 0
max_file = len(list_of_files)

while True:
    # Put files in a directory randomly generated
    dir_depth = random.randint(1, MAX_DIR_DEPTH)
    file_nums = random.randint(1, MAX_FILES_IN_DIR)
    file_idx = curr_idx + file_nums

    path = lustre_mount_point
    for i in range(dir_depth):
        path = os.path.join(path, str(random.randint(1, MAX_DIRS_IN_DIR)))
    if not os.path.exists(path):
        print (path)
        #os.makedirs(path)
        total_files_and_dirs += dir_depth
    
    index = curr_idx
    while index < file_idx and index < max_file and total_files_and_dirs < target_inodes:
        file_path = os.path.join(path, list_of_files[index])
        file_size = list_of_files_sizes[index]
        command = ""

        if file_size < SMALL_FILE_SIZE:
            if file_size == 0:
                file_size = 128
            command = "dd if=/dev/zero of=" + file_path + " bs=" + str(file_size) +" count=" + str(1) + " status=none"
        elif file_size < STRIPE_SIZE :
            count = int(math.ceil(file_size / SMALL_FILE_SIZE))
            command = "dd if=/dev/zero of=" + file_path + " bs=" + str(SMALL_FILE_SIZE) +" count=" + str(count) + " status=none"
        else:
            count = int(math.ceil(file_size / STRIPE_SIZE))
            command = "dd if=/dev/zero of=" + file_path + " bs=" + str(STRIPE_SIZE) +" count=" + str(count) + " status=none"
        print (command)
        #os.system(command)
        total_files_and_dirs += 1
        total_files_size += file_size
        index += 1

    curr_idx = index
    if index >= max_file or total_files_and_dirs >= target_inodes:
        break

print ("total_files_and_dirs: " + str(total_files_and_dirs) + ", total_files_size: " + str(total_files_size))

