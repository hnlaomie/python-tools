# -*- coding: utf-8 -*-
import sys, csv
from os.path import dirname, abspath
from jinja2 import Environment, FileSystemLoader

def load_csv(csv_file: str) -> []:
    '''
    将数据载入列表
    :param csv_file: csv文件
    :return: 数据列表
    '''
    data_list = []

    with open(csv_file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter=',')
        for row in reader:
            data_list.append(row)

    return data_list

def save_to_html(data_list: [], html_file: str):
    data = {"table": data_list}
    current_dir = dirname(abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(current_dir), trim_blocks=True)
    output = j2_env.get_template('template/table.tmpl').render(data)
    with open(html_file, "w") as writer:
        writer.write(output)

"""
将csv转换为html
"""
if __name__ == '__main__':
    if (len(sys.argv) > 2):
        csv_file = sys.argv[1]
        html_file = sys.argv[2]
        data_list = load_csv(csv_file)
        save_to_html(data_list, html_file)
    else:
        print("usage: python3 csv_to_html.py [csv_file] [html_file]")

