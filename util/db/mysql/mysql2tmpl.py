# -*- coding: utf-8 -*-
from os.path import dirname, abspath
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from util.db.mysql.typeconverter import mysql_to_hive

class TableInfo(object):
    pass

class ColumnInfo(object):
    pass

def make_session(connection_string):
    engine = create_engine(connection_string, echo=False, convert_unicode=True)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def print_html_doc(data):
    current_dir = dirname(abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(current_dir), trim_blocks=True)
    output = j2_env.get_template('template/modeltable.tmpl').render(data)
    print(output)

"""
根据mysql表结构，通过jinja2模板，输出用户需要的内容
"""
if __name__ == '__main__':

    server = "mysql+mysqlconnector://root:root@localhost:3306/tjdev?charset=utf8"
    source, sengine = make_session(server)
    smeta = MetaData(bind=sengine)
    smeta.reflect(sengine)
    for table_name in smeta.tables.keys():
        tableInfo = TableInfo()
        tableInfo.name = table_name
        table = smeta.tables.get(table_name)

        columns = []
        for column in table.columns :
            columnInfo = ColumnInfo()
            columnInfo.name = column.name
            columnInfo.type = mysql_to_hive(column.type)
            columns.append(columnInfo)
        tableInfo.columns = columns

        data = {"table" : tableInfo}
        print_html_doc(data)
