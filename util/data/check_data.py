# -*- coding: utf-8 -*-

import os, sys, csv
from datetime import datetime
from datetime import timedelta
import time

KEY_FORMAT = "%Y-%m-%d-%H"
now = datetime.strptime(str(time.strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")

default_tables = ["android_fsshow_log", "show_log", "ios_fsshow_log", "ios_show_log",
                  "android_fsclick_log", "click_log", "ios_fsclick_log", "ios_click_log"]
yg_tables = ["show_log_detail", "click_log_detail"]

def get_int_hour(hour_list: []) -> []:
    data_list = []
    for hour in hour_list:
        data_list.append(str(int(hour)))
    return data_list

def get_day(data: str) -> str:
    '''
    获取字符串中的日期
    :param data:
    :return: 日期("yyyy-MM-dd")
    '''
    values = data.strip().split("=")
    day = values[-1]
    if (len(day) == 8):
        day = day[:4] + "-" + day[4:6] + "-" + day[6:]
    return day

def get_hour(data: str) -> str:
    '''
    获取字符串中的时
    :param data:
    :return: 时("HH")
    '''
    values = data.strip().split("=")
    hour = values[-1]
    hour = hour.zfill(2)
    return hour

def load_table_data(file: str) -> {}:
    '''
    通过载入表的日期分区，判断数据是否已有
    :param file:
    :return: key: yyyy-MM-dd-HH  value: 表列表，包含指定分区已有的表
    '''
    data_map = {}
    with open(file, "r") as reader:
        for line in reader:
            if line.startswith("drwxr"):
                data_list = line.split("/")
                if (data_list != None and len(data_list) > 3):
                    hour = get_hour(data_list[-1])
                    day = get_day(data_list[-2])
                    key = day + "-" + hour
                    table = data_list[-3].strip()

                    table_list = data_map.get(key)
                    if (table_list == None):
                        table_list = []
                    table_list.append(table)
                    data_map[key] = table_list

    return data_map

def load_error_date(file: str) -> []:
    '''
    通过缺数表的日志，判断数据是否已有
    :param file: 缺数表日志
    :return: 缺数时间列表，格式"yyyy-MM-dd-HH"
    '''
    date_list = []
    with open(file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter=',')
        for line in reader:
            error_table = line[0]
            # 出错的表在监控的表中，则数据不全，该小时数据有错，不载入该小时的数据
            if error_table in default_tables:
                date_list.append(line[1])

    return list(set(date_list))

def write_error_data(date_list: [], yg_map: {}, error_file: str):
    '''
    输出未及时载入数据的表
    :param date_list:
    :param default_map:
    :param error_file:
    :return:
    '''
    error_map = {}
    # 最新载入日志数据时间（当前时间前1小时）
    log_date = now + timedelta(hours=-1)
    for i in range(0, 24):
        minus_hour = i * -1
        check_date = log_date + timedelta(hours=minus_hour)
        str_date = check_date.strftime(KEY_FORMAT)

        table_list = yg_map.get(str_date)
        # 该小时无载入数据的表，则输出错误
        if (table_list == None):
            if str_date in date_list :
                error_map[str_date] = yg_tables

    if (len(error_map) > 0):
        with open(error_file, "w") as csv_output:
            for k, v in error_map.items():
                writer = csv.writer(csv_output, delimiter=',', lineterminator='\n')
                writer.writerow([k, str(v)])

def get_load_date(date_list: [], yg_map: {}, load_file: str):
    '''
    取得硬广需要载入数据的时间段，最近24小时，未缺数的时段都得载入
    :param date_list:
    :param yg_map:
    :param load_file:
    :return:
    '''
    load_map = {}

    # 最新载入日志数据时间（当前时间前1小时）
    log_date = now + timedelta(hours=-1)
    for i in range(0, 24):
        minus_hour = i * -1
        check_date = log_date + timedelta(hours=minus_hour)
        str_date = check_date.strftime(KEY_FORMAT)

        table_list = yg_map.get(str_date)
        # 该时段未载入且不缺数载入数据
        if (table_list == None):
            #tables = [item for item in default_tables if item not in set(table_list)]
            # 该时段所有表已载入数据
            if str_date not in set(date_list) :
                key = str_date[:10]
                hour_list = load_map.get(key)
                if (hour_list == None):
                    hour_list = []
                hour_list.append(str_date[11:])
                load_map[key] = hour_list

    if (len(load_map) > 0):
        with open(load_file, "w") as writer:
            for k, v in load_map.items():
                hour_data = str.join(",", v)
                int_date = k[:4] + k[5:7] + k[8:]
                int_hour_data = str.join(",", get_int_hour(v))
                writer.write(k + ":" + hour_data + ":" + int_date + ":" + int_hour_data + "\n")

def check_and_load(error_table_file: str, yg_log_file: str, error_file: str, load_file: str):
    error_date_list = load_error_date(error_table_file)
    yg_map = load_table_data(yg_log_file)
    write_error_data(error_date_list, yg_map, error_file)
    get_load_date(error_date_list, yg_map, load_file)

if __name__ == '__main__':
    '''
    error_table_file: 缺数表报警日志
    yg_log_file:      导入数据
    error_file:       错误信息，未按时入库的原始日志
    load_file:        需导入的时间段
    '''
    if (len(sys.argv) > 4):
        error_table_file = sys.argv[1]
        yg_log_file = sys.argv[2]
        error_file = sys.argv[3]
        load_file = sys.argv[4]
        check_and_load(error_table_file, yg_log_file, error_file, load_file)
    else:
        print("usage: python3 check_data.py [error_table_file] [yg_log_file] [error_file] [load_file]")