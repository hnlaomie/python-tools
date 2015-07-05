# -*- coding: utf-8 -*-

import os, sys, csv

def append_to_last(file, column_index):
    # 保存拼成的数据
    data = []

    # 读入行数据并在最后一列添加数据
    with open(file, "r") as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if len(row) > int(column_index) :
                row.append(row[int(column_index)])
                data.append(row)

    # 写入新数据
    with open(file, "w") as csv_output:
        writer = csv.writer(csv_output, lineterminator='\n')
        writer.writerows(data)

"""
使用: python [datafile] [outfile]

用"datafile"的数据生成测试用的csv文件"outfile"
"datafile"第１行为列索引，第２行开始为每行相关列的值，对于未给出的列为空值
"""
if __name__ == '__main__':
    if (len(sys.argv) > 2):
        path = sys.argv[1]
        column_index = sys.argv[2]
        walltree(path, column_index, append_to_last)
    else:
        print("usage: python appendcolumn.py [path] column_index")