# -*- coding: utf-8 -*-

import sys, psycopg2, smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from os.path import dirname, abspath
from jinja2 import Environment, FileSystemLoader

# ＤＢ配置
db_name = "adwo"
host = "172.17.0.2"
password = "bidev"
dsp_user = "dw_dsp"
yg_user = "dw_yingguang"

# 邮件设置
sender = 'lichunhui@adwo.com'
#receivers = ['lichunhui@adwo.com', 'tj-guowei@adwo.com', 'wangtienan@adwo.com', 'wangying1@adwo.com', 'duguiling@adwo.com']
receivers = ['lichunhui@adwo.com']

class DSPData(object):
    pass

class DSPRow(object):
    pass

class YGData(object):
    pass

class YGRow(object):
    pass

def load_data(user: str, sql: str) -> [] :
    """
    从数据库载入数据
    :param user: 数据库用户
    :param sql: 查询sql
    :return: 行数据列表
    """
    row_data = []
    try:
        conn_str = "dbname='" + db_name + "' user='" + user + "' host='" + host + "' password='" + password + "'"
        connection = psycopg2.connect(conn_str)
        cursor = connection.cursor()

        cursor.execute(sql)
        row_data = cursor.fetchall()

        cursor.close()
        connection.close()
    except:
        print("载入数据错误：" + sql)

    return row_data


def load_dsp_data(date: str) -> [] :
    """
    载入dsp验证数据
    :param date: 日期(%Y%m%d)
    :return: ２４小时数据列表
    """

    row_data = []

    sql =  "select "
    sql += "    hour, bid_hive, win_hive, show_hive, click_hive, "
    sql += "    bid_pgsql, win_pgsql, show_pgsql, click_pgsql "
    sql += "from dsp_hour_count "
    sql += "where date_id = " + date + " "
    sql += "order by hour"

    rows = load_data(dsp_user, sql)

    for row in rows:
        dspRow = DSPRow()
        dspRow.hour = row[0]
        dspRow.bid_hive = row[1]
        dspRow.win_hive = row[2]
        dspRow.show_hive = row[3]
        dspRow.click_hive = row[4]
        dspRow.bid_pgsql = row[5]
        dspRow.win_pgsql = row[6]
        dspRow.show_pgsql = row[7]
        dspRow.click_pgsql = row[8]

        row_data.append(dspRow)

    return row_data


def load_yg_data(date: str) -> [] :
    """
    载入硬广验证数据
    :param date: 日期(%Y%m%d)
    :return: ２４小时数据列表
    """

    row_data = []

    sql =  "select "
    sql += "    hour, request_hive, show_hive, click_hive, "
    sql += "    request_pgsql, show_pgsql, click_pgsql "
    sql += "from yg_hour_count "
    sql += "where date_id = " + date + " "
    sql += "order by hour"

    rows = load_data(yg_user, sql)

    for row in rows:
        ygRow = YGRow()
        ygRow.hour = row[0]
        ygRow.request_hive = row[1]
        ygRow.show_hive = row[2]
        ygRow.click_hive = row[3]
        ygRow.request_pgsql = row[4]
        ygRow.show_pgsql = row[5]
        ygRow.click_pgsql = row[6]

        row_data.append(ygRow)

    return row_data


def build_mail_body(date: str, mail_file: str) -> str :
    """
    生成邮件主体内容
    :param date: 日期(%Y%m%d)
    :param mail_file: 保存附件文件
    :return: 邮件主体内容
    """

    # 从数据库载入验证结果数据
    dsp_data = DSPData()
    dsp_rows = load_dsp_data(date)
    dsp_data.rows = dsp_rows
    dsp_data.date = date[:4] + "-" + date[4:6] + "-" + date[6:8]

    yg_data = YGData()
    yg_rows = load_yg_data(date)
    yg_data.rows = yg_rows

    # 根据模板生成邮件内容
    data = {"dsp_data" : dsp_data, "yg_data" : yg_data}
    current_dir = dirname(abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(current_dir), trim_blocks=True)
    mail_body = j2_env.get_template("template/mail_body.tmpl").render(data)
    with open(mail_file, "w") as writer:
        writer.write(mail_body)

    return mail_body

def send_report(mail_subject: str, mail_body: str):
    """
    发送邮件
    :param mail_subject: 标题
    :param mail_body: 内容
    :return:
    """
    # 创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = Header("check_data")
    message['To'] = Header("check_data")
    message['Subject'] = Header(mail_subject, 'utf-8')

    # 邮件正文内容
    message.attach(MIMEText(mail_body, 'html', 'utf-8'))

    # 构造附件，传送文件
    # att = MIMEText(open(att_path, 'rb').read(), 'base64', 'utf-8')
    # att["Content-Type"] = 'application/octet-stream;charset=utf-8'
    # att["Content-Disposition"] = 'attachment; filename='+att_name
    # message.attach(att)

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("邮件发送失败!")


def check(date: str, mail_file: str):
    mail_body = build_mail_body(date, mail_file)
    subject = "平台数据验证" + "_" + date[:4] + "-" + date[4:6] + "-" + date[6:8]
    #send_report(subject, mail_body)

if __name__ == '__main__':

    if (len(sys.argv) > 2):
        date = sys.argv[1]
        mail_file = sys.argv[2]
        check(date, mail_file)
    else:
        print("usage: python check_data.py [date] [mail_file]")
