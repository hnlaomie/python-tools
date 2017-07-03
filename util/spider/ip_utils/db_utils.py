#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlite3 import connect, Connection

_clawer_db = '/home/laomie/projects/ip/crawler.db'

day_of_seconds = 60 * 60 * 24

def create_connection(db_file: str) -> Connection:
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = connect(db_file)
        return conn
    except Exception as e:
        print(e)

    return None


def exec_select(conn: Connection, sql: str, params: () = None) -> []:
    """
    根据sql查询数据并返回结果
    :param conn: 数据连接
    :param sql: 查询语句
    :param params: 查询参数
    :return: List([])
    """
    data_list = []
    cur = conn.cursor()
    if params is None:
        cur.execute(sql)
    else:
        cur.execute(sql, params)
    rows = cur.fetchall()

    for row in rows:
        data = []
        for value in row:
            data.append(value)
        data_list.append(data)

    return data_list


def blank_edu_ip(conn: Connection) -> []:
    """

    :param conn: 数据连接
    :return: List([proxy])
    """
    select_sql = '''
        SELECT begin_ip, end_ip
        FROM edu_ip_list
        WHERE end_ip_desc = '' OR begin_ip_desc = ''
        limit 100
    '''
    rows = exec_select(conn, select_sql)
    return rows


def update_begin_ip_desc(conn: Connection, row_list: []) -> []:
    """
    批量更新开始ip描述
    :param conn: 数据连接
    :row_list: 数据列表[(ip描述,ip)]
    :return:
    """
    update_sql = '''
        UPDATE OR IGNORE edu_ip_list
        SET begin_ip_desc = ?
        WHERE begin_ip = ?
    '''

    cur = conn.cursor()
    cur.executemany(update_sql, row_list)


def update_end_ip_desc(conn: Connection, row_list: []) -> []:
    """
    批量更新结束ip描述
    :param conn: 数据连接
    :row_list: 数据列表[(ip描述,ip)]
    :return:
    """
    update_sql = '''
        UPDATE OR IGNORE edu_ip_list
        SET end_ip_desc = ?
        WHERE end_ip = ?
    '''

    cur = conn.cursor()
    cur.executemany(update_sql, row_list)


def all_edu_ip(conn: Connection) -> []:
    """

    :param conn: 数据连接
    :return: List([proxy])
    """
    select_sql = '''
        SELECT a.begin_ip, a.end_ip, a.adv_region_code,
            b.province_brief_name, b.city_brief_name, 
            a.begin_ip_desc, a.end_ip_desc
        FROM edu_ip_list a
        LEFT JOIN mobile_adv_area b
        ON a.adv_region_code = b.region_code
    '''
    rows = exec_select(conn, select_sql)
    return rows


def all_adv_region(conn: Connection) -> []:
    """

    :param conn: 数据连接
    :return: List([proxy])
    """
    select_sql = '''
        SELECT region_code, region_name, father_region_name
        FROM mobile_adv_region
    '''
    rows = exec_select(conn, select_sql)
    return rows