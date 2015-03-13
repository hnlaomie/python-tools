# -*- coding: utf-8 -*-

import os, sys
from stat import S_ISDIR, S_ISREG

def walltree(path, oldName, newName, callback):
    for f in os.listdir(path):
        fullpath = os.path.join(path, f)
        mode = os.stat(fullpath).st_mode
        if S_ISDIR(mode):
            walltree(fullpath, oldName, newName, rename)
        elif S_ISREG(mode):
            callback(fullpath, oldName, newName)
        else:
            print(fullpath)

def rename(file, oldName, newName):
    path = os.path.dirname(file)
    fileName = os.path.basename(file)
    newName = fileName.replace(oldName, newName)
    if (fileName != newName):
        os.rename(file, os.path.join(path, newName))

"""
使用: python rename.py [path] oldName newName

遍历[path]下所有文件,如文件名中有"oldName",则替换为"newName".
"""
if __name__ == '__main__':
    if (len(sys.argv) > 3):
        path = sys.argv[1]
        oldName = sys.argv[2]
        newName = sys.argv[3]
        walltree(path, oldName, newName, rename)
    else:
        print("usage: python rename.py [path] oldName, newName")