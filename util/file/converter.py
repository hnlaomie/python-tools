#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys, csv

if __name__ == '__main__':
    argv_length = len(sys.argv)
    if (argv_length > 2):
        in_file = sys.argv[1]
        out_file = sys.argv[2]

        with open(in_file, 'rb') as input, open(out_file, 'w') as output:
            writer = csv.writer(output, delimiter=';', lineterminator='\n')
            for line in input:
                if line is not None and len(line) > 0 :
                    index = line.find(b';')
                    key = line[:index]
                    str_key = key.decode('gb18030')
                    value = line[index + 1 :]
                    str_value = value.decode('gb18030')
                    data_list = str_value.strip().split('|')

                    if data_list is not None and len(data_list) > 0 :
                        row_list = []
                        for data in data_list :
                            row_list.append([str_key.encode('utf-8'), data.encode('utf-8')])
                        writer.writerows(row_list)
    else:
        print("usage: converter.py [in_file] [out_file]")
