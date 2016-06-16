# -*- coding: utf-8 -*-

import os, sys, csv

def get_order_list(order_file: str) -> [] :
    order_list = []
    with open(order_file, "r") as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            order_list.append(row[0])

    return order_list

def save_report(data: [], order_id: str, out_path: str, report_file: str):
    order_file = report_file.replace("orderId", order_id)
    out_file = os.path.join(out_path, order_file)
    with open(out_file, "w") as csv_output:
        writer = csv.writer(csv_output, lineterminator='\n')
        writer.writerows(data)

def build_report(order_file: str, csv_file: str, out_path: str):
    # used order map
    used_order_map = {}
    # row data list
    row_list = []
    report_file = os.path.basename(csv_file)
    pre_order_id = None
    # header on first line
    is_header = True
    header = None

    with open(csv_file, "r") as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if (len(row) > 0):
                if is_header:
                    # save first line to header, first column is order_id
                    header = row[1:]
                    is_header = False
                else:
                    order_id = row[0]

                    if pre_order_id == None:
                        pre_order_id = order_id

                    # save data to file when line change to next order_id
                    if order_id != pre_order_id:
                        row_list.insert(0, header)
                        used_order_map[pre_order_id] = pre_order_id
                        save_report(row_list, pre_order_id, out_path, report_file)
                        row_list.clear()
                        pre_order_id = order_id

                    row_list.append(row[1:])

    if pre_order_id != None:
        row_list.insert(0, header)
        used_order_map[pre_order_id] = pre_order_id
        save_report(row_list, pre_order_id, out_path, report_file)

    # save empty report with header
    row_list.clear()
    row_list.append(header)
    order_list = get_order_list(order_file)
    for order_id in order_list:
        if (used_order_map.get(order_id) == None):
            save_report(row_list, order_id, out_path, report_file)

"""
usage: python build_report.py [order_file] [csv_file] [out_path]

read data from csv_file, group by order_id and output multipule reports to out_path.
if order without data, output empty report with header.

order_file: with multiple orderId
csv_file: first column is "orderId"
out_path: report's directory
"""
if __name__ == '__main__':
    if (len(sys.argv) > 3):
        order_file = sys.argv[1]
        csv_file = sys.argv[2]
        out_path = sys.argv[3]
        build_report(order_file, csv_file, out_path)
    else:
        print("usage: python build_report.py [order_file] [csv_file] [out_path]")