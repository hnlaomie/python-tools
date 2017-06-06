# -*- coding: utf-8 -*-

import os, sys, csv

def get_delete_users(user_tag_list: []) -> {}:
    '''
    获取满足删除条件的作弊用户
    :param user_tag_list: 用户标签列表
    :return: 满足删除条件的作弊用户哈希表
    '''
    # 安沃平台用户
    adwo_user_map = {}
    # 其它平台用户
    other_user_map = {}

    for row in user_tag_list:
        user = row[0]
        tag = int(row[1])
        # 来源标签的处理
        if tag == 372 :
            adwo_user_map[user] = None
        if ((tag >= 373) and (tag <= 378)):
            other_user_map[user] = None

    # 只要单独出现在安沃平台的用户
    adwo_key_set = set(adwo_user_map.keys()) - set(other_user_map.keys())
    result_map = {k: adwo_user_map[k] for k in adwo_key_set}

    return adwo_user_map

def delete(user_tag_file: str):
    '''
    删除用户标签文件里的用户标签
    :param user_tag_file: 原始用户标签文件
    :return:
    '''
    # 用户标签数据载入列表
    user_tag_list = []
    with open(user_tag_file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter=',', lineterminator='\n')
        for row in reader:
            user_tag_list.append(row)

    adwo_user_map = get_delete_users(user_tag_list)


"""
使用: python delete_data.py user_tag_file

将user_tag_file里找出要删除的用户标签，并将数据从dmp库里删除。

user_tag_file: 原始用户标签文件
user_id, tag_id

"""
if __name__ == '__main__':
    if (len(sys.argv) > 1):
        user_tag_file = sys.argv[1]
        delete(user_tag_file)
    else:
        print("usage: python delete_data.py user_tag_file")