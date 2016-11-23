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
    data_list = []

    statements_and_params = []
    for user_id in user_list:
        params = (user_id,)
        statements_and_params.append((select_statement, params))

    results = execute_concurrent(
        session, statements_and_params, raise_on_first_error=False)

    for (success, result) in results:
        if not success:
            print("查询报错")
        else:
            print(result[0])

def load_data(user_list: []) -> []:
    '''
    连接cassandra查询数据
    :param user_list: 用户列表
    :return: 用户标签
    '''
    data_list = []

    sql = "SELECT user_id, tag_id FROM user_tags"
    sql = sql + " WHERE user_id=%s"

    cluster = Cluster(['192.168.1.20'])
    session = cluster.connect('dmp')
    futures = []

    for user_id in user_list:
        futures.append(session.execute_async(sql, (user_id,)))

    # wait for them to complete and use the results
    for future in futures:
        rows = future.result()
        for row in rows:
            data_list.append([row.user_id, str(row.tag_id)])

    session.shutdown()
    cluster.shutdown()

    return data_list

def load_to_file(user_file, out_file):
    """
    根据给定的用户，从cassandra数据库中读取用户标签数据到文件
    :param user_file: 用户文件
    :param out_file: 用户标签文件
    :return:
    """
    row_count = 0
    user_list = load_user(user_file)

    with open(out_file, "w") as csv_output:
        writer = csv.writer(csv_output, delimiter=',', lineterminator='\n')
        data_list = load_data(user_list)
        if data_list is not None:
            print("写入" + str(len(data_list)) + "行记录")
            writer.writerows(data_list)

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
