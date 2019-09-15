#!/usr/bin/python

import os
import random
import math
import sys

if len(sys.argv) != 5:
    print ("Usage: ./aging.py target_inodes index total_runners last_stop_index")
    sys.exit()

target_inodes = int(sys.argv[1]) #152628
local_index = int(sys.argv[2])
total_runners = int(sys.argv[3])
last_stop_index = int(sys.argv[4])
print ("calling ./aging.py " + str(target_inodes) + " " + str(local_index) + " " + str(total_runners) + " " + str(last_stop_index))

lustre_mount_point = os.path.join("/lustre", "50"+str(local_index))
if not os.path.exists(lustre_mount_point):
    print("create lustre directory for local runner: ", lustre_mount_point)
    os.mkdir(lustre_mount_point)
    
file_size_map_file = "/proj/dirr-PG0/tools/darshan-logs-intrepid-file-size.txt"

MAX_DIR_DEPTH = 15
MAX_FILES_IN_DIR = 100
MAX_DIRS_IN_DIR = 150
STRIPE_SIZE = 262144 # 256KB
SMALL_FILE_SIZE = 1024 # 1KB

list_of_files = []
list_of_files_sizes = []
with open(file_size_map_file, 'r') as f:
    for line in f.readlines():        
        file_name = line.split('\t')[0]
        file_size = int(line.split('\t')[1])
        list_of_files.append(file_name)
        list_of_files_sizes.append(file_size)

print ("load log file... OK")

total_files_and_dirs = 0
total_files_size = 0

max_file = len(list_of_files)
curr_idx = int(float(max_file)/float(total_runners)) * local_index + last_stop_index

while True:
    # Put files in a directory randomly generated
    dir_depth = random.randint(1, MAX_DIR_DEPTH)
    file_nums = random.randint(1, MAX_FILES_IN_DIR)
    file_idx = curr_idx + file_nums

    path = lustre_mount_point
    for i in range(dir_depth):
        path = os.path.join(path, str(random.randint(1, MAX_DIRS_IN_DIR)))
    if not os.path.exists(path):
        # print (path)
        os.makedirs(path)
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
        elif file_size < 16 * STRIPE_SIZE:
            count = int(math.ceil(file_size / STRIPE_SIZE))
            command = "dd if=/dev/zero of=" + file_path + " bs=" + str(STRIPE_SIZE) +" count=" + str(count) + " status=none"
        else:
            file_size = 16 * STRIPE_SIZE
            count = int(math.ceil(file_size / STRIPE_SIZE))
            command = "dd if=/dev/zero of=" + file_path + " bs=" + str(STRIPE_SIZE) +" count=" + str(count) + " status=none"

        # print (command)
        os.system(command)
        total_files_and_dirs += 1
        if total_files_and_dirs % 100 == 0:
            print ("create files/dirs inodes reach to ", total_files_and_dirs)

        total_files_size += file_size
        index += 1

    curr_idx = index
    if index >= max_file or total_files_and_dirs >= target_inodes:
        break

off_set = curr_idx - (int(float(max_file)/float(total_runners)) * local_index)
print ("total_files_and_dirs: " + str(total_files_and_dirs) + ", total_files_size: " + str(total_files_size) + ", index: " + str(off_set))