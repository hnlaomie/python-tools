#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, redis

def dump(server: str, port: str, db: str, data_file: str) -> int :
    '''
    从redis导出数据到csv文件
    :param server:
    :param port:
    :param db:
    :param data_file: csv文件，文件行格式如下
                      "user---[label1, label2, ... , labeln]"
    :return: 生成文件的行数
    '''
    left_bracket = b'['
    right_bracket = b']'
    semicolon = b';'
    # 标签分隔符
    label_separator = b', '
    column_separator = b'---'
    line_separator = b'\n'

    row_count = 0
    with open(data_file, "wb") as writer:
        r = redis.StrictRedis(host=server, port=port, db=db)
        for key in r.scan_iter():
            redis_value = r.get(key)
            value = left_bracket + redis_value.replace(semicolon, label_separator) + right_bracket
            row = key + column_separator + value + line_separator
            row_count = row_count + 1
            writer.write(row)

    return row_count

if __name__ == '__main__':
    """
    使用: python dump_data.py [redis_server] [redis_port] [redis_db] [data_file]

    将redis指定数据库的KV数据导出文件

    redis_server: redis服务器ip
    redis_port: redis服务器端口
    redis_db: redis服务器数据库，可用“INFO keyspace”命令查看
    data_file: 导出键和值存放的文件

    """
    if (len(sys.argv) > 4):
        redis_server = sys.argv[1]
        redis_port = sys.argv[2]
        redis_db = sys.argv[3]
        data_file = sys.argv[4]

        row_count = dump(redis_server, redis_port, redis_db, data_file)
        print(row_count)
    else:
        print("usage: python dump_data.py [redis_server] [redis_port] [redis_db] [data_file]")
