#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def user_count(logfile):
    users = {}
    hasUser = False

    with open(logfile, "r") as input:
        for line in input:
            if (hasUser == True):
                data = line.split('|')
                user = data[1]
                count = users.get(user)
                if (count == None):
                    count = 0
                users[user] = count + 1
                hasUser = False

            if line.startswith("---") and line.endswith("---\n"):
                hasUser = True

    print("总提交者:" + str(len(users)))
    for key in users.keys():
        print(key + ":" + str(users.get(key)))

"""
使用: python [logfile]

根据svn日志统计有多少提交者
"""
if __name__ == '__main__':
    if (len(sys.argv) > 1):
        logfile = sys.argv[1]
        user_count(logfile)
    else:
        print("usage: python usercount.py [logfile]")