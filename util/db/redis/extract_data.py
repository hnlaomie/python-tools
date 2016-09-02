#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time
from datetime import datetime
from datetime import timedelta

def init_from_date(date: str) -> int :
    '''
    起始时间用 unix time 表示，给出日期则用该日期，否则用昨天的时间
    :param date: 指定日期，格式"%Y%m%d"
    :return:
    '''
    date_format = "%Y%m%d"
    # 默认为昨天的日期
    temp_date = date
    if (date == None):
        temp_date = (datetime.today() - timedelta(days=1)).strftime(date_format)
    log_date = datetime.strptime(temp_date, date_format)
    from_date = int(log_date.strftime("%s")) * 1000
    # from_date = int(time.mktime(log_date.timetuple()) * 1000)

    return from_date

def extract(data_file: str, out_file: str, date: str) -> int :
    # 一天的微秒数
    day_microseconds = 86400000
    left_bracket = b'['
    right_bracket = b']'
    semicolon = b';'
    # 标签分隔符
    label_separator = b','
    column_separator = b'---'
    line_separator = b'\n'

    from_date = init_from_date(date)
    row_count = 0

    with open(data_file, 'rb') as input, open(out_file, 'wb') as output:
        for line in input:
            # "dmpUser_"开头的数据不处理
            if line != None and not line.startswith(b'dmpUser_'):
                line = line.replace(b' ', b'')

                column_separator_index = line.find(column_separator, 0)
                left_bracket_index = line.find(left_bracket, column_separator_index)
                right_bracket_index = line.find(right_bracket, left_bracket_index)

                if left_bracket_index > column_separator_index and right_bracket_index > left_bracket_index :
                    key = line[:column_separator_index]
                    value = line[left_bracket_index + 1:right_bracket_index]

                    labels = value.split(label_separator)
                    for label in labels :
                        if label != None and len(label) > 0 :
                            row_count = row_count + 1
                            log_time = from_date + (row_count % day_microseconds)
                            row = key + label_separator + label + label_separator
                            row = row + str.encode(str(log_time), "UTF-8") + line_separator
                            output.write(row)

    return row_count

if __name__ == '__main__':
    """
    使用: python extract_data.py [data_file] [out_file] [date]

    抽取文件数据，转化为指定格式的数据，原先一个用户和多个标签在一行，
    处理后一行只一个用户，一个标签，且加上长整形的时间

    data_file: 数据文件，行格式如下
               "user---[label1, label2, ... , labeln]"
    out_file: 输出文件，行格式如下
              "user,label,log_time"
    date: "%Y%m%d"

    """
    argv_length = len(sys.argv)
    if (argv_length > 2):
        data_file = sys.argv[1]
        out_file = sys.argv[2]
        date = None
        if (argv_length == 4):
            date = sys.argv[3]

        row_count = extract(data_file, out_file, date)
        print(row_count)
    else:
        print("usage: python extract_data.py [data_file] [out_file] [date]")