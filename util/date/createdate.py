# -*- coding: utf-8 -*-

import os, sys, csv
from datetime import datetime
from datetime import timedelta

def createDate(startDate, addDays):
    file = "/home/laomie/dm.yg_datetime.csv"
    fromDate = datetime.strptime(startDate, "%Y-%m-%d")

    # 写入新数据
    with open(file, "w") as csv_output:
        writer = csv.writer(csv_output, quotechar=',', lineterminator='\n')
        for i in range(0, int(addDays)):
            toDate = fromDate + timedelta(days=i)
            for hour in range(0, 24):
                hourDate = toDate + timedelta(hours=hour)
                data = []
                #data.append(hourDate.strftime('%Y-%m-%d %H:%M:%S'))
                data.append(hourDate.strftime('%Y%m%d%H%M%S'))
                data.append(hourDate.strftime('%Y%m%d'))
                data.append(hourDate.year)
                data.append(hourDate.month)
                data.append(hourDate.day)
                data.append(hourDate.hour)

                #data.append(hourDate.strftime('%Y-%m-%d %H:%M:%S'))
                #data.append(hourDate.hour)
                writer.writerow(data)

"""
使用: python createdate.py [startDate] [addDays]

根据输入的开始时间和天数，生成日期相关的csv文件
"""
if __name__ == '__main__':
    if (len(sys.argv) > 2):
        startDate = sys.argv[1]
        addDays = sys.argv[2]
        createDate(startDate, addDays)
    else:
        print("usage: python createdate.py [startDate] [addDays]")