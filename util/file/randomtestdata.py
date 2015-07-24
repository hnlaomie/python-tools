# -*- coding: utf-8 -*-

import os, sys, csv, random
from datetime import datetime
from datetime import timedelta


def create_data(row_count, start_date):
    # 测试数据设置
    game_count = 1000
    user_count = 100000

    # 保存作成的数据
    row_datas = []
    base_date = datetime.strptime(start_date, "%Y-%m-%d")

    # 第一行生成列索引
    row_datas.append([8, 6, 13, 14, 3, 4])

    # 生成测试数据
    for i in range(int(row_count)):
        row_data = []
        # 登录时间
        add_second = random.randint(0, 3599)
        login_date = base_date + timedelta(seconds=add_second)
        row_data.append(login_date.strftime('%Y-%m-%d %H:%M:%S'))
        # 游戏ID
        app_id = random.randint(1, game_count)
        row_data.append(app_id)
        row_data.append(app_id)
        # 用户
        uuid = random.randint(1, user_count)
        user = 'user-' + str(uuid)
        row_data.append(user)
        row_data.append(1)
        # 设备
        row_data.append(uuid)
        row_datas.append(row_data)

    return row_datas

def output_data(data, datafile):
    with open(outfile, "w") as csv_output:
        writer = csv.writer(csv_output, lineterminator='\n')
        writer.writerows(data)

"""
使用: python randomtestdata.py [row_count] [outfile]

生成指定记录数的测试数据
"""
if __name__ == '__main__':
    if (len(sys.argv) > 3):
        row_count = sys.argv[1]
        start_date = sys.argv[2]
        outfile = sys.argv[3]
        data = create_data(row_count, start_date)
        output_data(data, outfile)
    else:
        print("usage: python randomtestdata.py [row_count] [start_date] [outfile]")