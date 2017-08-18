# -*- coding: utf-8 -*-

import sys

def intersection(ip_list1: [], ip_list2: []) -> []:

    result_list = []
    ip_data1 = []
    ip_data2 = []
    is_pop1 = True
    is_pop2 = True

    while (len(ip_list1) > 0) or (len(ip_list2) > 0):
        # 首次ip出栈
        if (is_pop1 and len(ip_list1) > 0):
            ip_data1 = ip_list1.pop()
            is_pop1 = False
        if (is_pop2 and len(ip_list2) > 0):
            ip_data2 = ip_list2.pop()
            is_pop2 = False

        if (len(ip_data1) > 1 and len(ip_data2) > 1):
            begin_ip1 = ip_data1[0]
            end_ip1 = ip_data1[1]
            begin_ip2 = ip_data2[0]
            end_ip2 = ip_data2[1]

            # end_ip1小，计算交集
            if end_ip1 < end_ip2:
                is_pop1 = True
                # 有交集
                if end_ip1 >= begin_ip2:
                    # 交集为[begin_ip2, end_ip1]
                    if begin_ip1 < begin_ip2:
                        result_list.append([begin_ip2, end_ip1])
                    # 交集为[begin_ip1, end_ip1]
                    else:
                        result_list.append([begin_ip1, end_ip1])
            else:
                is_pop2 = True
                # 无交集
                if end_ip2 >= begin_ip1:
                    # 交集为[begin_ip1, end_ip2]
                    if begin_ip2 < begin_ip1:
                        result_list.append([begin_ip1, end_ip2])
                    # 交集为[begin_ip2, end_ip2]
                    else:
                        result_list.append([begin_ip2, end_ip2])
        else:
            if (len(ip_data1) < 2):
                is_pop1 = True
            if (len(ip_data2) < 2):
                is_pop2 = True

        # 一个列表空了，另一个得出栈
        if (len(ip_list1) == 0):
            is_pop2 = True
        if (len(ip_list2) == 0):
            is_pop1 = True

    return result_list


if __name__ == '__main__':
    ip_list1 = [[31, 40], [20, 30], [1, 2]]
    ip_list2 = [[40, 50], [29, 39]]
    data = intersection(ip_list1, ip_list2)
    print(data)