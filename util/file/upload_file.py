# -*- coding: utf-8 -*-

import os, sys, paramiko

def get_csv_files(path: str) -> [] :
    """
    get csv files from directory
    :param path: file path
    :return: csv files list
    """
    files = []
    for f in os.listdir(path):
        if (f.endswith(".csv")):
            files.append(f)

    return files

def upload_files(local_path: str, remote_path: str):
    """
    upload csv file from local to remote via sftp.
    :param local_path: local path
    :param remote_path: remote path
    :return:
    """

    sftp_server = "192.168.11.1"
    sftp_port = 22
    sftp_user = "abc"
    sftp_password = "abc"

    server = paramiko.Transport((sftp_server, sftp_port))
    server.connect(username=sftp_user, password=sftp_password)
    sftp = paramiko.SFTPClient.from_transport(server)

    csv_files = get_csv_files(local_path)
    for f in csv_files:
        local_file = os.path.join(local_path, f)
        remote_file = os.path.join(remote_path, f)
        print("upload file:" + local_file)
        sftp.put(local_file, remote_file)

    sftp.close()
    server.close()


"""
usage: python upload.py [local_path] [remote_path]

upload files from local path to remote path via sftp.

local_path: local path
remote_path: sftp server path
"""
if __name__ == '__main__':
    if (len(sys.argv) > 2):
        local_path = sys.argv[1]
        remote_path = sys.argv[2]
        upload_files(local_path, remote_path)
    else:
        print("usage: python upload.py [local_path] [remote_path]")
