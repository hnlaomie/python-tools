#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, csv, time
from datetime import datetime
from cassandra.cluster import Cluster, Session, ResultSet
from cassandra.concurrent import execute_concurrent


def load_tag(tag_file: str) -> []:
    """
    从标签文件载入标签ID
    :param tag_file: 标签文件
    :return: 标签ID列表
    """
    tag_list = []

    with open(tag_file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter=',')

        for row in reader:
            if row is not None and len(row) > 0:
                for tag_id in row:
                    tag_list.append(tag_id)

    return tag_list


def load_to_file(tag_file, out_file):
    """
    根据给定的标签，从cassandra数据库中读取标签用户数据到文件
    :param tag_file: 标签文件
    :param out_file: 标签用户文件
    :return:
    """
    row_count = 0
    data_list = []
    tag_list = load_tag(tag_file)

    sql = "SELECT source_id, tag_id, user_id FROM tag_users"
    sql = sql + " WHERE source_id in (1, 2) and tag_id=%s"

    cluster = Cluster(['192.168.11.52'])
    session = cluster.connect('dmp')
    futures = []

    with open(out_file, "w") as csv_output:
        writer = csv.writer(csv_output, delimiter=',', lineterminator='\n')

        for tag_id in tag_list:
            futures.append(session.execute_async(sql, (int(tag_id),)))

        # wait for them to complete and use the results
        for future in futures:
            rows = future.result()
            for row in rows:
                row_count = row_count + 1
                data_list.append([str(row.source_id), str(row.tag_id), row.user_id])
                if (len(data_list) >= 1000000):
                    print("标签用户文件写入" + str(row_count) + "行数据。")
                    writer.writerows(data_list)
                    data_list.clear()

        if len(data_list) > 0:
            writer.writerows(data_list)

    session.shutdown()
    cluster.shutdown()


if __name__ == '__main__':
    """
    使用: python get_users.py tag_file out_file

    在tag_file中给出要查找的标签，out_file里给出所查标签的标签用户数据

    tag_file: 标签文件，一个标签ID一行，或多个标签ID一行，标签间用逗号分隔
    out_file: 标签用户数据文件

    """
    if (len(sys.argv) > 2):
        tag_file = sys.argv[1]
        out_file = sys.argv[2]

        load_to_file(tag_file, out_file)
    else:
        print("usage: python get_users.py tag_file out_file")
