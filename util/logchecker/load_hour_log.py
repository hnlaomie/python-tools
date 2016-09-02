# -*- coding: utf-8 -*-
import sys

def load_data(log_file: str, out_file: str, log_date: str, log_hour: str) -> int :
    '''
    从日志文件载入指定时间的数据
    :param log_file: 日志文件
    :param out_file: 输出文件
    :param log_date: 年月日（%Y%m%d）
    :param log_hour: 小时
    :return: 写入的记录数
    '''
    hours = log_hour.split(",")
    outLines = 0

    with open(log_file, 'rb') as input, open(out_file, 'wb') as output:
        for line in input:
            if line != None and len(line) > 30 :
                # 取前四列，第一列exchange长度为1或2,第二列日志类型长度为1,第三列日期长度为8,第四列时长度为1或2
                data = line[:line.find(b',', 14)]
                lastIndex = data.find(b',', 10)
                date = data[lastIndex - 8 : lastIndex]
                hour = data[lastIndex + 1 :]
                if date.decode() == log_date and hour.decode() in hours :
                    output.write(line)
                    outLines = outLines + 1

    return outLines

if __name__ == '__main__':
    '''
    将日志文件中指定时间的数据输出到指定文件
    '''
    if (len(sys.argv) > 4):
        log_file = sys.argv[1]
        out_file = sys.argv[2]
        log_date = sys.argv[3]
        log_hour = sys.argv[4]
        try:
            rows = load_data(log_file, out_file, log_date, log_hour)
            print(rows)
        except:
            # 有异常打印异常
            print("error:", sys.exc_info()[0])
    else:
        print("usage: python3 load_hour_log.py [log_file] [out_file] [log_date] [log_hour]")