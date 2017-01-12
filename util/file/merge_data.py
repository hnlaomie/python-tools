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

def merge(redis_data_file: str, hive_data_file: str, out_file: str) -> int :
    '''
    合并redis和hive的数据
    :param redis_data_file:
                      "user---tag1,tag2,...,tagn"
    :param hive_data_file:
                      "user---tag"
    :param out_file: redis pipe 可用的文件 
                      "set user tag1,tag2,...,tagn"
    :return: 生成文件的行数
    '''
    encoding = 'UTF-8'

    map_data = load_redis_data(redis_data_file)

    row_count = 0
    with open(hive_data_file, "rb") as reader, open(out_file, "wb") as writer:
        for line in reader:
            cols = line.split(column_separator)
            if len(cols) > 1:
                user = cols[0]
                tag = cols[1].strip(line_separator)
                value = map_data.get(user)
                if value != None:
                    tags = value.split(tag_separator)
                    if tag not in tags:
                        value = value + tag_separator + tag
                else:
                    value = tag
                row = b'set ' + user + b' ' + value + line_separator
                row_count = row_count + 1
                if row_count % 500000 == 0 :
                    print('写入' + str(row_count) + '行')
                writer.write(row)

    return row_count

if __name__ == '__main__':
    """
    使用: python merge_data.py [redis_data_file] [hive_data_file] [out_file]

    将redis和hive的数据合并为新的文件

    redis_data_file: redis数据文件
    hive_data_file: hive数据文件 
    out_file: 新的数据文件

    """
    if (len(sys.argv) > 3):
        redis_data_file = sys.argv[1]
        hive_data_file = sys.argv[2]
        out_file = sys.argv[3]

        row_count = merge(redis_data_file, hive_data_file, out_file)
        print(row_count)
    else:
        print("usage: python merge_data.py [redis_data_file] [hive_data_file] [out_file]")
