# -*- coding: utf-8 -*-

import sys, csv

def calculate(app_map):
    """
    将媒体每小时展示数进行归一，拟合计算
        归一：小时展示数 / min(小时展示数)
        拟合：sum(abs(归一值 - 标准值)) / 24
    :param app_map: 媒体展示值
    :return: 媒体拟合值
    """
    app_rate_map = {}

    base_data = [61, 32, 12, 4, 1, 5, 14, 40, 60, 70, 88, 89, 92, 85, 71, 63, 65, 91, 99, 100, 92, 91, 77, 57]

    for key in app_map.keys():
        pv_data = app_map.get(key)
        min_pv = min(pv_data)

        sum_rate = 0;
        for i in range(0, 24):
            sum_rate = sum_rate + abs(pv_data[i] / min_pv - base_data[i]) / base_data[i]

        rate = sum_rate / 24

        app_rate_map[key] = rate

    return app_rate_map

def get_hour(hour):
    int_hour = 0
    if (str(hour).startswith("0", 0)):
        int_hour = int(hour[1:])
    else:
        int_hour = int(hour)

    return int_hour

def init_hour_data(pv_hour_file):
    """
    解析媒体每小时展示数，生成以媒体ＩＤ为键，值为２４小时展示数列表的字典结构
    """
    app_map = {}

    with open(pv_hour_file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter='\t')

        for row in reader:
            app_id = row[0]
            hour = row[1]
            pv = row[2]

            # 初始化２４小时的展示数
            if (app_map.get(app_id) == None):
                pv_data = []
                for i in range(0, 24):
                    pv_data.append(1)
                app_map[app_id] = pv_data

            int_hour = get_hour(hour)
            app_map.get(app_id)[int_hour] = int(pv)

    return app_map

def append_to_last(table_file, pv_hour_file):
    """
    将媒体展示数拟合值和２４小时展示数列表放到媒体统计列表后两列
    """
    # 保存拼成的数据
    data = []

    # 读入行数据并在最后一列添加数据
    with open(table_file, "r") as csv_input:
        app_map = init_hour_data(pv_hour_file)
        app_rate_map = calculate(app_map)

        reader = csv.reader(csv_input, delimiter='\t')

        for row in reader:
            app_id = row[1]
            rate = app_rate_map.get(app_id)
            pv_data = app_map.get(app_id)

            row.append(rate)
            row.append(pv_data)
            data.append(row)

    # 写入新数据
    with open("/home/laomie/temp/test.csv", "w") as csv_output:
        writer = csv.writer(csv_output, delimiter='\t', lineterminator='\n')
        writer.writerows(data)

"""
使用: python pv_hour_rate.py table_file pv_hour_file

将pv_hour_file里每个媒体每小时展示数进行归一，拟合，最终拟合值并入table_file最后两列
倒数第２列为每小时展示数列表，最后一列为拟合值。

table_file: 媒体统计文件
date_id, app_id, ... ,

pv_hour_file: 媒体美小时展示数文件
app_id, hour, pv
"""
if __name__ == '__main__':
    if (len(sys.argv) > 2):
        table_file = sys.argv[1]
        pv_hour_file = sys.argv[2]
        append_to_last(table_file, pv_hour_file)
    else:
        print("usage: python pv_hour_rate.py table_file pv_hour_file")