# -*- coding: utf-8 -*-

import os, sys, csv

def build_tag_data(data: []) -> []:
    '''
    扩充标签的范围，对于没有的范围，用户数给０，并给出总用户数列
    :param data: 标签用户数列表
    :return: 扩充的标签用户数列表
    '''
    new_data = []
    tag_map = {}

    # 计算最大最小范围和用户数
    length = len(data)
    tag_id = data[0][0]
    min_range = int(data[0][1])
    max_range = int(data[length - 1][1])
    all_count = 0
    for row in data:
        all_count = all_count + int(row[2])
        tag_map[int(row[1])] = row[2]

    for i in range(min_range, max_range + 1):
        user_count = 0
        if i in tag_map.keys():
            user_count = tag_map.get(i)
        # 每段范围为0.05
        row = [tag_id, round(i * 0.05, 2), user_count, all_count]
        new_data.append(row)

    return new_data

def tag_sum(src_file: str, dest_file: str):
    '''
    标签用户统计的处理
    :param src_file: 原始标签统计文件
    :param dest_file: 处理后标签统计文件
    :return:
    '''
    with open(src_file, "r") as csv_input, open(dest_file, "w") as csv_output:
        reader = csv.reader(csv_input, delimiter='\t', lineterminator='\n')
        writer = csv.writer(csv_output, delimiter=',', lineterminator='\n')

        row_list = []
        pre_tag = None

        for row in reader:
            current_tag = row[0]

            # 标签未变，只需将相同标签数据放入列表
            if current_tag == pre_tag:
                row_list.append(row)
            # 标签变了，需先处理原先标签的数据，然后清空列表
            else:
                if len(row_list) > 0:
                    rows = build_tag_data(row_list)
                    writer.writerows(rows)
                    row_list.clear()
                row_list.append(row)

            pre_tag = current_tag

        if len(row_list) > 0:
            rows = build_tag_data(row_list)
            writer.writerows(rows)


"""
使用: python tag_agg.py src_file dest_file

将src_file里每个标签，没有出现范围的用户数记０，并添加一列标签的总用户数。

src_file: 原始标签统计文件
tag_id, weight_range, user_count

dest_file: 处理后标签统计文件
tag_id, weight_range, user_count, tag_all_user
"""
if __name__ == '__main__':
    if (len(sys.argv) > 2):
        src_file = sys.argv[1]
        dest_file = sys.argv[2]
        tag_sum(src_file, dest_file)
    else:
        print("usage: python tag_agg.py src_file dest_file")