#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlite3 import connect, Connection

_clawer_db = '/home/laomie/crawler.db'

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


def upsert_proxy(conn: Connection, proxy_list: []):
    """
    往代理列表中放代理，存在则修改更新时间，不存在则新插入
    :param conn: 数据连接
    :param proxy_list: 代理列表，格式为：[(proxy1),(proxy2),...(proxyn)]
    :return:
    """
    update_sql = ''' 
        UPDATE OR IGNORE proxy_list
        SET update_date = datetime('now', 'localtime')
        WHERE proxy = ?
    '''
    insert_sql = ''' 
        INSERT OR IGNORE INTO proxy_list (proxy, insert_date, update_date)
        VALUES (?, datetime('now', 'localtime'), datetime('now', 'localtime'))
    '''

    cur = conn.cursor()
    cur.executemany(update_sql, proxy_list)
    cur.executemany(insert_sql, proxy_list)


def all_proxy(conn: Connection) -> []:
    """
    从代理信息表中取出所有最近有效的代理，更新日为最近两天以内
    :param conn: 数据连接
    :return: List([proxy])
    """
    time_diff = day_of_seconds * 2
    select_sql = '''
        SELECT a.proxy
        FROM proxy_list a 
        LEFT JOIN disable_proxies b ON a.proxy = b.proxy
        WHERE CAST(strftime('%s', datetime('now', 'localtime')) - strftime('%s', a.update_date) as INTEGER) < ?
        AND a.error_count < 1
        AND b.proxy is NULL
    '''
    rows = exec_select(conn, select_sql, (time_diff,))
    return rows


def update_proxy_error(conn: Connection, proxy_list: []) -> []:
    """
    批量更新代理信息表中代理错误次数
    :param conn: 数据连接
    :proxy_list: 代理列表[(代理１), (代理１), ... , (代理n)]
    :return:
    """
    update_sql = '''
        UPDATE OR IGNORE proxy_list
        SET error_count = error_count + 1
        WHERE proxy = ?
    '''

    cur = conn.cursor()
    cur.executemany(update_sql, proxy_list)


def reload_activate_proxies(conn: Connection, data_list: []):
    """
    载入活跃代理，载入前先清空数据
    :param conn: 数据连接
    :param data_list: 代理列表，格式为：[(proxy1, response_time1),(proxy2, response_time2),...(proxyn, response_timen)]
    :return:
    """
    delete_sql = ''' 
        DELETE FROM activate_proxies
    '''
    insert_sql = ''' 
        INSERT INTO activate_proxies (proxy, response_time, insert_date)
        VALUES (?, ?, datetime('now', 'localtime'))
    '''

    cur = conn.cursor()
    cur.execute(delete_sql)
    cur.executemany(insert_sql, data_list)


def all_activate_proxies(conn: Connection) -> []:
    """
    从活跃代理中取出所有有效的活跃代理，排除已失效的代理
    :param conn: 数据连接
    :return: List([proxy])
    """
    select_sql = '''
        SELECT a.proxy from activate_proxies a
        LEFT JOIN disable_proxies b ON a.proxy = b.proxy
        WHERE b.proxy is NULL
        ORDER BY a.response_time DESC
    '''
    rows = exec_select(conn, select_sql)
    return rows


def insert_disable_proxy(conn: Connection, proxy: ()):
    """
    写入失效的代理
    :param conn: 数据连接
    :param proxy: (代理)
    :return:
    """
    insert_sql = '''
        INSERT OR IGNORE INTO disable_proxies (proxy, insert_date)
        VALUES (?, datetime('now', 'localtime'))
    '''
    cur = conn.cursor()
    cur.execute(insert_sql, proxy)


def refresh_disable_proxies(conn: Connection):
    """
    刷新失效的代理，失效一天以上就可删除
    :param conn: 数据连接
    :return:
    """
    delete_sql = ''' 
        DELETE FROM disable_proxies
        WHERE CAST(strftime('%s', datetime('now', 'localtime')) - strftime('%s', insert_date) as INTEGER) > ?
    '''
    cur = conn.cursor()
    cur.execute(delete_sql, (day_of_seconds,))


def update_tac_info(conn: Connection, tac_data: ()):
    """
    更新tac的品牌，机型和状态
    :param conn: 数据连接
    :param tac_data: (品牌，机型，状态，tac）
        状态：（0:正常）
    :return:
    """
    update_sql = '''
        UPDATE OR IGNORE tac_info
        SET brand = ? ,
        model = ? ,
        status = ? ,
        query_count = query_count + 1 ,
        update_date = datetime('now', 'localtime')
        WHERE tac_id = ?
    '''
    cur = conn.cursor()
    cur.execute(update_sql, tac_data)


def update_tac_status(conn: Connection, tac_data: ()):
    """
    更新tac的状态
    :param conn: 数据连接
    :param tac_data: (状态，tac）
        状态：（2:不存在，3:查询错）
    :return:
    """
    update_sql = '''
        UPDATE OR IGNORE tac_info
        SET status = ? ,
        query_count = query_count + 1 ,
        update_date = datetime('now', 'localtime')
        WHERE tac_id = ?
    '''
    cur = conn.cursor()
    cur.execute(update_sql, tac_data)


def load_imei(conn: Connection) -> []:
    """
    载入imei数据，根据用户数降序排，只取状态为初始化的数据
    :param conn: 数据连接
    :return: List([imei])
    """
    select_sql = '''
        SELECT imei
        FROM tac_info
        WHERE status = 1
        ORDER BY user_count DESC
        LIMIT 16
    '''
    rows = exec_select(conn, select_sql)
    return rows
