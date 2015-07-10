# -*- coding: utf-8 -*-

import os, sys, csv

def create_data(column_count, datafile):
    column_map = {}
    # 保存作成的数据
    data = []

    row_index = 0

    with open(datafile, "r") as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            row_data = []

            # 根据第一行数据生成相关索引
            if row_index == 0 :
                data_size = len(row)
                for i in range(data_size):
                    column_map[row[i]] = i
            else:
                for i in range(int(column_count)):
                    # 该列是否在数据列中存在
                    index = column_map.get(str(i + 1))
                    # 存在则使用数据列给出的数据，否则给空
                    if (index != None):
                        row_data.append(row[index])
                    else:
                        row_data.append("")

                data.append(row_data)

            row_index = row_index + 1

    return data

def output_data(data, datafile):
    with open(outfile, "w") as csv_output:
        writer = csv.writer(csv_output, lineterminator='\n')
        writer.writerows(data)

"""
使用: python [column_count] [datafile] [outfile]

做出"column_count"列数据，"datafile"第１行为列索引，第２行开始为每行相关列的值，对于未给出的列为空值
"""
if __name__ == '__main__':
    if (len(sys.argv) > 3):
        column_count = sys.argv[1]
        datafile = sys.argv[2]
        outfile = sys.argv[3]
        data = create_data(column_count, datafile)
        output_data(data, outfile)
    else:
        print("usage: python createtestdata.py [column_count] [datafile] [outfile]")