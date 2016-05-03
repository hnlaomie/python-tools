# -*- coding: utf-8 -*-

import os, sys, csv

def build_report(csv_file, out_path, report_file):
    rowList = []
    pre_order_id = None
    is_header = True
    header = None

    with open(csv_file, "r") as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if (len(row) > 0):
                if is_header:
                    header = row[1:]
                    is_header = False
                else:
                    order_id = row[0]

                    if pre_order_id == None:
                        pre_order_id = order_id

                    if order_id != pre_order_id:
                        rowList.insert(0, header)
                        data_to_report(rowList, pre_order_id, out_path, report_file)
                        rowList.clear()
                        pre_order_id = order_id

                    rowList.append(row[1:])

    if pre_order_id != None:
        rowList.insert(0, header)
        data_to_report(rowList, pre_order_id, out_path, report_file)

def data_to_report(data, order_id, out_path, report_file):
    order_file = report_file.replace("orderId", order_id)
    out_file = os.path.join(out_path, order_file)
    with open(out_file, "w") as csv_output:
        writer = csv.writer(csv_output, lineterminator='\n')
        writer.writerows(data)

"""
usage: python build_report.py [csv_file] [out_path] [report_file]

read data from csv_file, group by order_id and output multipule reports to out_path.

csv_file: first column is "orderId"
out_path: report's directory
report_file: report file name
"""
if __name__ == '__main__':
    if (len(sys.argv) > 3):
        csv_file = sys.argv[1]
        out_path = sys.argv[2]
        report_file = sys.argv[3]
        build_report(csv_file, out_path, report_file)
    else:
        print("usage: python build_report.py [csv_file] [out_path] [report_file]")