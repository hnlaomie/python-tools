# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from datetime import timedelta

def load_down_row(log_file: str) -> []:
    '''
    将日志中down的行载入列表
    :param log_file: 日志文件
    :return: down列表
    '''
    down_list = []

    with open(log_file, "r") as input:
        for row in input:
            # down行为包含"spark is down"的行
            if row != None and row.find("spark is down") > 0 :
                down_list.append(row)

    return down_list

def last_hour_is_down(down_list: []) -> bool:
    '''
    判断上小时进程是否down
    :param down_list: 进程down日志信息列表
    :return: True进程down, False没down
    '''
    is_down = False
    # 最新载入日志数据时间（当前时间前1小时）
    check_date = datetime.today() - timedelta(hours = 1)
    check_str = check_date.strftime('%Y-%m-%d_%H')

    for line in down_list:
        if str(line).startswith(check_str):
            is_down = True

    return is_down

if __name__ == '__main__':
    '''
    通过日志文件，判断上小时进程是否down，如果down，返回"True"
    '''
    if (len(sys.argv) > 1):
        log_file = sys.argv[1]
        down_list = load_down_row(log_file)
        is_down = last_hour_is_down(down_list)
        print(is_down)
    else:
        print("usage: python3 check_down_hour.py [log_file]")
