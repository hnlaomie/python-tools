# -*- coding: utf-8 -*-

import sys

# 标签分隔符
tag_separator = b','
column_separator = b'---'
line_separator = b'\n'

def load_redis_data(redis_data_file: str) -> {} :
    data = {}
    with open(redis_data_file, "rb") as reader:
        for line in reader:
            cols = line.split(column_separator)
            if len(cols) > 1 :
                data[cols[0]] = cols[1].strip(line_separator)

    return data

def diff(src_file1: str, src_file2: str, diff_file: str) -> int :
    '''
    比较１和２的数据，将２中不在１出现的行输出到差分文件
    :param src_file1:
    :param src_file2:
    :param diff_file: redis pipe 可用的文件
    :return: 差分文件的行数
    '''

    data = {}
    with open(src_file1, "rb") as reader:
        for line in reader:
            data[line] = None

    row_count = 0
    with open(src_file2, "rb") as reader, open(diff_file, "wb") as writer:
        for line in reader:
            if line not in data :
                row_count = row_count + 1
                writer.write(line)

    return row_count

if __name__ == '__main__':
    """
    使用: python diff.py [src_file1] [src_file2] [diff_file]

    将redis和hive的数据合并为新的文件

    src_file1: 数据文件1
    src_file2: 数据文件2
    diff_file: 数据文件２不在１中的行

    """
    if (len(sys.argv) > 3):
        src_file1 = sys.argv[1]
        src_file2 = sys.argv[2]
        diff_file = sys.argv[3]

        row_count = diff(src_file1, src_file2, diff_file)
        print(row_count)
    else:
        print("usage: python merge_data.py [redis_data_file] [hive_data_file] [out_file]")
