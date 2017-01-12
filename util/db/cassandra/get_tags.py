#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, csv, time
from datetime import datetime
from cassandra.cluster import Cluster, Session, ResultSet
from cassandra.concurrent import execute_concurrent

def load_user(user_file: str) -> []:
    """
    从用户文件载入用户ID
    :param user_file: 用户文件
    :return: 用户ID列表
    """
    user_list = []

    with open(user_file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter=',')

        for row in reader:
            if row is not None and len(row) > 0:
                for user_id in row:
                    user_list.append(user_id)

    return user_list

def load_partition_data(user_list: [], session, select_statement) -> []:
    '''
    载入部分用户的标签
    :param user_list:
    :param session:
    :param select_statement:
    :return:
    '''
    data_list = []

    statements_and_params = []
    for user_id in user_list:
        params = (user_id,)
        statements_and_params.append((select_statement, params))

    results = execute_concurrent(
        session, statements_and_params, concurrency=100, raise_on_first_error=False)

    for (success, result) in results:
        if not success:
            print("查询报错")
        else:
            for row in result:
                data_list.append([row.user_id, str(row.tag_id)])

    return data_list

def load_to_file(user_file, out_file):
    """
    根据给定的用户，从cassandra数据库中读取用户标签数据到文件
    :param user_file: 用户文件
    :param out_file: 用户标签文件
    :return:
    """
    user_list = load_user(user_file)

    sql = "SELECT user_id, tag_id FROM user_tags"
    sql = sql + " WHERE user_id=?"

    cluster = Cluster(['192.168.11.52'])
    session = cluster.connect('dmp')
    select_statement = session.prepare(sql)

    with open(out_file, "w") as csv_output:
        writer = csv.writer(csv_output, delimiter=',', lineterminator='\n')

        # 拆分用户，太多用户返回的标签可能太大，列表放不下
        user_temp_list = []
        for user in user_list:
            user_temp_list.append(user)
            if (len(user_temp_list) >= 2):
                data_list = load_partition_data(user_temp_list, session, select_statement)
                if data_list is not None:
                    print("写入" + str(len(data_list)) + "行记录")
                    writer.writerows(data_list)
                    user_temp_list.clear()

        if (len(user_temp_list) > 0):
            data_list = load_partition_data(user_temp_list, session, select_statement)
            if data_list is not None:
                print("最后写入" + str(len(data_list)) + "行记录")
                writer.writerows(data_list)

    session.shutdown()
    cluster.shutdown()

if __name__ == '__main__':
    """
    使用: python get_tags.py user_file out_file

    在user_file中给出要查找的用户，out_file里给出所查用户的用户标签数据

    user_file: 用户文件，一个用户ID一行，或多个用户ID一行，用户间用逗号分隔
    out_file: 用户标签数据文件

    """
    if (len(sys.argv) > 2):
        user_file = sys.argv[1]
        out_file = sys.argv[2]

        load_to_file(user_file, out_file)
    else:
        print("usage: python get_tags.py user_file out_file")
