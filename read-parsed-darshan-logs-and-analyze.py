#!/usr/local/bin/python3

file_size_map_file = "/Users/ddai/Documents/test-data-sets/processed.txt"
file_size_map_file2 = "/Users/ddai/Documents/test-data-sets/processed-v1.txt"

with open(file_size_map_file, 'r') as f:
    print ("start processing")
    s = f.read()
    print ("finish reading the file")
    s = s[1:-2]
    array_s = s.split(',')
    print ("split string finish")

    with open(file_size_map_file2, 'w') as f_out:
        for kvs in array_s:
            f_out.write(kvs.split(':')[0].strip() + "\t" + kvs.split(':')[1].strip() + "\n")
        
