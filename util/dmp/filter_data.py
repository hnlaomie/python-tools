# -*- coding: utf-8 -*-

import os, sys, re

def filter(src_file: str, dest_file: str):
    '''
    清洗用户数据
    1. 删除双引号
    2. 正则验证idfa, imei
    :param src_file: 原始用户文件
    :param dest_file: 处理后用户文件
    :return:
    '''

    # idfa and imei regular expression
    idfa = rb"^([A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12})"
    imei = rb"^(\d{15})"

    line_split = b'\n'

    with open(src_file, "rb") as reader, open(dest_file, "wb") as writer:
        row_count = 0
        for line in reader:
            # 替换双引号和"|"
            temp = line.replace(b'"', b'').replace(b'|', b'')
            # 去掉结尾的换行符
            length = len(temp) - 1
            user_id = temp[0 : length]

            # 只要和imei, idfa长度一致的字符串
            if (length == 15):
                is_match = re.match(imei, user_id)
            elif (length == 36):
                is_match = re.match(idfa, user_id)
            else:
                is_match = None

            if (is_match is not None):
                writer.write(user_id + line_split)


"""
使用: python filter_data.py src_file dest_file

清洗src_file里的数据并输出dest_file。

src_file: 原始数据文件
user_id

dest_file: 处理后数据文件
user_id
"""
if __name__ == '__main__':
    if (len(sys.argv) > 1):
        src_file = sys.argv[1]
        dest_file = sys.argv[2]
        filter(src_file, dest_file)
    else:
        print("usage: python filter_data.py src_file dest_file")