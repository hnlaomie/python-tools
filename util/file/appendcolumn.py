# -*- coding: utf-8 -*-

import os, sys, csv
from stat import S_ISDIR, S_ISREG

def walltree(path, column_index, callback):
    for f in os.listdir(path):
        fullpath = os.path.join(path, f)
        mode = os.stat(fullpath).st_mode
        if S_ISDIR(mode):
            walltree(fullpath, column_index, append_to_last)
        elif S_ISREG(mode):
            callback(fullpath, column_index)
        else:
            print(fullpath)

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
使用: python appendcolumn.py [path] columnIndex

遍历[path]下所有文件,每行增加一列和"columnIndex"列相同的值
"""
if __name__ == '__main__':
    if (len(sys.argv) > 2):
        path = sys.argv[1]
        column_index = sys.argv[2]
        walltree(path, column_index, append_to_last)
    else:
        print("usage: python appendcolumn.py [path] column_index")