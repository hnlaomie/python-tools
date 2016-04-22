# -*- coding: utf-8 -*-

import sys, csv, time
from datetime import datetime
from cassandra.cluster import Cluster, Session, ResultSet
from cassandra.concurrent import execute_concurrent

def load_user(user_file):
    """
    从用户文件载入用户ID
    :param user_file: 用户文件
    :return: 用户ID列表
    """
    user_list = []

    with open(user_file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter=',')

        for row in reader:
            user_id = row[0]
            user_list.append(user_id)

    return user_list


def data_to_list(result):
    """
    保存用户行为数据保存到列表
    :param writer: 用户行为数据
    :return: 用户行为列表
    """
    action_list = []

    for row in result:
        data_list = []
        for data in row:
            data_list.append(data)

        # 将unix time 转为年月日时分秒
        unix_time = data_list[1] / 1000
        log_time = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        data_list[1] = log_time

        action_list.append(data_list)

    return action_list


def get_connection():
    """
    获取数据库连接
    :return: 连接
    """
    cluster = Cluster(['192.168.1.20'])
    session = cluster.connect('dsp')
    return session


def load_to_file(user_file, action_file):
    """
    根据给定的用户，从cassandra数据库中读取用户行为数据到文件
    :param user_file: 用户文件
    :param action_file: 用户行为文件
    :return:
    """
    sql = "SELECT user_id, log_time, req_id, action_type, platform_id, adv_type_id, adv_id, app_id, city_id, "
    sql = sql + "sdk_id, req_ip, dev_id, network_id "
    sql = sql + "FROM dsp.user_action WHERE user_id = ?"

    session = get_connection()
    user_list = load_user(user_file)
    action_list = []

    with open(action_file, "w") as csv_output:
        writer = csv.writer(csv_output, delimiter=',', lineterminator='\n')

        select_statement = session.prepare(sql)

        statements_and_params = []
        for user_id in user_list:
            params = (user_id,)
            statements_and_params.append((select_statement, params))

        results = execute_concurrent(
            session, statements_and_params, raise_on_first_error = False)

        for (success, result) in results:
            if not success:
                print("查询出错.")  # result will be an Exception
            else:
                action_list.extend(data_to_list(result))
                if (len(action_list) >= 2000000):
                    writer.writerows(action_list)
                    action_list.clear()

        writer.writerows(action_list)


if __name__ == '__main__':
    """
    使用: python user_action.py user_file action_file

    在user_file中给出要查找的用户，action_file里给出所查用户的所有用户行为数据

    user_file: 用户文件，每个用户ID一行
    action_file: 用户行为数据文件

    """
    if (len(sys.argv) > 2):
        user_file = sys.argv[1]
        action_file = sys.argv[2]

        load_to_file(user_file, action_file)
    else:
        print("usage: python user_action.py user_file action_file")